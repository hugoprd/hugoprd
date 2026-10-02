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
    sorted_langs = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Inicia a construção de uma tabela invisível
    graph_lines = ['<table align="center" style="border: none !important; background-color: transparent !important; border-collapse: collapse !important;">']
    
    for lang, bytes_count in sorted_langs:
        percent = (bytes_count / total_bytes) * 100
        bar = generate_ascii_bar(percent)
        lang_name = lang.lower()
        
        # Cria as linhas da tabela, separando as variáveis em colunas (td)
        graph_lines.append('  <tr style="border: none !important; background-color: transparent !important;">')
        # Coluna 1: Nome alinhado à direita
        graph_lines.append(f'    <td align="right" style="border: none !important; padding: 2px 12px 2px 0 !important; font-family: monospace; white-space: nowrap;">{lang_name}</td>')
        # Coluna 2: Barra ASCII
        graph_lines.append(f'    <td style="border: none !important; padding: 2px 12px 2px 0 !important; font-family: monospace; white-space: nowrap;">{bar}</td>')
        # Coluna 3: Porcentagem alinhada à direita
        graph_lines.append(f'    <td align="right" style="border: none !important; padding: 2px 0 2px 0 !important; font-family: monospace; white-space: nowrap;">{percent:.1f}%</td>')
        graph_lines.append('  </tr>')
        
    graph_lines.append("</table>")
    
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