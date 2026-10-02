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
    
    graph_lines = ["<pre>"]
    for lang, bytes_count in sorted_langs:
        percent = (bytes_count / total_bytes) * 100
        bar = generate_ascii_bar(percent)
        # Formata a string (ex: Python     ████░░░░░░░░░░░ 20.5%)
        graph_lines.append(f"{lang.ljust(12)} {bar} {percent:.1f}%")
    graph_lines.append("</pre>")
    
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