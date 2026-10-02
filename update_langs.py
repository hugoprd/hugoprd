import os
import requests

TOKEN = os.getenv("GH_TOKEN")
HEADERS = {"Authorization": f"token {TOKEN}"} if TOKEN else {}

def get_repos():
    url = "https://api.github.com/user/repos?affiliation=owner,collaborator&per_page=100"
    response = requests.get(url, headers=HEADERS)
    return response.json()

def get_languages():
    repos = get_repos()
    lang_stats = {}
    
    for repo in repos:
        if 'languages_url' not in repo:
            continue
        langs_url = repo['languages_url']
        langs = requests.get(langs_url, headers=HEADERS).json()
        
        for lang, bytes_count in langs.items():
            lang_stats[lang] = lang_stats.get(lang, 0) + bytes_count
                
    return lang_stats

def generate_ascii_bar(percent, width=15):
    filled = int((percent / 100) * width)
    empty = width - filled
    return "█" * filled + "░" * empty

def create_svg(stats):
    total_bytes = sum(stats.values())
    sorted_langs = sorted(stats.items(), key=lambda x: x[1], reverse=True)[:5]
    
    max_name_len = max(len(lang) for lang, _ in sorted_langs)
    
    svg_lines = []
    y_pos = 25
    
    for lang, bytes_count in sorted_langs:
        percent = (bytes_count / total_bytes) * 100
        bar = generate_ascii_bar(percent)
        lang_name = lang.lower().rjust(max_name_len)
        
        line_text = f"{lang_name}  {bar}  {percent:.1f}%"
        svg_lines.append(f'    <text x="0" y="{y_pos}" class="text" xml:space="preserve">{line_text}</text>')
        y_pos += 28
        
    svg_content = f"""<svg width="720" height="{y_pos}" xmlns="http://www.w3.org/2000/svg">
        <style>
            @import url('https://fonts.googleapis.com/css2?family=VT323&amp;display=swap');
            .text {{ 
                font-family: 'VT323', monospace; 
                font-size: 24px; 
            }}
            @media (prefers-color-scheme: dark) {{
            .text {{ fill: #c9d1d9; }}
            }}
            @media (prefers-color-scheme: light) {{
            .text {{ fill: #24292f; }}
            }}
        </style>
        {chr(10).join(svg_lines)}
        </svg>"""
    
    with open("langs_stats.svg", "w", encoding="utf-8") as file:
        file.write(svg_content)

if __name__ == "__main__":
    langs = get_languages()
    if langs:
        create_svg(langs)