import requests
import json

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

def find_company_price_item_id(tiss_code):
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
        response = requests.post(url_item_finder, headers=headers_essenciais, json=payload)
        response.raise_for_status()
        return response.json()  # Retorna a resposta JSON se a requisição for bem-sucedida

    except requests.exceptions.HTTPError as errh:
        print(f"Erro HTTP ao buscar company_price_item_id para TISS Code {tiss_code}: {errh}")
        if errh.response is not None:
            print(f"  Response Body: {errh.response.text}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Erro ao buscar company_price_item_id para TISS Code {tiss_code}: {err}")
        return None

def update_product_info(product_id, company_price_item_id, detail_info="Descrição: [DESCRICAO] Código TISS: [COD_TISS]"):
    url_update_product = f"{BASE_URL}/product-imported-info-link"
    payload_update = {
        "id": None,
        "product_id": product_id,
        "detail_info": detail_info,
        "company_price_item_id": company_price_item_id,
        "conversion": 1,
        "type": "brasindice"
    }

    try:
        response = requests.post(url_update_product, headers=headers_essenciais, json=payload_update)
        response.raise_for_status()
        print(f"Produto ID: {product_id} atualizado com company_price_item_id: {company_price_item_id} com sucesso.")

    except requests.exceptions.HTTPError as errh:
        print(f"Erro HTTP ao atualizar Produto ID {product_id}: {errh}")
        if errh.response is not None:
            print(f"  Response Body: {errh.response.text}")
    except requests.exceptions.RequestException as err:
        print(f"Erro ao atualizar Produto ID {product_id}: {err}")


def process_product(product_id, tiss_code):
    print(f"Processando Produto ID: {product_id}, TISS Code: {tiss_code}")
    items = find_company_price_item_id(tiss_code)
    if items and isinstance(items, list) and items: # Verifica se items não é None, é lista e não está vazia
        selected_item_id = None
        max_pmc = -1
        selected_item = None

        for item in items:
            pmc = item.get('vl_pmc')
            if isinstance(pmc, (int, float)) and pmc > max_pmc:  # Verifica se vl_pmc é um número
                max_pmc = pmc
                selected_item = item

        if selected_item:
            selected_item_id = selected_item.get('id')
            print(f"  company_price_item_id encontrado: {selected_item_id} (com maior vl_pmc)")
            update_product_info(product_id, selected_item_id)
        else:
            print(f"  company_price_item_id não encontrado com 'vl_pmc' válido para TISS Code: {tiss_code} para Produto ID: {product_id}")

    else:
        print(f"  company_price_item_id não encontrado para TISS Code: {tiss_code} para Produto ID: {product_id}")
    print("-----------------------")


if __name__ == "__main__":
    file_path = "relatorio-produtos_txt.txt"  # Nome do seu arquivo .txt

    try:
        with open(file_path, 'r') as file:
            for line in file:
                parts = line.strip().split(";")
                if len(parts) == 2:
                    product_id = parts[0].strip()
                    tiss_code = parts[1].strip()
                    process_product(product_id, tiss_code)
                else:
                    print(f"Linha ignorada devido a formato inválido: {line.strip()}")
        print("Processamento concluído para todos os produtos.")

    except FileNotFoundError:
        print(f"Erro: Arquivo '{file_path}' não encontrado.")
    except Exception as e:
        print(f"Ocorreu um erro geral: {e}")