# Script criado para debuggar o seguinte erro:
#
#  File "C:\Conhec_Api_Pub_DataJud\app_pub_datajud.py", line 156, in <listcomp>
#     df_tratado['assuntos'] = df_tratado['assuntos'].apply(lambda x: [assunto['codigo'] for assunto in x])
#                                                                      ~~~~~~~^^^^^^^^^^
# TypeError: list indices must be integers or slices, not str

import json
import pandas as pd
import os
import re


dados = []

# Ler o arquivo de texto e processar cada linha
with open('./dados/elastic_cache', 'r', encoding='utf8') as file:
    for line in file:
        # Converter cada linha para um dicionário
        linha_dict = json.loads(line)
        # Adicionar o dicionário à lista de dados
        dados.append(linha_dict)

# Recria o DataFrame
df = pd.DataFrame.from_dict([document['_source'] for document in dados])

df_tratado = df[['classe','grau','numeroProcesso', 'dataAjuizamento', 'orgaoJulgador', 'assuntos']].copy()
del df

def avaliar(assuntos):
    try:
        for assunto in assuntos:
            return assunto['codigo']
    except:
        return 'Tem erro'

df_tratado['assuntos'] = df_tratado['assuntos'].apply(lambda x: try: [assunto['codigo'] for assunto in x] except: 'Erros de formatacao')
df_tratado['assuntos_debug'] = df_tratado['assuntos'].apply(avaliar)

df_debug = df_tratado[df_tratado['assuntos_debug'] == 'Tem erro']

#gerando o arquivo para conferencia manual do conteudo de Assuntos
df_debug.to_csv('./dados/debugados', sep=';')