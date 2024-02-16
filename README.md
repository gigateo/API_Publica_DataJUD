Script para Acessar a API Publica do DATAJUD e buscar todos os processos que tiverem o código da classe contida no grupo de procedimento:  "conhecimento", listados na planilha de classes parametrizadas do DATAJUD.

O script gerará a planilha: **./dados/Procs_Conhecimento_{sigla_Tribunal}.xlsx**

O script também gerará o arquivo: **./dados/elastic_cache** contendo todos os registros baixados (sem tratamento), permitindo estudos/depurações posteriores.


# Passo 1 
Obtenha a versão mais atualizada do arquivo: "Parametrização Classe - Todos os ramos", disponível em: https://www.cnj.jus.br/sistemas/datajud/parametrizacao/

Obs: No momento da criação desse script, a mais atualizada é a **_Versão 7.0 – divulgada em 9/1/2024_**

Mova o arquivo baixado para o diretorio: **./CNJ**

OBS: Deixe apenas UMA planilha contendo as classes parametrizadas no diretorio: **CNJ**

# Passo 2
Edite o arquivo: **app_pub_datajud.py** e coloque a sigla do tribunal que deseja obter os dados na variável: **sigla_Tribunal**

Ex: Para baixar os dados do Tribunal de justica do Amapa, basta colocar o conteudo: **'tjap'**

A lista completa de siglas está disponivel em: https://datajud-wiki.cnj.jus.br/api-publica/endpoints na coluna URL.

Neste exemplo usaremos o Tribunal de Justiça do Estado do Amapá, cuja URL é: https://api-publica.datajud.cnj.jus.br/api_publica_tjap/_search