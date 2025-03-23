import asyncio
import aiohttp
import json
import os
import time

# Configurações (ajuste conforme necessário)
BASE_URL = "https://app-bd.spincare.com.br/spincare/produto/{id}"  # Endpoint correto
TOKEN = "SEU TOKEN"  # Token do Chrome
OUTPUT_FILENAME_PREFIX = "produtos_codigo_tiss_run_missing_ids" # Prefixo para os nomes dos arquivos de saída - **MODIFICADO para IDs faltantes**
OUTPUT_FILENAME_EXTENSION = ".txt" # Extensão dos arquivos de saída
CONCURRENT_REQUESTS = 50  # Número de requisições simultâneas (ajuste com cuidado!)
DELAY_BETWEEN_REQUESTS_CONCURRENT = 0.01 # Pequena pausa entre lançar requisições concorrentes
INPUT_MISSING_IDS_FILENAME = "ids_faltantes_requisicao.txt" # Nome do arquivo com IDs faltantes - **NOVO**

headers = {
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

async def fetch_produto_codigo_tiss(session, product_id, output_file):
    """Função assíncrona para buscar produto, extrair codigo_tiss e salvar no arquivo."""
    request_url = BASE_URL.format(id=product_id)

    try:
        async with session.get(request_url, headers=headers) as response:
            response.raise_for_status()
            json_data = await response.json()

            codigo_tiss = json_data.get('ds_codigo_tiss')
            if codigo_tiss is None:
                codigo_tiss = ""  # Se for null, usa string vazia

            linha_txt = f"{product_id};{codigo_tiss}\n" # Formato ID;codigo_tiss

            output_file.write(linha_txt) # Escreve diretamente no arquivo aberto

            print(f"Extraído e salvo: ID {product_id}, Codigo TISS: {codigo_tiss}")

    except aiohttp.ClientError as e:
        print(f"Erro aiohttp para ID {product_id}: {e}")
    except json.JSONDecodeError as e:
        print(f"Erro JSON decode para ID {product_id}: {e} - Resposta textual: {await response.text() if response else 'Sem resposta'}")
    except Exception as e:
        print(f"Erro inesperado para ID {product_id}: {e}")


async def process_products_range(product_ids, output_file): # **MODIFICADO: Aceita lista de IDs**
    """Processa uma lista de IDs de produtos e salva no arquivo."""
    async with aiohttp.ClientSession() as session:
        tasks = []
        for product_id in product_ids: # Itera sobre a lista de IDs
            task = asyncio.create_task(fetch_produto_codigo_tiss(session, product_id, output_file)) # Passa o arquivo para a task
            tasks.append(task)
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS_CONCURRENT)

        await asyncio.gather(*tasks)


async def main(): # **MAIN REORGANIZADO PARA LER IDs DO ARQUIVO**
    """Função principal assíncrona para orquestrar, ler IDs do arquivo e salvar em TXT."""
    run_count = 1 # Contador de execuções, para nomear os arquivos
    output_filename = f"{OUTPUT_FILENAME_PREFIX}_run_{run_count}{OUTPUT_FILENAME_EXTENSION}" # Gera nome de arquivo

    missing_product_ids = []
    try:
        with open(INPUT_MISSING_IDS_FILENAME, 'r', encoding='utf-8') as ids_file: # Abre arquivo de IDs faltantes
            for line in ids_file:
                product_id_str = line.strip().rstrip(';') # Remove espaços e ; no final
                try:
                    product_id = int(product_id_str)
                    missing_product_ids.append(product_id)
                except ValueError:
                    print(f"Linha ignorada, ID inválido: {line.strip()}")
    except FileNotFoundError:
        print(f"Erro: Arquivo de IDs faltantes '{INPUT_MISSING_IDS_FILENAME}' não encontrado.")
        return

    if not missing_product_ids:
        print("Nenhum ID de produto faltante para processar. Verifique o arquivo ids_faltantes_requisicao.txt.")
        return

    print(f"Iniciando execução para IDs faltantes. Arquivo de saída: {output_filename}")
    print(f"Processando {len(missing_product_ids)} IDs faltantes.")


    with open(output_filename, 'w', encoding='utf-8') as output_file: # Abre arquivo para escrita
        await process_products_range(missing_product_ids, output_file) # Chama a função de processamento com a lista de IDs

    print(f"Execução para IDs faltantes concluída. Resultados salvos em: {output_filename}")
    print(f"Processo assíncrono geral concluído! Resultados salvos em arquivo: {output_filename}")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Tempo total de execução: {end_time - start_time:.2f} segundos")