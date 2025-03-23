import asyncio
import aiohttp
import json
import time

BASE_URL = "https://app-bd.spincare.com.br/spincare"
TOKEN = "SEU TOKEN"  # Token do Chrome
SUCCESS_LOG_FILENAME = "produtos_revinculados_brasindice_async.txt" # Log file for successful re-links - **MODIFIED Filename**
DELETED_LINKS_FILE_PATH = "links_deletados.txt" # File to read Product IDs from - **NEW**
CONCURRENT_REQUESTS = 50  # Adjust as needed

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
    'token': TOKEN,  # Usando 'token' header que funcionou
    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Mobile Safari/537.36'
}

async def async_get_product_data(session, product_id):
    """Fetches product data by ID asynchronously to get TISS code."""
    url = f"{BASE_URL}/produto/{product_id}"
    try:
        async with session.get(url, headers=headers_essenciais) as response:
            response.raise_for_status()
            return await response.json()
    except aiohttp.ClientError as e:
        print(f"Erro aiohttp ao buscar dados do produto ID {product_id} para obter TISS Code: {e}")
        return None

async def async_find_company_price_item_id(session, tiss_code):
    """Finds company_price_item_id by TISS code in brasindice asynchronously."""
    url_item_finder = f"{BASE_URL}/empresa-tabela-preco/item-finder"
    payload = {
        "item_type": "Medicamento",
        "item_ds": None,
        "manufacturer_nm": None,
        "measure_unit": None,
        "tiss_code": tiss_code,
        "tuss_code": None,
        "type": "brasindice"
    }

    try:
        async with session.post(url_item_finder, headers=headers_essenciais, json=payload) as response:
            response.raise_for_status()
            return await response.json()  # Retorna a resposta JSON se a requisição for bem-sucedida

    except aiohttp.ClientError as errh:
        print(f"Erro aiohttp ao buscar company_price_item_id para TISS Code {tiss_code}: {errh}")
        if errh.response is not None:
            print(f"  Response Body: {await errh.response.text()}")
        return None
    except json.JSONDecodeError as e:
        if response:
            response_text = await response.text()
        else:
            response_text = "No response received"
        print(f"Erro JSON decode ao buscar company_price_item_id para TISS Code {tiss_code}: {e} - Response Text: {response_text}")
        return None
    except Exception as err:
        print(f"Erro ao buscar company_price_item_id para TISS Code {tiss_code}: {err}")
        return None

async def async_update_product_info(session, product_id, company_price_item_id, output_file_success, detail_info="Revinculado via script"):
    url_update_product = f"{BASE_URL}/product-imported-info-link"
    payload_update = {
        "id": None,
        "product_id": product_id,
        "detail_info": detail_info,
        "company_price_item_id": company_price_item_id,
        "conversion": 1,
        "type": "brasindice"
    }

    print(f"Payload para revinculação do Produto ID {product_id}: {json.dumps(payload_update)}") # Imprimindo o payload

    try:
        async with session.post(url_update_product, headers=headers_essenciais, json=payload_update) as response:
            response.raise_for_status()
            print(f"Produto ID: {product_id} revinculado com company_price_item_id: {company_price_item_id} (brasindice) com sucesso.")
            output_file_success.write(f"{product_id};{company_price_item_id};brasindice\n")  # Log de sucesso

    except aiohttp.ClientResponseError as errh: # Captura ClientResponseError diretamente
        print(
            f"Erro aiohttp HTTP {errh.status} ao revincular Produto ID {product_id} com tipo brasindice: {errh.message}, URL: {errh.request_info.url}"
        ) # Imprime status e mensagem de errh
        try:
            response_text = await errh.text() # Tenta obter o corpo da resposta
            print(f"  Response Body: {response_text}")
        except:
            print("  Não foi possível obter o corpo da resposta.") # Caso não consiga ler o body
    except json.JSONDecodeError as e:
        if response:
            response_text = await response.text()
        else:
            response_text = "No response received"
        print(f"Erro JSON decode ao revincular Produto ID {product_id}: {e} - Response Text: {response_text}")
    except Exception as err:
        print(f"Erro ao revincular Produto ID {product_id}: {err}")

async def async_process_product(session, product_id, output_file_success): # Adicionado output_file_success
    """Processes re-linking for a single product asynchronously."""
    product_data = await async_get_product_data(session, product_id)
    if not product_data:
        return

    tiss_code = product_data.get('ds_codigo_tiss')
    if not tiss_code:
        print(f"Aviso: Codigo TISS não encontrado para Produto ID {product_id}. Não é possível revincular.")
        return

    print(f"Revinculando Produto ID: {product_id}, TISS Code: {tiss_code} (brasindice)")

    brasindice_items = await async_find_company_price_item_id(session, tiss_code)
    best_brasindice_item_id, max_pmc_brasindice = find_best_item_id(brasindice_items)

    if best_brasindice_item_id:
        await async_update_product_info(session, product_id, best_brasindice_item_id, output_file_success)
    else:
        print(f"Nenhum company_price_item_id 'brasindice' encontrado para TISS Code: {tiss_code} e Produto ID: {product_id}. Não revinculado.")

    print("-----------------------")

def find_best_item_id(items):
    best_item_id = None
    max_pmc = -1
    if items and isinstance(items, list):
        for item in items:
            pmc = item.get('vl_pmc')
            if isinstance(pmc, (int, float)) and pmc > max_pmc:
                max_pmc = pmc
                best_item_id = item.get('id')
    return best_item_id, max_pmc


async def process_products_from_file(file_path, output_file_success): # Adicionado output_file_success
    """Processa produtos do arquivo de IDs deletados e tenta revincular de forma assíncrona."""
    product_ids_to_relink = []
    try:
        with open(file_path, 'r', encoding='utf-8') as ids_file:
            for line in ids_file:
                parts = line.strip().split(";")
                if parts:
                    product_id_str = parts[0].strip()
                    try:
                        product_id = int(product_id_str)
                        product_ids_to_relink.append(product_id)
                    except ValueError:
                        print(f"Linha ignorada, ID inválido: {line.strip()}")
    except FileNotFoundError:
        print(f"Erro: Arquivo de IDs deletados '{file_path}' não encontrado.")
        return

    tasks = []
    async with aiohttp.ClientSession() as session:
        for product_id in product_ids_to_relink:
            task = asyncio.create_task(async_process_product(session, product_id, output_file_success))
            tasks.append(task)
            if len(tasks) >= CONCURRENT_REQUESTS:
                await asyncio.gather(*tasks)
                tasks = []
        if tasks:
            await asyncio.gather(*tasks)


async def main():
    start_time = time.time()
    print(f"Iniciando script assíncrono para revincular produtos (brasindice) do arquivo: {DELETED_LINKS_FILE_PATH}")

    with open(SUCCESS_LOG_FILENAME, 'w', encoding='utf-8') as output_file_success: # Abre arquivo de log de sucesso
        await process_products_from_file(DELETED_LINKS_FILE_PATH, output_file_success) # Passa o caminho do arquivo e o arquivo de log

    end_time = time.time()
    print(f"Script assíncrono de revinculação concluído. Tempo total de execução: {end_time - start_time:.2f} segundos")
    print(f"Log de produtos revinculados salvo em: {SUCCESS_LOG_FILENAME}")


if __name__ == "__main__":
    asyncio.run(main())