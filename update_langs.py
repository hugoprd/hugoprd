import os
import requests
import re

TOKEN = os.getenv("GH_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"}

def get_repos():
    url = "https://api.github.com/user/repos?affiliation=owner,collaborator&per_page=100"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_languages():
    repos = get_repos()
    lang_stats = {}
    
    for repo in repos:
        langs_url = repo['languages_url']
        langs = requests.get(langs_url, headers=HEADERS).json()
        
        for lang, bytes_count in langs.items():
            if lang in lang_stats:
                lang_stats[lang] += bytes_count
            else:
                lang_stats[lang] = bytes_count
                
    return lang_stats

def generate_ascii_bar(percent, width=15):
    filled = int((percent / 100) * width)
    empty = width - filled
    return "█" * filled + "░" * empty

def update_readme(stats):
    total_bytes = sum(stats.values())
    
    # Ordena as linguagens da mais usada para a menos usada
    sorted_langs = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 1. Encontra o tamanho do maior nome para alinhar perfeitamente (ex: jupyter notebook tem 16)
    max_name_len = max(len(lang) for lang, _ in sorted_langs)
    
    # 3. Usa um div com fonte monospace em vez do <pre> para sumir com o fundo cinza
    graph_lines = ['<div align="center" style="font-family: monospace; white-space: nowrap;">']
    
    for lang, bytes_count in sorted_langs:
        percent = (bytes_count / total_bytes) * 100
        bar = generate_ascii_bar(percent)
        
        # 2. Deixa em minúsculo e preenche com espaços até igualar ao maior nome
        lang_name = lang.lower().ljust(max_name_len)
        
        # Monta a linha com dois espaços de respiro entre os elementos
        line = f"{lang_name}  {bar}  {percent:.1f}%"
        
        # Troca espaços normais por &nbsp; para o GitHub não ignorar o alinhamento e adiciona <br>
        line_safe = line.replace(" ", "&nbsp;")
        graph_lines.append(f"{line_safe}<br>")
        
    graph_lines.append("</div>")
    
    new_content = "\n".join(graph_lines)
    
    with open("README.md", "r") as file:
        readme = file.read()
        
    readme = re.sub(
        r"<!-- START_LANGS -->.*?<!-- END_LANGS -->",
        f"<!-- START_LANGS -->\n{new_content}\n<!-- END_LANGS -->",
        readme,
        flags=re.DOTALL
    )
    
    with open("README.md", "w") as file:
        file.write(readme)

if __name__ == "__main__":
    langs = get_languages()
    update_readme(langs)