import requests  # Import requests is still needed for initial GET to fetch tiss_code if needed from ids_faltantes.txt - if you are using ids_faltantes approach
import json
import asyncio
import aiohttp
import time

BASE_URL = "https://app-bd.spincare.com.br/spincare"
TOKEN = "SEU TOKEN"  # Token do Chrome

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

SUCCESS_LOG_FILENAME = "produtos_atualizados_sucesso.txt"
CONCURRENT_REQUESTS = 50 # Adjust as needed

async def async_find_company_price_item_id(session, tiss_code, item_type):
    url_item_finder = f"{BASE_URL}/empresa-tabela-preco/item-finder"
    payload = {
        "item_type": "Medicamento",
        "item_ds": None,
        "manufacturer_nm": None,
        "measure_unit": None,
        "tiss_code": tiss_code,
        "tuss_code": None,
        "type": item_type
    }

    try:
        async with session.post(url_item_finder, headers=headers_essenciais, json=payload) as response:
            response.raise_for_status()
            return await response.json()

    except aiohttp.ClientError as errh:
        print(f"Erro aiohttp ao buscar company_price_item_id para TISS Code {tiss_code} e tipo {item_type}: {errh}")
        if errh.response is not None:
            print(f"  Response Body: {await errh.response.text()}")
        return None
    except json.JSONDecodeError as e:
        if response:
            response_text = await response.text()
        else:
            response_text = "No response received"
        print(f"Erro JSON decode ao buscar company_price_item_id para TISS Code {tiss_code} e tipo {item_type}: {e} - Response Text: {response_text}")
        return None
    except Exception as err:
        print(f"Erro ao buscar company_price_item_id para TISS Code {tiss_code} e tipo {item_type}: {err}")
        return None


async def async_update_product_info(session, product_id, company_price_item_id, item_type, output_file_success, detail_info="Descrição: [DESCRICAO] Código TISS: [COD_TISS]"):
    url_update_product = f"{BASE_URL}/product-imported-info-link"
    payload_update = {
        "id": None,
        "product_id": product_id,
        "detail_info": detail_info,
        "company_price_item_id": company_price_item_id,
        "conversion": 1,
        "type": item_type
    }

    try:
        async with session.post(url_update_product, headers=headers_essenciais, json=payload_update) as response:
            response.raise_for_status()
            print(f"Produto ID: {product_id} atualizado com company_price_item_id: {company_price_item_id} e tipo: {item_type} com sucesso.")
            output_file_success.write(f"{product_id};{company_price_item_id};{item_type}\n") # Log de sucesso

    except aiohttp.ClientResponseError as errh:
        print(f"Erro aiohttp HTTP {errh.status} ao atualizar Produto ID {product_id} com tipo {item_type}: {errh.message}, URL: {errh.request_info.url}")
        try:
            response_text = await errh.text()
            print(f"  Response Body: {response_text}")
        except:
            print("  Could not retrieve response body.")
    except json.JSONDecodeError as e:
        if response:
            response_text = await response.text()
        else:
            response_text = "No response received"
        print(f"Erro JSON decode ao atualizar Produto ID {product_id} com tipo {item_type}: {e} - Response Text: {response_text}")
    except Exception as err:
        print(f"Erro ao atualizar Produto ID {product_id} com tipo {item_type}: {err}")


async def async_process_product(session, product_id, tiss_code, output_file_success): # Adicionado output_file_success
    print(f"Processando Produto ID: {product_id}, TISS Code: {tiss_code}")

    # Busca itens em ambos 'brasindice' e 'simpro' de forma assíncrona
    brasindice_items_coro = async_find_company_price_item_id(session, tiss_code, "brasindice")
    simpro_items_coro = async_find_company_price_item_id(session, tiss_code, "simpro")

    brasindice_items, simpro_items = await asyncio.gather(brasindice_items_coro, simpro_items_coro)

    best_brasindice_item_id, max_pmc_brasindice = find_best_item_id(brasindice_items)
    best_simpro_item_id, max_pmc_simpro = find_best_item_id(simpro_items)

    # Atualiza com o melhor item 'brasindice', se encontrado
    if best_brasindice_item_id:
        print(f"  Item 'brasindice' encontrado para TISS Code: {tiss_code}")
        await async_update_product_info(session, product_id, best_brasindice_item_id, "brasindice", output_file_success) # Passando output_file_success
    else:
        print(f"  Nenhum item 'brasindice' encontrado para TISS Code: {tiss_code}")

    # Atualiza com o melhor item 'simpro', se encontrado
    if best_simpro_item_id:
        print(f"  Item 'simpro' encontrado para TISS Code: {tiss_code}")
        await async_update_product_info(session, product_id, best_simpro_item_id, "simpro", output_file_success) # Passando output_file_success
    else:
        print(f"  Nenhum item 'simpro' encontrado para TISS Code: {tiss_code}")

    if not best_brasindice_item_id and not best_simpro_item_id:
        print(f"  company_price_item_id não encontrado para TISS Code: {tiss_code} em ambos 'brasindice' e 'simpro' para Produto ID: {product_id}")

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
    tasks = []
    async with aiohttp.ClientSession() as session:
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    parts = line.strip().split(";")
                    if len(parts) == 2:
                        product_id = parts[0].strip()
                        tiss_code = parts[1].strip()

                        if not tiss_code:  # Check if tiss_code is empty
                            print(f"Produto ID: {product_id} ignorado devido a TISS Code vazio.")
                            continue # Skip to the next product

                        task = asyncio.create_task(async_process_product(session, product_id, tiss_code, output_file_success)) # Passando output_file_success para a task
                        tasks.append(task)
                    else:
                        print(f"Linha ignorada devido a formato inválido: {line.strip()}")
                    if len(tasks) >= CONCURRENT_REQUESTS: # Limitando requisições concorrentes
                        await asyncio.gather(*tasks) # Espera tasks atuais completarem
                        tasks = [] # Limpa a lista de tasks
            if tasks: # Aguarda tasks restantes
                await asyncio.gather(*tasks)
        except FileNotFoundError:
            print(f"Erro: Arquivo '{file_path}' não encontrado.")
        except Exception as e:
            print(f"Ocorreu um erro geral: {e}")


async def main():
    file_path = "produtos.txt"  # Nome do seu arquivo .txt

    start_time = time.time()
    print(f"Iniciando processamento assíncrono dos produtos do arquivo: {file_path}")

    with open(SUCCESS_LOG_FILENAME, 'w', encoding='utf-8') as output_file_success: # Abre arquivo de log de sucesso
        await process_products_from_file(file_path, output_file_success) # Passa arquivo de log para a função

    end_time = time.time()
    print(f"Processamento assíncrono concluído. Tempo total de execução: {end_time - start_time:.2f} segundos")
    print(f"Log de produtos atualizados com sucesso salvo em: {SUCCESS_LOG_FILENAME}")


if __name__ == "__main__":
    asyncio.run(main())