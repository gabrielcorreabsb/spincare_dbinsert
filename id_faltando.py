import os

# Configurações (ajuste conforme necessário)
START_ID = 0  # ID inicial do intervalo
END_ID = 200000  # ID final do intervalo
INPUT_FILENAME = "produtos.txt" # Nome do arquivo de entrada com os IDs processados
OUTPUT_MISSING_IDS_FILENAME = "ids_faltantes_requisicao.txt" # Nome do arquivo de saída para IDs faltantes no formato de requisição

def generate_missing_ids_request_file():
    """
    Lê o arquivo produtos.txt, identifica IDs faltantes no range especificado
    e gera um novo arquivo txt com esses IDs no formato de requisição (ID;).
    """

    processed_ids = set()

    try:
        with open(INPUT_FILENAME, 'r', encoding='utf-8') as infile:
            for line in infile:
                parts = line.strip().split(";")
                if len(parts) >= 1:
                    try:
                        product_id = int(parts[0].strip())
                        processed_ids.add(product_id)
                    except ValueError:
                        print(f"Linha com ID inválido no arquivo {INPUT_FILENAME}: {line.strip()}")
    except FileNotFoundError:
        print(f"Erro: Arquivo de entrada '{INPUT_FILENAME}' não encontrado.")
        return
    except Exception as e:
        print(f"Erro ao ler o arquivo '{INPUT_FILENAME}': {e}")
        return

    expected_ids = set(range(START_ID, END_ID + 1))
    missing_ids = sorted(list(expected_ids - processed_ids))

    if missing_ids:
        print(f"Encontrados {len(missing_ids)} IDs de produtos faltantes.")
        try:
            with open(OUTPUT_MISSING_IDS_FILENAME, 'w', encoding='utf-8') as outfile:
                for product_id in missing_ids:
                    outfile.write(f"{product_id};\n") # Formato ID; para requisição
            print(f"IDs faltantes salvos no formato de requisição em: {OUTPUT_MISSING_IDS_FILENAME}")
        except Exception as e:
            print(f"Erro ao salvar IDs faltantes em {OUTPUT_MISSING_IDS_FILENAME}: {e}")
    else:
        print("Nenhum ID de produto faltante encontrado no range especificado. Todos os IDs em 'produtos.txt' cobrem o range completo.")

if __name__ == "__main__":
    generate_missing_ids_request_file()
    print("Processo de verificação de IDs faltantes e geração do arquivo de requisição concluído.")