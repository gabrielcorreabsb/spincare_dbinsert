import asyncio
import aiohttp
import json
import os
import time

# Configurações (ajuste conforme necessário)
BASE_URL = "https://app-bd.spincare.com.br/spincare/produto/{id}"  # Endpoint correto
TOKEN = "SEU TOKEN"  # Token do Chrome
START_ID = 140000  # ID inicial do intervalo - **INICIAL, será atualizado nos reinícios**
END_ID = 200000  # ID final do intervalo (ou ajuste para o range desejado)
OUTPUT_FILENAME_PREFIX = "produtos_codigo_tiss_run" # Prefixo para os nomes dos arquivos de saída
OUTPUT_FILENAME_EXTENSION = ".txt" # Extensão dos arquivos de saída
CONCURRENT_REQUESTS = 50  # Número de requisições simultâneas (ajuste com cuidado!)
DELAY_BETWEEN_REQUESTS_CONCURRENT = 0.01 # Pequena pausa entre lançar requisições concorrentes
MAX_REQUESTS_PER_RUN = 7000  # **NOVA CONFIGURAÇÃO: Máximo de requisições por execução**

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


async def process_products_range(start_id, end_id, output_file): # **FUNÇÃO REORGANIZADA**
    """Processa uma faixa de IDs de produtos e salva no arquivo."""
    request_count = 0 # Contador de requisições para esta execução
    async with aiohttp.ClientSession() as session:
        tasks = []
        for product_id in range(start_id, end_id + 1):
            if request_count >= MAX_REQUESTS_PER_RUN: # **VERIFICA LIMITE AQUI**
                print(f"Limite de {MAX_REQUESTS_PER_RUN} requisições atingido para esta execução. Parando e reiniciando...")
                break # Sai do loop interno, encerrando esta execução
            task = asyncio.create_task(fetch_produto_codigo_tiss(session, product_id, output_file)) # Passa o arquivo para a task
            tasks.append(task)
            await asyncio.sleep(DELAY_BETWEEN_REQUESTS_CONCURRENT)
            request_count += 1 # Incrementa o contador após cada requisição

        await asyncio.gather(*tasks)
    return product_id # Retorna o último ID processado (ou None se nenhum processado nesta execução)


async def main(): # **MAIN REORGANIZADO PARA REINICIAR E NOVOS ARQUIVOS**
    """Função principal assíncrona para orquestrar, reiniciar e salvar em TXT."""
    current_start_id = START_ID # Inicia com o START_ID inicial
    last_processed_id = None
    run_count = 1 # Contador de execuções, para nomear os arquivos

    while current_start_id <= END_ID: # Loop externo para reiniciar até END_ID ser alcançado
        output_filename = f"{OUTPUT_FILENAME_PREFIX}_run_{run_count}{OUTPUT_FILENAME_EXTENSION}" # Gera novo nome de arquivo para cada execução
        print(f"Iniciando execução {run_count}. Arquivo de saída: {output_filename}")
        print(f"Processando IDs a partir de: {current_start_id} até {END_ID}. Máximo {MAX_REQUESTS_PER_RUN} requisições.")

        with open(output_filename, 'w', encoding='utf-8') as output_file: # Abre um NOVO arquivo para cada execução (modo 'w')
            last_processed_id = await process_products_range(current_start_id, END_ID, output_file) # Chama a função de processamento

        print(f"Execução {run_count} concluída. Resultados salvos em: {output_filename}")

        if last_processed_id is not None:
            current_start_id = last_processed_id + 1 # Próxima execução começa do próximo ID
        else:
            print("Nenhum produto processado nesta execução. Parando.") # Se process_products_range retornar None (improvável, mas para segurança)
            break # Sai do loop externo se nenhum produto foi processado
        if current_start_id <= END_ID: # Pausa antes de reiniciar (opcional)
            print("Pausando por 5 segundos antes de reiniciar...")
            time.sleep(5) # Pausa de 5 segundos antes de reiniciar
        else:
            print("Todos os IDs processados. Concluído.") # Sai do loop se todos os IDs foram processados
            break
        run_count += 1 # Incrementa o contador de execuções para o próximo nome de arquivo


    print(f"Processo assíncrono geral concluído! Resultados salvos em arquivos com prefixo: {OUTPUT_FILENAME_PREFIX}_run_*")


if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(main())
    end_time = time.time()
    print(f"Tempo total de execução: {end_time - start_time:.2f} segundos")