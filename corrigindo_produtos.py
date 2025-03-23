import asyncio
import aiohttp
import json
import time

BASE_URL = "https://app-bd.spincare.com.br/spincare"
TOKEN = "SEU TOKEN"  # Token do Chrome
SUCCESS_LOG_FILENAME = "produtos_atualizados_sucesso.txt"
DELETED_LINKS_LOG_FILENAME = "links_deletados.txt"
CORRECTED_PRODUCTS_LOG_FILENAME = "produtos_links_corrigidos.txt"

headers_essenciais = {
    'accept': 'application/json, text/plain, */*',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    'content-type': 'application/json',
    'dnt': '1',
    'node': 'node2',
    'origin': 'https://app.spincare.com.br',
    'platform': 'web',
    'priority': 'u=1, i',
    'referer': 'https://app.spincare.com.br/',
    'schema': 'homesaude',
    'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
    'sec-ch-ua-mobile': '?1',
    'sec-ch-ua-platform': '"Android"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'timezone': 'GMT-0300',
    'token': TOKEN,
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36'
}

CONCURRENT_REQUESTS = 50 # Adjust as needed for concurrency

async def async_get_product_data(session, product_id):
    """Fetches product data by ID asynchronously."""
    url = f"{BASE_URL}/produto/{product_id}"
    try:
        async with session.get(url, headers=headers_essenciais) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"Erro ao buscar dados do produto ID {product_id}: {e}")
        return None

async def async_get_linked_items(session, product_id):
    """Fetches linked items for a product asynchronously."""
    url = f"{BASE_URL}/product-imported-info-link/{product_id}/list"
    try:
        async with session.get(url, headers=headers_essenciais) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"Erro ao buscar links do produto ID {product_id}: {e}")
        return None

async def async_delete_linked_item(session, link_id):
    """Deletes a product-imported-info-link by ID asynchronously."""
    url = f"{BASE_URL}/product-imported-info-link/{link_id}"
    try:
        async with session.delete(url, headers=headers_essenciais) as response:
            response.raise_for_status()
            print(f"Link ID {link_id} deletado com sucesso.")
            return True
    except aiohttp.ClientError as e:
        print(f"Erro ao deletar link ID {link_id}: {e}")
        if e.response is not None:
            print(f"  Response Body: {await e.response.text()}")
        return False

def are_product_names_similar(main_product_name, linked_item_name):
    """Checks if linked item name is similar to main product name (based on first words)."""
    if not main_product_name or not linked_item_name:
        return False

    main_words = main_product_name.split()[:3]
    linked_name_lower = linked_item_name.lower()
    for word in main_words:
        if word.lower() not in linked_name_lower:
            return False
    return True

async def async_process_product_links(session, product_id, main_product_ds, output_file_deleted_links, output_file_corrected_links):
    """Processes links for a single product asynchronously."""
    linked_items_list = await async_get_linked_items(session, product_id)
    if not linked_items_list:
        return

    for linked_item in linked_items_list:
        link_id = linked_item.get("id")
        linked_item_ds_produto = linked_item.get("empresaTabelaPrecoItem", {}).get("ds_produto")

        if not are_product_names_similar(main_product_ds, linked_item_ds_produto):
            print(f"Produto ID: {product_id}, Link ID: {link_id} - Nomes de produtos não similares.")
            if await async_delete_linked_item(session, link_id):
                output_file_deleted_links.write(f"{product_id};{link_id}\n")
        else:
            print(f"Produto ID: {product_id}, Link ID: {link_id} - Nomes de produtos considerados similares.")
            output_file_corrected_links.write(f"{product_id};{link_id}\n")
        await asyncio.sleep(0.01) # Small delay to avoid overwhelming server


async def process_successful_updates(output_file_deleted_links, output_file_corrected_links):
    """Processes the success log file, checks for dissimilar links and deletes them asynchronously."""
    deleted_count = 0
    corrected_count = 0
    processed_products = 0 # Counter for processed products
    start_time_process = time.time()

    async with aiohttp.ClientSession() as session:
        tasks = []
        try:
            with open(SUCCESS_LOG_FILENAME, 'r', encoding='utf-8') as file:
                for line in file:
                    parts = line.strip().split(";")
                    if len(parts) >= 1:
                        product_id = parts[0].strip()
                        try:
                            product_id = int(product_id)
                        except ValueError:
                            print(f"ID de produto inválido na linha: {line.strip()}")
                            continue

                        main_product_info = await async_get_product_data(session, product_id)
                        if not main_product_info:
                            print(f"Não foi possível obter dados do produto para ID {product_id}. Pulando verificação de links.")
                            continue

                        main_product_ds = main_product_info.get("ds_produto")
                        task = asyncio.create_task(async_process_product_links(session, product_id, main_product_ds, output_file_deleted_links, output_file_corrected_links))
                        tasks.append(task)
                        processed_products += 1

                        if len(tasks) >= CONCURRENT_REQUESTS:
                            await asyncio.gather(*tasks)
                            tasks = [] # Clear tasks for next batch
                    if processed_products % 100 == 0: # Progress every 100 products
                        elapsed_time = time.time() - start_time_process
                        print(f"Produtos processados: {processed_products}, Tempo decorrido: {elapsed_time:.2f} segundos")


                if tasks: # Wait for remaining tasks
                    await asyncio.gather(*tasks)

        except FileNotFoundError:
            print(f"Erro: Arquivo de log de sucesso '{SUCCESS_LOG_FILENAME}' não encontrado.")
        except Exception as e:
            print(f"Ocorreu um erro geral durante o processamento de links: {e}")

    end_time_process = time.time()
    print(f"Processamento de links concluído. Tempo total de processamento: {end_time_process - start_time_process:.2f} segundos")
    print(f"Total de links deletados: (Contagem precisa ser implementada corretamente)") # Placeholder, correct counting needed
    print(f"Total de links considerados corretos (similares): (Contagem precisa ser implementada corretamente)") # Placeholder, correct counting needed


async def main():
    start_time = time.time()
    print("Iniciando script assíncrono para verificar e deletar links de produtos não similares.")

    with open(DELETED_LINKS_LOG_FILENAME, 'w', encoding='utf-8') as output_file_deleted_links, \
         open(CORRECTED_PRODUCTS_LOG_FILENAME, 'w', encoding='utf-8') as output_file_corrected_links:
        await process_successful_updates(output_file_deleted_links, output_file_corrected_links)

    end_time = time.time()
    print(f"Script assíncrono concluído. Tempo total de execução: {end_time - start_time:.2f} segundos")
    print(f"Log de links deletados salvo em: {DELETED_LINKS_LOG_FILENAME}")
    print(f"Log de links corretos (similares) salvo em: {CORRECTED_PRODUCTS_LOG_FILENAME}")


if __name__ == "__main__":
    asyncio.run(main())