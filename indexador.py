# -*- coding: utf-8 -*-
import json
import string
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import RSLPStemmer # Stemmer para Português
import time
import os

def carregar_dados(filepath):
    """Carrega os dados JSON do arquivo especificado."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        print(f"Dados carregados de '{filepath}'. Total de {len(dados)} receitas.")
        return dados
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filepath}' não encontrado.")
        return None
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar JSON do arquivo '{filepath}'.")
        return None

def limpar_texto(texto):
    """Remove pontuação e converte para minúsculas."""
    if texto is None:
        return ""
    # Remove pontuação
    texto_sem_pontuacao = texto.translate(str.maketrans('', '', string.punctuation))
    # Converte para minúsculas
    texto_minusculo = texto_sem_pontuacao.lower()
    return texto_minusculo

def processar_documentos(documentos):
    """Aplica limpeza, tokenização, remoção de stopwords e stemming."""
    if not documentos:
        return {}

    stop_words = set(stopwords.words('portuguese'))
    stemmer = RSLPStemmer()
    # Alternativa: stemmer = nltk.stem.SnowballStemmer('portuguese')
    
    documentos_processados = {}
    campos_para_indexar = ['strMeal', 'strInstructions', 'strCategory', 'strArea'] 
    # Adicione 'strIngredientX' se quiser indexar ingredientes

    print("Iniciando processamento dos documentos...")
    count = 0
    for doc in documentos:
        doc_id = doc.get('idMeal')
        if not doc_id:
            continue # Pula receitas sem ID

        texto_combinado = ""
        for campo in campos_para_indexar:
            texto_combinado += limpar_texto(doc.get(campo, "")) + " " # Combina campos relevantes

        # Tokenização
        tokens = word_tokenize(texto_combinado, language='portuguese')
        
        # Remoção de stopwords e stemming
        tokens_processados = [
            stemmer.stem(token) 
            for token in tokens 
            if token.isalnum() and token not in stop_words # Mantém apenas alfanuméricos e remove stopwords
        ]
        
        documentos_processados[doc_id] = tokens_processados
        count += 1
        if count % 20 == 0:
            print(f"  Processados {count}/{len(documentos)} documentos...")

    print(f"Processamento concluído para {len(documentos_processados)} documentos.")
    return documentos_processados

def construir_indice_invertido(documentos_processados):
    """Constrói um índice invertido a partir dos documentos processados."""
    indice = {}
    print("Construindo índice invertido...")
    
    for doc_id, tokens in documentos_processados.items():
        for token in tokens:
            if token not in indice:
                indice[token] = []
            if doc_id not in indice[token]: # Evita IDs duplicados para o mesmo termo no mesmo doc
                 indice[token].append(doc_id)

    # Opcional: Ordenar a lista de documentos para cada termo (pode ajudar em algumas operações)
    # for token in indice:
    #     indice[token].sort()

    print(f"Índice invertido construído com {len(indice)} termos únicos.")
    return indice

def salvar_indice(indice, filepath):
    """Salva o índice invertido em um arquivo JSON."""
    print(f"Salvando índice em '{filepath}'...")
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(indice, f, indent=2, ensure_ascii=False)
        print("Índice salvo com sucesso!")
    except IOError as e:
        print(f"Erro ao salvar o índice '{filepath}': {e}")

# --- Execução Principal ---
if __name__ == "__main__":
    start_time = time.time()
    
    arquivo_dados = 'receitas_db.json'
    arquivo_indice = 'indice_invertido.json'
    
    # Verifica se o arquivo de índice já existe e se é mais novo que o de dados
    indice_existe = os.path.exists(arquivo_indice)
    dados_mod_time = os.path.getmtime(arquivo_dados) if os.path.exists(arquivo_dados) else 0
    indice_mod_time = os.path.getmtime(arquivo_indice) if indice_existe else 0

    if indice_existe and indice_mod_time > dados_mod_time:
        print(f"Arquivo de índice '{arquivo_indice}' já existe e está atualizado. Carregando...")
        try:
            with open(arquivo_indice, 'r', encoding='utf-8') as f:
                indice_invertido = json.load(f)
            print(f"Índice carregado com {len(indice_invertido)} termos.")
        except (IOError, json.JSONDecodeError) as e:
            print(f"Erro ao carregar índice pré-existente: {e}. Reconstruindo...")
            indice_invertido = None # Força reconstrução
    else:
        if indice_existe:
             print(f"Arquivo de dados '{arquivo_dados}' é mais recente que o índice. Reconstruindo índice...")
        else:
             print(f"Arquivo de índice '{arquivo_indice}' não encontrado. Construindo...")
        indice_invertido = None

    if indice_invertido is None:
        # Carregar dados
        receitas = carregar_dados(arquivo_dados)
        
        if receitas:
            # Processar documentos (limpeza, tokenização, stopwords, stemming)
            documentos_processados = processar_documentos(receitas)
            
            # Construir índice invertido
            indice_invertido = construir_indice_invertido(documentos_processados)
            
            # Salvar índice invertido
            salvar_indice(indice_invertido, arquivo_indice)
        else:
            print("Não foi possível carregar os dados. Saindo.")
            
    end_time = time.time()
    print(f"\nTempo total de execução: {end_time - start_time:.2f} segundos.")