import requests
import json
import pandas as pd
import os
import ast
from datetime import datetime
import numpy as np


#informe a sigla do Tribunal
sigla_Tribunal = 'tjap'

#Endpoints disponiveis em: https://datajud-wiki.cnj.jus.br/api-publica/endpoints
endpoint_Tribunal = f'https://api-publica.datajud.cnj.jus.br/api_publica_{sigla_Tribunal}/_search'

#APIKey atual disponivel em: https://datajud-wiki.cnj.jus.br/api-publica/acesso
APIKey = 'cDZHYzlZa0JadVREZDJCendQbXY6SkJlTzNjLV9TRENyQk1RdnFKZGRQdw=='

#Definicao do Acesso
headers = {
  'Authorization': f'ApiKey {APIKey}',
  'Content-Type': 'application/json'
}

# Define o número total de colunas para mostrar ao imprimir o dataframe
pd.set_option('display.max_columns', 100)

# Define um valor grande para a largura máxima da coluna
pd.set_option('display.max_colwidth', 200)

#Diretorio base para armazenar a planilha com as Classes parametrizadas obtidas no site do DataJUD
dir_CNJ = './CNJ'

arquivos = os.listdir(dir_CNJ)

if arquivos:
    for planilha in arquivos:
        if planilha.endswith(".xlsx"):
            #Pegando a tabela da Situações Datamart V7
            situacoesDM_v7 = pd.read_excel(f'{dir_CNJ}/{planilha}', sheet_name="Classes Datajud", skiprows=1)

else:
    print(f"Baixe a planilha contendo as classes parametrizadas disponivel em: https://www.cnj.jus.br/sistemas/datajud/parametrizacao/ para o diretório: {dir_CNJ}")
    exit(1)

#Filtra apenas as classes de conhecimento
classes_ConhecimentoDM = situacoesDM_v7[situacoesDM_v7["Grupo de Procedimento"] == 'Conhecimento'].copy()
classes_Conhecimento = str(list(classes_ConhecimentoDM['Código'].values))[1:-1]

#Apaga variaveis de supporte
del situacoesDM_v7
del classes_ConhecimentoDM

# Query DSL
pesquisa = ast.literal_eval(
'''{
    "size": 1000, 
    "query": { 
        "bool": { 
            "filter": { 
                "terms": { "classe.codigo" :  [ ''' + classes_Conhecimento + '''] } 
            } 
        } 
    }, 
    "sort": [{ "@timestamp" : {"order" : "asc" } }] 
}'''
)

dados_Body = json.dumps(pesquisa)

#submetendo a Query
response = requests.request("POST", endpoint_Tribunal, headers=headers, data=dados_Body)

#Resposta
procs_Json = json.loads(response.text)
hits = procs_Json.get('hits', {}).get('hits', [])

if not hits:
    print('Não existem Resultados para a consulta realizada')
    exit(1)

df_processos = pd.DataFrame.from_dict([document['_source'] for document in hits])


#Salva em arquivo local
with open('./dados/elastic_cache', 'a', encoding='utf8') as arquivo:       

    for hit in hits:
        arquivo.write(json.dumps(hit, ensure_ascii=False) + '\n')


while True:
            
    #Necessario para Paginacao
    ultimo_registro = str(hits[-1]['sort'])

    #Query DSL - Paginacao
    pesquisa = ast.literal_eval(
        '''{
            "size": 1000, 
            "query": { 
                "bool": { 
                    "filter": { 
                        "terms": { "classe.codigo" :  [ ''' + classes_Conhecimento + '''] } 
                    } 
                } 
            }, 
            "search_after": ''' + ultimo_registro + ''' ,
            "sort": [{ "@timestamp" : {"order" : "asc" } }] 
        }'''
    )

    dados_Body = json.dumps(pesquisa)
    
    #Nova Requisicao
    response = requests.request("POST", endpoint_Tribunal, headers=headers, data=dados_Body)

    #Nova Resposta
    procs_Json = json.loads(response.text)
    hits = procs_Json.get('hits', {}).get('hits', [])

    if not hits:
        print('Não existem mais registros')
        break

    else:
        df_pagina = pd.DataFrame.from_dict([document['_source'] for document in hits])
    
        #Concatena e reindexa em um novo dataFrame
        df_processos = pd.concat([df_processos, df_pagina ], ignore_index=True)

        print(f'Total de registros obtidos até o momento: {df_processos.shape[0]}')

        #Salva em arquivo local
    with open('./dados/elastic_cache', 'a', encoding='utf8') as arquivo:       

        for hit in hits:
            arquivo.write(json.dumps(hit, ensure_ascii=False) + '\n')    


#Tratamento pos carga de dados
df_tratado = df_processos[['classe','grau','numeroProcesso', 'dataAjuizamento', 'orgaoJulgador', 'assuntos']].copy()
del df_processos

#Extrai apenas o codigo das classes
df_tratado['classe'] = df_tratado['classe'].apply(lambda x: x['codigo'])

#Converte para datetime
df_tratado['dataAjuizamento'] = df_tratado['dataAjuizamento'].apply(lambda x: datetime.fromisoformat(x.replace('Z', '+00:00')).date())

#Extrai apenas o nome dos orgaos julgadores
df_tratado['orgaoJulgador'] = df_tratado['orgaoJulgador'].apply(lambda x: x['nome'])

#Extrai apenas o codigo dos assuntos
#df_tratado['assuntos'] = df_tratado['assuntos'].apply(lambda x: [assunto['codigo'] for assunto in x])
def obter_Assuntos(assuntos):
    try:
        for assunto in assuntos:
            return assunto['codigo']
    except:
        return 'Erros detectados'

#Funcao criada para contornar o erro depurado atraves do script: debugger.py    
df_tratado['assuntos'] = df_tratado['assuntos'].apply(obter_Assuntos)

#Removendo registros duplicados
df_tratado = df_tratado.drop_duplicates(subset=['classe', 'grau', 'numeroProcesso', 'orgaoJulgador'], keep= 'last').reset_index(drop = True)

#Criando a planilha em: ./dados/Procs_Conhecimento_{sigla_Tribunal}.xlsx
print(f'Criando a Planilha com dados processados em:  ./dados/Procs_Conhecimento_{sigla_Tribunal}.xlsx')
df_tratado.to_excel(f'./dados/Procs_Conhecimento_{sigla_Tribunal}.xlsx', index= False)