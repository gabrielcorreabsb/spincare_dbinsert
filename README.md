# Scripts Python para Gestão de Produtos Spincare

[![Python](https://img.shields.io/badge/Python-3.7+-blue.svg?logo=python&logoColor=white)](https://www.python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Replace with your actual license badge if different -->

Este repositório contém um conjunto abrangente de scripts Python desenvolvidos para **automatizar e otimizar a gestão de produtos na plataforma Spincare**. O foco principal é aprimorar o catálogo de produtos através da **vinculação precisa com tabelas de preços (Brasindice e Simpro)** e da **atualização eficiente de informações cruciais**, como códigos TISS.  Estas ferramentas são projetadas para simplificar processos que, de outra forma, seriam manuais e demorados, permitindo uma gestão de produtos mais ágil e confiável.

## 🚀 Fluxo de Trabalho Sugerido para Gestão de Produtos Spincare 🚀

Este fluxo de trabalho descreve uma sequência **lógica e altamente recomendada** para utilizar os scripts de forma eficaz. Seguir esta ordem garante um processo completo e organizado, desde a coleta inicial de dados até a manutenção e correção das informações dos produtos na plataforma Spincare.

1.  **⚙️ Preparação Inicial: Extração de Códigos TISS em Massa (com `requisicao_spincare.py`)**

    *   **Objetivo Principal:**  Iniciar o processo obtendo os códigos TISS (Código Terminologia de Saúde Suplementar) para um amplo intervalo de IDs de produtos. Esta etapa fundamental cria a base de dados necessária para os passos subsequentes, permitindo a vinculação e atualização dos produtos.
    *   **Ação Detalhada:** Execute o script `requisicao_spincare.py`.
        *   **Configuração Essencial:** Antes de executar, **edite diretamente no script** as variáveis `START_ID`, `END_ID` e `MAX_REQUESTS_PER_RUN`.
            *   `START_ID`: Defina o ID do produto inicial do intervalo que você deseja processar.
            *   `END_ID`: Defina o ID do produto final do intervalo.
            *   `MAX_REQUESTS_PER_RUN`: Ajuste este valor para controlar o número máximo de requisições que o script fará em cada execução. Um valor menor (ex: 5000-7000) ajuda a evitar sobrecarregar o servidor da Spincare e facilita a retomada do processo.
        *   **Execução:** Abra um terminal, navegue até a pasta onde você salvou os scripts e execute o comando: `python requisicao_spincare.py`
        *   **Saída Esperada:** O script irá gerar arquivos de texto nomeados sequencialmente como `produtos_codigo_tiss_run_*.txt`. Cada arquivo conterá linhas no formato `ID_DO_PRODUTO;CODIGO_TISS` para os produtos processados naquele lote.
        *   **Observação Crucial:** `requisicao_spincare.py` é projetado para ser executado **múltiplas vezes**. Ele processa o intervalo de IDs em partes (lotes), salvando os resultados em arquivos separados a cada execução. Isso é vital para lidar com grandes volumes de dados, evitar timeouts da API e permitir a retomada do processo exatamente de onde parou, caso seja interrompido.

2.  **🔍 Detecção de Lacunas: Identificação de IDs de Produtos Faltantes (com `id_faltando.py`)**

    *   **Objetivo Principal:** Após executar `requisicao_spincare.py` por um período (ou se você já possui um arquivo `produtos.txt` com IDs processados), utilize `id_faltando.py` para **identificar se existem IDs de produtos *faltantes* no seu conjunto de dados**. Este script compara um intervalo de IDs esperado com os IDs já processados, revelando "lacunas" que precisam ser preenchidas.
    *   **Ação Detalhada:** Execute o script `id_faltando.py`.
        *   **Configuração Necessária:** **Edite diretamente no script** as variáveis `START_ID` e `END_ID` para definir o intervalo de IDs que você deseja verificar. Certifique-se também de que a variável `INPUT_FILENAME` esteja configurada corretamente para apontar para o arquivo que contém os IDs de produtos já processados (geralmente, você pode usar `produtos.txt` se já o tiver, ou um dos arquivos `produtos_codigo_tiss_run_*.txt` se estiver começando).
        *   **Execução:** No terminal, execute: `python id_faltando.py`
        *   **Saída Esperada:** O script irá gerar o arquivo `ids_faltantes_requisicao.txt`. Este arquivo conterá uma lista de IDs de produtos que foram identificados como faltantes dentro do intervalo especificado. Cada linha conterá um ID no formato `ID_DO_PRODUTO;`.
        *   **Utilidade:** `id_faltando.py` é essencial para **garantir a completude do seu conjunto de dados**. Ele ajuda a identificar se algum ID dentro do intervalo esperado não foi processado corretamente ou se há falhas na sua coleta de dados inicial.

3.  **🛠️ Correção de Falhas: Obtenção de Códigos TISS para IDs Faltantes (com `id_fix.py`)**

    *   **Objetivo Principal:** Uma vez que `id_faltando.py` identificou os IDs faltantes, `id_fix.py` entra em ação para **resolver essas "falhas"**, buscando e obtendo os códigos TISS *especificamente para esses IDs*. Este script utiliza a lista de IDs faltantes gerada no passo anterior para direcionar suas requisições à API da Spincare.
    *   **Ação Detalhada:** Execute o script `id_fix.py`.
        *   **Entrada Automática:** `id_fix.py` **automaticamente lê** a lista de IDs faltantes do arquivo `ids_faltantes_requisicao.txt` (gerado por `id_faltando.py`). **Não é necessário configurar nenhum arquivo de entrada adicional.**
        *   **Execução:** No terminal, execute: `python id_fix.py`
        *   **Saída Esperada:** O script irá gerar arquivos de texto nomeados como `produtos_codigo_tiss_run_missing_ids_run_*.txt`. Cada arquivo conterá linhas no formato `ID_DO_PRODUTO;CODIGO_TISS` para os IDs faltantes e seus respectivos códigos TISS obtidos.
        *   **Otimização:** `id_fix.py` é **altamente otimizado** para processar apenas os IDs faltantes. Ele evita o reprocessamento de IDs já obtidos, tornando o processo mais eficiente e rápido.

4.  **🗂️ Consolidação de Dados: Preparação do Arquivo `produtos.txt`**

    *   **Objetivo Principal:** Para o próximo passo crucial (`atualizar_produtos.py`), é necessário **consolidar todos os códigos TISS obtidos** em um único arquivo de entrada padronizado: `produtos.txt`. Este arquivo servirá como a fonte de dados para a atualização em massa dos produtos.
    *   **Ação Manual:** Este passo requer **ação manual** para combinar os dados.
        *   **Reúna os Arquivos:** Localize e reúna todos os arquivos de saída gerados por `requisicao_spincare.py` (`produtos_codigo_tiss_run_*.txt`) e `id_fix.py` (`produtos_codigo_tiss_run_missing_ids_run_*.txt`).
        *   **Combine os Dados:** Abra um editor de texto (como Notepad++, Sublime Text, VS Code) e **combine o conteúdo de todos esses arquivos em um único arquivo chamado `produtos.txt`**. Certifique-se de que cada linha no `produtos.txt` siga o formato **`ID_DO_PRODUTO;CODIGO_TISS`**.
        *   **Verificação (Recomendado):** Após a combinação, revise o arquivo `produtos.txt` para garantir que não há linhas duplicadas ou erros de formatação. Uma formatação correta é essencial para o próximo script funcionar corretamente.

5.  **🚀 Atualização em Massa: Vinculação e Atualização de Produtos (com `atualizar_produtos.py`)**

    *   **Objetivo Principal:** Utilizando o arquivo `produtos.txt` preparado no passo anterior, execute `atualizar_produtos.py` para **vincular em massa os produtos na plataforma Spincare a itens correspondentes nas tabelas de preços Brasindice e Simpro**. Este script automatiza a vinculação com base nos códigos TISS, enriquecendo as informações dos produtos.
    *   **Ação Detalhada:** Execute o script `atualizar_produtos.py`.
        *   **Entrada Automática:** `atualizar_produtos.py` **lê automaticamente** os dados do arquivo `produtos.txt` (que você preparou no passo anterior).
        *   **Execução:** No terminal, execute: `python atualizar_produtos.py`
        *   **Saída Esperada:** O script irá atualizar as informações dos produtos na Spincare, realizando a vinculação com Brasindice e Simpro. Além disso, ele irá gerar o arquivo `produtos_atualizados_sucesso.txt`, que registra os IDs dos produtos que foram atualizados com sucesso durante esta execução. Este arquivo será importante para os próximos passos.

6.  **✅ Garantia de Qualidade: Correção de Links Incorretos (com `corrigindo_produtos.py`)**

    *   **Objetivo Principal:** Após a atualização em massa, é crucial **garantir a qualidade dos links criados**. `corrigindo_produtos.py` verifica e corrige possíveis links incorretos, removendo aqueles onde o nome do item vinculado não corresponde adequadamente ao nome do produto principal. Esta etapa assegura que os links sejam relevantes e precisos.
    *   **Ação Detalhada:** Execute o script `corrigindo_produtos.py`.
        *   **Entrada Automática:** `corrigindo_produtos.py` **lê automaticamente** a lista de produtos atualizados com sucesso do arquivo `produtos_atualizados_sucesso.txt` (gerado por `atualizar_produtos.py`).
        *   **Execução:** No terminal, execute: `python corrigindo_produtos.py`
        *   **Saídas Esperadas:** O script irá gerar dois arquivos de saída:
            *   `links_deletados.txt`: Contém uma lista de IDs de produtos cujos links foram deletados por serem considerados não similares (nomes de produtos diferentes).
            *   `produtos_links_corrigidos.txt`: Contém uma lista de IDs de produtos cujos links foram considerados corretos e similares.
        *   **Importância da Verificação:** `corrigindo_produtos.py` é **fundamental para a manutenção da qualidade dos dados**. Ele evita a propagação de links incorretos, que poderiam levar a informações imprecisas ou problemas na plataforma Spincare.

7.  **🔄 Revinculação Estratégica: Revinculação ao Brasindice (Opcional, com `revincular_brasindice.py`)**

    *   **Objetivo Principal (Opcional):** Se o passo de correção (`corrigindo_produtos.py`) removeu alguns links, você pode utilizar `revincular_brasindice.py` para **tentar revincular esses produtos, focando especificamente na tabela de preços Brasindice**. Este script oferece uma tentativa de revinculação direcionada, especialmente útil se a tabela Brasindice for sua principal fonte de referência.
    *   **Ação Detalhada (Opcional):** Execute o script `revincular_brasindice.py`.
        *   **Entrada Automática:** `revincular_brasindice.py` **lê automaticamente** os IDs de produtos do arquivo `links_deletados.txt` (gerado por `corrigindo_produtos.py`).
        *   **Execução:** No terminal, execute: `python revincular_brasindice.py`
        *   **Saída Esperada:** O script tentará revincular os produtos ao Brasindice e gerará o arquivo `produtos_revinculados_brasindice_async.txt`, que lista os produtos que foram revinculados com sucesso ao Brasindice.
        *   **Uso Opcional:** A revinculação é **opcional**. Utilize este script se você deseja tentar reestabelecer links para os produtos que foram desvinculados, priorizando a tabela Brasindice.

8.  **🔎 Consulta Pontual: Busca e Atualização Individual (com `spincare_item_finder.py` - Uso Manual e Específico)**

    *   **Objetivo Principal (Uso Pontual):** Para casos **específicos, testes rápidos ou para verificar informações de um único produto**, utilize `spincare_item_finder.py`. Este script permite buscar o `company_price_item_id` para um código TISS individualmente e, opcionalmente, atualizar as informações de um produto específico.
    *   **Ação Manual e Direta:** Execute o script `spincare_item_finder.py`.
        *   **Arquivo de Entrada Manual:** Edite ou crie o arquivo `relatorio-produtos_txt.txt`. Este arquivo **requer entrada manual**. Adicione linhas no formato `ID_DO_PRODUTO;CODIGO_TISS` para os produtos que você deseja consultar ou atualizar individualmente.
        *   **Execução:** No terminal, execute: `python spincare_item_finder.py`
        *   **Saída no Console:** A saída principal deste script será **impressa diretamente no console (terminal)**. Ele exibirá informações sobre o `company_price_item_id` encontrado (se houver) e mensagens de sucesso ou erro para cada produto processado.
        *   **Uso Específico:** `spincare_item_finder.py` é **ideal para uso pontual e manual**. Não é projetado para processamento em massa. Utilize-o para verificações rápidas, testes ou para corrigir informações de produtos individuais conforme necessário.

**🔄 Ordem de Execução Otimizada:**

`requisicao_spincare.py` (Extração inicial de TISS) -> `id_faltando.py` (Detecção de IDs faltantes) -> `id_fix.py` (Correção de IDs faltantes - obtenção de TISS) -> (Preparar `produtos.txt` - Consolidação manual) -> `atualizar_produtos.py` (Atualização em massa e vinculação) -> `corrigindo_produtos.py` (Garantia de qualidade - correção de links) -> `revincular_brasindice.py` (Revinculação opcional ao Brasindice) -> `spincare_item_finder.py` (Consulta individual - uso pontual)

---

## Sobre os Programas

Este repositório inclui os seguintes scripts Python, cada um com uma finalidade específica dentro do fluxo de trabalho de gestão de produtos Spincare:

*   **`atualizar_produtos.py`**:
    *   **Finalidade:**  Atualiza informações de produtos na plataforma Spincare, vinculando-os a itens correspondentes nas tabelas de preços Brasindice e Simpro com base em seus códigos TISS.
    *   **Funcionalidades:**
        *   Lê uma lista de IDs de produtos e códigos TISS de um arquivo de texto (`produtos.txt`).
        *   Busca, de forma assíncrona, itens correspondentes nas tabelas Brasindice e Simpro usando a API da Spincare.
        *   Seleciona o melhor item (com base no maior valor de PMC - Preço Máximo ao Consumidor, se disponível).
        *   Atualiza as informações do produto na Spincare, vinculando-o ao item selecionado.
        *   Registra os produtos atualizados com sucesso em `produtos_atualizados_sucesso.txt`.

*   **`corrigindo_produtos.py`**:
    *   **Finalidade:**  Verifica e corrige links de produtos que foram previamente atualizados, removendo links onde o nome do item vinculado não é similar ao nome do produto principal.
    *   **Funcionalidades:**
        *   Lê a lista de produtos atualizados com sucesso de `produtos_atualizados_sucesso.txt`.
        *   Busca, de forma assíncrona, os links de itens importados para cada produto.
        *   Compara o nome do item vinculado com o nome do produto principal para verificar similaridade (baseado nas primeiras palavras do nome).
        *   Deleta links considerados não similares e registra os links deletados em `links_deletados.txt`.
        *   Registra os links considerados corretos (similares) em `produtos_links_corrigidos.txt`.

*   **`id_faltando.py`**:
    *   **Finalidade:**  Identifica IDs de produtos faltantes dentro de um intervalo especificado, comparando com os IDs já processados listados em `produtos.txt`.
    *   **Funcionalidades:**
        *   Define um intervalo de IDs de produtos (inicial e final) no próprio script.
        *   Lê IDs de produtos processados do arquivo `produtos.txt`.
        *   Compara o intervalo definido com os IDs processados para encontrar IDs faltantes.
        *   Gera um arquivo `ids_faltantes_requisicao.txt` contendo os IDs faltantes no formato adequado para serem usados em outros scripts (ex: `id_fix.py`).

*   **`id_fix.py`**:
    *   **Finalidade:**  Busca e salva os códigos TISS para uma lista de IDs de produtos faltantes, lendo os IDs do arquivo `ids_faltantes_requisicao.txt`.
    *   **Funcionalidades:**
        *   Lê IDs de produtos faltantes do arquivo `ids_faltantes_requisicao.txt`.
        *   Para cada ID, faz uma requisição assíncrona à API da Spincare para obter os dados do produto.
        *   Extrai o código TISS (`ds_codigo_tiss`) dos dados do produto.
        *   Salva os IDs dos produtos e seus códigos TISS correspondentes em arquivos de saída no formato `produtos_codigo_tiss_run_missing_ids_run_*.txt`.

*   **`requisicao_spincare.py`**:
    *   **Finalidade:**  Extrai códigos TISS de produtos em um grande intervalo de IDs e salva os resultados em arquivos de texto, com controle de requisições por execução para evitar sobrecarga do servidor.
    *   **Funcionalidades:**
        *   Define um intervalo de IDs de produtos (inicial e final) e um limite máximo de requisições por execução no próprio script.
        *   Processa os IDs em lotes, fazendo requisições assíncronas para a API da Spincare para obter dados de produtos.
        *   Extrai o código TISS de cada produto.
        *   Salva os IDs dos produtos e seus códigos TISS em arquivos de saída nomeados sequencialmente (`produtos_codigo_tiss_run_*.txt`) para cada execução.
        *   Reinicia o processo automaticamente para continuar do ponto onde parou, até completar o intervalo de IDs definido.

*   **`revincular_brasindice.py`**:
    *   **Finalidade:**  Revincula produtos à tabela de preços Brasindice, utilizando IDs de produtos que tiveram seus links deletados previamente.
    *   **Funcionalidades:**
        *   Lê IDs de produtos do arquivo `links_deletados.txt`.
        *   Para cada ID, busca o código TISS do produto na API da Spincare.
        *   Busca itens correspondentes na tabela Brasindice usando o código TISS.
        *   Seleciona o melhor item Brasindice (com base no maior valor de PMC, se disponível).
        *   Revincula o produto ao item Brasindice selecionado.
        *   Registra os produtos revinculados com sucesso em `produtos_revinculados_brasindice_async.txt`.

*   **`spincare_item_finder.py`**:
    *   **Finalidade:**  Script utilitário para encontrar o `company_price_item_id` correspondente a um código TISS específico e atualizar as informações de um produto com este ID.
    *   **Funcionalidades:**
        *   Lê pares de ID de produto e código TISS do arquivo `relatorio-produtos_txt.txt`.
        *   Para cada código TISS, busca, de forma síncrona, itens correspondentes na tabela Brasindice usando a API da Spincare.
        *   Seleciona o melhor item Brasindice (com base no maior valor de PMC, se disponível).
        *   Atualiza as informações do produto na Spincare, vinculando-o ao item Brasindice selecionado.

## Como Usar

Para utilizar esses scripts de forma eficaz, siga as instruções detalhadas abaixo:

### Pré-requisitos Essenciais

Antes de começar, certifique-se de ter os seguintes pré-requisitos instalados e configurados em seu ambiente:

*   **🐍 Python 3.7 ou Superior:** Os scripts são desenvolvidos em Python e requerem a versão 3.7 ou superior para funcionar corretamente. Você pode verificar sua versão do Python abrindo um terminal e digitando `python --version` ou `python3 --version`. Se necessário, baixe e instale a versão mais recente do Python em [https://www.python.org/downloads/](https://www.python.org/downloads/).

*   **📦 Bibliotecas Python Necessárias:** Os scripts dependem de bibliotecas Python externas para realizar tarefas como requisições HTTP assíncronas e manipulação de dados JSON. As bibliotecas necessárias são:
    *   `requests`: Para requisições HTTP síncronas (utilizado em `spincare_item_finder.py`).
    *   `aiohttp`: Para requisições HTTP assíncronas, permitindo maior eficiência e velocidade (utilizado nos demais scripts).
    *   `asyncio`: Para programação assíncrona em Python (essencial para `aiohttp`).

    Você pode instalar todas as dependências de uma vez usando o `pip`, o gerenciador de pacotes do Python. **Recomendação:** Crie um arquivo `requirements.txt` na raiz do seu repositório com o seguinte conteúdo:
    ```
    requests
    aiohttp
    ```
    Em seguida, abra um terminal na pasta do repositório e execute o comando:
    ```bash
    pip install -r requirements.txt
    ```
    Ou, se preferir instalar individualmente, execute:
    ```bash
    pip install requests aiohttp
    ```

*   **🔑 Token de Acesso à API Spincare:**  A comunicação com a API da Spincare é autenticada por meio de um token de acesso. **Este token é crítico para o funcionamento dos scripts.**  Você precisará obter um token de acesso válido da plataforma Spincare (geralmente obtido através do seu perfil de usuário ou configurações de API na plataforma).

    **❗ Segurança do Token:**  **Mantenha seu token de acesso em segurança!** Ele concede acesso à sua conta e dados na Spincare.
        *   **Nunca compartilhe seu token publicamente.**
        *   **Não inclua o token diretamente no código se for versionar o repositório publicamente.**
        *   **Substitua o valor padrão `TOKEN = "SEU_TOKEN_AQUI"` em cada script pelo seu token real antes de executar os scripts.**  Abra cada arquivo `.py` e localize a linha `TOKEN = "Bearer ..."` e substitua o valor `SEU_TOKEN_AQUI` pelo seu token de acesso da Spincare.

### Configuração Inicial do Ambiente

Siga estes passos para configurar seu ambiente de trabalho antes de executar os scripts:

1.  **📥 Clonar o Repositório (Opcional, se você estiver usando Git):** Se você estiver utilizando o Git para controle de versão, clone este repositório para sua máquina local. Caso contrário, você pode simplesmente baixar os arquivos dos scripts.
    ```bash
    git clone [URL_DO_SEU_REPOSITÓRIO]
    cd [NOME_DO_REPOSITÓRIO]
    ```
    Substitua `[URL_DO_SEU_REPOSITÓRIO]` pelo URL do seu repositório GitHub e `[NOME_DO_REPOSITÓRIO]` pelo nome da pasta que será criada.

2.  **📦 Instalar as Dependências Python:** Se você criou o arquivo `requirements.txt` conforme recomendado, navegue até a pasta do repositório no terminal e execute:
    ```bash
    pip install -r requirements.txt
    ```
    Isso instalará automaticamente todas as bibliotecas necessárias listadas no `requirements.txt`. Se você optar por instalar individualmente, use os comandos `pip install requests aiohttp` conforme mencionado nos Pré-requisitos.

3.  **🔑 Configurar os Tokens de Acesso:** **Este passo é essencial para a segurança e funcionamento dos scripts.**
    *   **Abra cada arquivo `.py`** (ex: `atualizar_produtos.py`, `corrigindo_produtos.py`, etc.) em um editor de texto.
    *   **Localize a linha que define a variável `TOKEN`**. Geralmente, ela se parece com: `TOKEN = "Bearer SEU_TOKEN_AQUI"`.
    *   **Substitua o valor `"SEU_TOKEN_AQUI"` pelo seu token de acesso real da API Spincare.**  Mantenha as aspas e certifique-se de incluir o prefixo `"Bearer "` antes do seu token.
    *   **Salve as alterações em cada arquivo `.py` após substituir o token.**
    *   **Verifique Duplamente:** Confirme que você substituiu o token em **todos os scripts** que utilizam a variável `TOKEN`.

### Executando os Scripts Python

Cada script foi projetado para ser executado diretamente a partir da linha de comando. Siga estas instruções gerais e, em seguida, consulte a seção "Detalhes de Uso por Script" para instruções específicas de cada script.

*   **Navegue até o Diretório:** Abra um terminal ou prompt de comando e use o comando `cd` para navegar até o diretório onde você salvou os arquivos dos scripts Python (o diretório do repositório clonado ou a pasta onde você baixou os scripts).

*   **Executar o Script:** Para executar um script específico, use o comando `python` seguido do nome do script. Por exemplo, para executar `atualizar_produtos.py`, digite:
    ```bash
    python atualizar_produtos.py
    ```
    Ou, se você estiver usando `python3` como padrão:
    ```bash
    python3 atualizar_produtos.py
    ```
    Pressione Enter para executar o comando. O script será iniciado e exibirá mensagens no terminal indicando o progresso, erros ou conclusões.

#### Detalhes de Uso por Script

Esta seção fornece detalhes específicos sobre como executar e configurar cada script individualmente, incluindo arquivos de entrada, arquivos de saída e quaisquer configurações adicionais. **Leia atentamente as instruções para cada script antes de executá-lo.**

*   **`atualizar_produtos.py`**:
    *   **Finalidade Primária:** Atualizar informações de produtos e vinculá-los a itens Brasindice/Simpro.
    *   **Arquivo de Entrada:** `produtos.txt` - **Formato Obrigatório:** Cada linha deve conter `ID_DO_PRODUTO;CODIGO_TISS`. Crie este arquivo ou certifique-se de que ele esteja corretamente formatado antes de executar o script.
    *   **Arquivo de Saída:** `produtos_atualizados_sucesso.txt` - Registra os IDs dos produtos que foram atualizados com sucesso durante a execução.
    *   **Configurações:** Nenhuma configuração adicional no script é geralmente necessária após definir o `TOKEN`.
    *   **Execução:** `python atualizar_produtos.py`

*   **`corrigindo_produtos.py`**:
    *   **Finalidade Primária:** Corrigir links de produtos, removendo links não similares.
    *   **Arquivo de Entrada:** `produtos_atualizados_sucesso.txt` - Este arquivo é **gerado automaticamente** por `atualizar_produtos.py`. Certifique-se de executar `atualizar_produtos.py` primeiro para gerar este arquivo de entrada.
    *   **Arquivos de Saída:**
        *   `links_deletados.txt` - Lista de IDs de produtos cujos links foram deletados.
        *   `produtos_links_corrigidos.txt` - Lista de IDs de produtos cujos links foram considerados corretos.
    *   **Configurações:** Nenhuma configuração adicional no script é geralmente necessária após definir o `TOKEN`.
    *   **Execução:** `python corrigindo_produtos.py`

*   **`id_faltando.py`**:
    *   **Finalidade Primária:** Identificar IDs de produtos faltantes em um intervalo.
    *   **Arquivo de Entrada:** `produtos.txt` (ou um arquivo similar contendo IDs já processados). **Formato Esperado:** Cada linha deve conter pelo menos o ID do produto (o formato exato pode ser adaptado, veja o script).
    *   **Arquivo de Saída:** `ids_faltantes_requisicao.txt` - Lista de IDs de produtos faltantes, no formato `ID_DO_PRODUTO;`.
    *   **Configurações Essenciais (Diretamente no Script):**
        *   `START_ID`: ID inicial do intervalo a ser verificado. **Edite no script.**
        *   `END_ID`: ID final do intervalo a ser verificado. **Edite no script.**
        *   `INPUT_FILENAME`: Nome do arquivo de entrada com os IDs processados (padrão: `produtos.txt`). **Verifique e edite se necessário no script.**
    *   **Execução:** `python id_faltando.py`

*   **`id_fix.py`**:
    *   **Finalidade Primária:** Obter códigos TISS para IDs de produtos faltantes.
    *   **Arquivo de Entrada:** `ids_faltantes_requisicao.txt` - **Gerado automaticamente** por `id_faltando.py`.
    *   **Arquivos de Saída:** Arquivos nomeados como `produtos_codigo_tiss_run_missing_ids_run_*.txt` - Contêm IDs faltantes e seus códigos TISS.
    *   **Configurações:** Nenhuma configuração adicional no script é geralmente necessária após definir o `TOKEN`.
    *   **Execução:** `python id_fix.py`

*   **`requisicao_spincare.py`**:
    *   **Finalidade Primária:** Extrair códigos TISS para um intervalo de IDs de produtos.
    *   **Arquivo de Saída:** Arquivos nomeados como `produtos_codigo_tiss_run_*.txt` - Contêm IDs de produtos e seus códigos TISS.
    *   **Configurações Essenciais (Diretamente no Script):**
        *   `START_ID`: ID inicial do intervalo a ser processado. **Edite no script.**
        *   `END_ID`: ID final do intervalo a ser processado. **Edite no script.**
        *   `MAX_REQUESTS_PER_RUN`: Número máximo de requisições por execução. **Ajuste no script.**
    *   **Execução:** `python requisicao_spincare.py`

*   **`revincular_brasindice.py`**:
    *   **Finalidade Primária:** Revincular produtos ao Brasindice.
    *   **Arquivo de Entrada:** `links_deletados.txt` - **Gerado automaticamente** por `corrigindo_produtos.py`.
    *   **Arquivo de Saída:** `produtos_revinculados_brasindice_async.txt` - Registra produtos revinculados ao Brasindice.
    *   **Configurações:** Nenhuma configuração adicional no script é geralmente necessária após definir o `TOKEN`.
    *   **Execução:** `python revincular_brasindice.py`

*   **`spincare_item_finder.py`**:
    *   **Finalidade Primária:** Busca e atualiza informações de um único produto com base no código TISS.
    *   **Arquivo de Entrada:** `relatorio-produtos_txt.txt` - **Formato Obrigatório:** Cada linha deve conter `ID_DO_PRODUTO;CODIGO_TISS`. **Crie ou edite este arquivo manualmente** para os produtos que deseja processar.
    *   **Saída:** Resultados e mensagens de progresso são exibidos diretamente no **console (terminal)** durante a execução.
    *   **Configurações:** Nenhuma configuração adicional no script é geralmente necessária após definir o `TOKEN`.
    *   **Execução:** `python spincare_item_finder.py`

### ⚠️ Observações Importantes e Boas Práticas

*   **🔑 Segurança do Token de Acesso:** Reitere-se a importância de manter seu token de acesso à API Spincare seguro e privado. Nunca o compartilhe publicamente ou o inclua diretamente no código versionado em repositórios públicos.

*   **🚦 Limites de Requisição da API Spincare:** Esteja ciente dos limites de taxa e requisição da API da Spincare. Exceder esses limites pode resultar em bloqueios temporários ou permanentes do seu acesso.
    *   Os scripts assíncronos (`atualizar_produtos.py`, `corrigindo_produtos.py`, `id_fix.py`, `requisicao_spincare.py`, `revincular_brasindice.py`) e o parâmetro `MAX_REQUESTS_PER_RUN` em `requisicao_spincare.py` foram implementados para ajudar a mitigar o risco de sobrecarga.
    *   **Monitore o uso dos scripts e os logs de execução.** Se você começar a receber erros relacionados a limites de taxa (ex: HTTP 429 - Too Many Requests), reduza a concorrência (ajuste `CONCURRENT_REQUESTS` nos scripts assíncronos e `MAX_REQUESTS_PER_RUN` em `requisicao_spincare.py`) e aumente os intervalos de espera entre as requisições (`DELAY_BETWEEN_REQUESTS_CONCURRENT`).

*   **📁 Gerenciamento de Arquivos de Entrada e Saída:**
    *   **Verifique os formatos esperados dos arquivos de entrada** para cada script (especialmente `produtos.txt` e `relatorio-produtos_txt.txt`). Formatos incorretos podem causar erros ou resultados inesperados.
    *   **Monitore os arquivos de saída gerados por cada script** (arquivos `.txt`). Eles contêm informações importantes sobre o progresso, sucessos, erros e listas de IDs processados.
    *   **Adapte os caminhos dos arquivos nos scripts, se necessário**, caso você queira usar nomes de arquivos diferentes ou organizar os arquivos em subpastas.

*   **🐛 Tratamento de Erros e Logs:**
    *   Os scripts incluem tratamento de erros básico, como logs de erros HTTP e JSON, e mensagens informativas no console.
    *   **Examine atentamente o console (terminal) durante a execução dos scripts** para identificar mensagens de erro, avisos ou informações de progresso.
    *   **Verifique os arquivos de log de saída** (ex: `produtos_atualizados_sucesso.txt`, `links_deletados.txt`, etc.) para obter detalhes sobre o que foi processado com sucesso e quaisquer problemas que possam ter ocorrido.
    *   Em caso de erros persistentes, revise o código, verifique as configurações (token, arquivos de entrada), e consulte a documentação da API Spincare, se disponível.

*   **📄 `requirements.txt` (Altamente Recomendado):** Utilizar um arquivo `requirements.txt` para gerenciar as dependências do projeto é uma boa prática. Isso facilita a configuração do ambiente para você e para qualquer pessoa que for utilizar ou contribuir com os scripts. Certifique-se de que o `requirements.txt` inclua todas as bibliotecas necessárias (`requests`, `aiohttp`).

## Contribuição

Contribuições para este projeto são calorosamente bem-vindas! Se você tiver sugestões de melhorias, correções de bugs, otimizações de código, novos scripts úteis ou melhorias na documentação, sinta-se à vontade para contribuir. As formas de contribuir incluem:

*   **Reportar Issues:** Se você encontrar bugs, comportamentos inesperados ou tiver sugestões de melhorias, abra uma Issue detalhada no repositório. Inclua o máximo de informações possível para que a issue seja clara e acionável.
*   **Enviar Pull Requests (PRs):** Se você tiver desenvolvido uma correção de bug, uma nova funcionalidade ou melhorias, envie um Pull Request (PR) com suas alterações.
    *   **Descreva claramente suas mudanças no PR.**
    *   **Siga as convenções de código existentes no projeto.**
    *   **Se possível, inclua testes para novas funcionalidades ou correções.**

Antes de contribuir com alterações significativas, é recomendável abrir uma Issue para discutir a proposta ou melhoria primeiro. Isso garante que o trabalho esteja alinhado com os objetivos do projeto e evita esforços duplicados.

## Licença

[**MIT License**](LICENSE.md)  

Este projeto é licenciado sob a [MIT License](LICENSE.md) - veja o arquivo [LICENSE.md](LICENSE.md) para detalhes completos sobre os termos de uso, distribuição e modificação. A MIT License é uma licença permissiva que permite grande flexibilidade para usar, modificar e distribuir o código, tanto para uso pessoal quanto comercial.

## Contato

**Autor:** [Seu Nome Completo]

*   **GitHub:** [Gabriel Corrêa ](https://github.com/gabrielcorreabsb)  
*   **Email:** blogsrto@gmail.com 
*   **Linkedin:** https://linkedin.com/in/gabrielcorreabsb

Sinta-se à vontade para entrar em contato caso tenha dúvidas, sugestões ou precise de ajuda para utilizar os scripts.
