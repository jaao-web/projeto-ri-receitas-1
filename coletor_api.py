# -*- coding: utf-8 -*-
import requests
import json
import string
import time

# URL base da API
BASE_URL = "https://www.themealdb.com/api/json/v1/1/search.php?f="

def coletar_dados():
    """
    Função principal para coletar todas as receitas da API TheMealDB,
    iterando por cada letra do alfabeto, usando requests.Session().
    """
    alfabeto = string.ascii_lowercase  # Gera uma string com 'abcdefghijklmnopqrstuvwxyz'
    todas_as_receitas = []
    
    # Usar uma sessão para otimizar conexões
    session = requests.Session() 

    print("Iniciando a coleta de dados da TheMealDB com Session...")

    # Itera sobre cada letra do alfabeto para buscar receitas
    for letra in alfabeto:
        url = f"{BASE_URL}{letra}"
        print(f"Buscando receitas que começam com a letra '{letra}'...")

        try:
            # Faz a requisição para a API usando a sessão
            response = session.get(url) 

            # Garante que a requisição foi bem-sucedida
            response.raise_for_status() 

            data = response.json()

            # A API retorna {'meals': null} se não encontrar nada
            if data.get('meals'):
                todas_as_receitas.extend(data['meals'])
                print(f"  > {len(data['meals'])} receitas encontradas para a letra '{letra}'.")
            else:
                print(f"  > Nenhuma receita encontrada para a letra '{letra}'.")

        except requests.exceptions.RequestException as e:
            print(f"  > Erro ao buscar dados para a letra '{letra}': {e}")
        
        # Política de Polidez: Pequena pausa entre requisições
        # time.sleep(0.5) # Pausa pode ser ajustada ou removida com Session, 
                        # mas manter uma pequena pode ser cortês.
                        # O script original tinha 1s, mantive por segurança.
        time.sleep(1) 

    print("\nColeta finalizada!")
    print(f"Total de receitas coletadas: {len(todas_as_receitas)}")

    # Salva os dados coletados em um arquivo JSON
    nome_arquivo = 'receitas_db.json' 
    # Usar o mesmo nome para sobrescrever o arquivo anterior com os dados coletados (se rodar novamente)
    print(f"Salvando os dados em '{nome_arquivo}'...")

    try:
        with open(nome_arquivo, 'w', encoding='utf-8') as f:
            # indent=2 para formatar o JSON de forma legível
            # ensure_ascii=False para garantir caracteres especiais (acentos, etc.) sejam salvos corretamente
            json.dump(todas_as_receitas, f, indent=2, ensure_ascii=False)
        print("Dados salvos com sucesso!")
    except IOError as e:
        print(f"Erro ao salvar o arquivo '{nome_arquivo}': {e}")


if __name__ == "__main__":
    coletar_dados()