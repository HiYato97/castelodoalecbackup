import os
import json
import html
from pathlib import Path

BASE_DIR = Path(".").resolve()

# Dados do Autor e Links
NOME_AUTOR = "Alec"
BIO_AUTOR = "***Bem vindes ao meu castelo****"
LOCALIZACAO = "Brazil - Minas Gerais"
TWITTER_URL = "https://twitter.com/alelecleclec"
LINKTREE_URL = "https://linktr.ee/castelodoalec"

def encontrar_avatar_local():
    """ Procura por uma imagem de avatar/perfil na pasta raiz """
    extensoes = ['.png', '.jpg', '.jpeg', '.webp']
    for ext in extensoes:
        for foto in BASE_DIR.glob(f"*{ext}"):
            nome_lower = foto.name.lower()
            if any(k in nome_lower for k in ['avatar', 'profile', 'alec', 'perfil', 'thumb']):
                return foto.relative_to(BASE_DIR).as_posix()

    for ext in extensoes:
        fotos = list(BASE_DIR.glob(f"*{ext}"))
        if fotos:
            return fotos[0].relative_to(BASE_DIR).as_posix()

    return ""

def obter_metadados_serie(pasta_serie):
    """ Extrai o título real e informações do series.json ou manifest.json """
    titulo = pasta_serie.name
    genero = ""
    curtidas = 0

    caminho_series_json = pasta_serie / "series.json"
    if caminho_series_json.exists():
        try:
            with open(caminho_series_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "data" in data:
                    titulo = data["data"].get("title", titulo)
                    curtidas = data["data"].get("thumbsup_cnt", 0)
                    genre_data = data["data"].get("genre", {})
                    if genre_data:
                        genero = genre_data.get("name", "")
        except Exception:
            pass

    if titulo == pasta_serie.name:
        caminho_manifest = pasta_serie / "manifest.json"
        if caminho_manifest.exists():
            try:
                with open(caminho_manifest, "r", encoding="utf-8") as f:
                    manifest_data = json.load(f)
                    titulo = manifest_data.get("series_title", titulo)
            except Exception:
                pass

    titulo_limpo = html.unescape(titulo).strip()
    return titulo_limpo, genero, curtidas

def encontrar_capa_serie(pasta_serie):
    """
    1. Varre os arquivos diretamente na raiz da série procurando por qualquer
       imagem que comece com 'img_' (ignorando maiúsculas/minúsculas).
    2. Se não encontrar, faz o fallback para a primeira imagem de 'episodes'.
    """
    extensoes_validas = {'.jpg', '.jpeg', '.png', '.webp'}

    # Prioridade 1: Arquivos na raiz da pasta da série que comecem com "img_"
    try:
        for arquivo in pasta_serie.iterdir():
            if arquivo.is_file():
                nome_lower = arquivo.name.lower()
                ext_lower = arquivo.suffix.lower()
                if nome_lower.startswith("img_") and ext_lower in extensoes_validas:
                    return arquivo.relative_to(BASE_DIR).as_posix()
    except Exception:
        pass

    # Prioridade 2: Primeira imagem dentro da pasta episodes/
    pasta_episodes = pasta_serie / "episodes"
    if pasta_episodes.exists():
        for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.JPG', '*.PNG']:
            imagens = sorted(list(pasta_episodes.glob(f"**/{ext}")))
            if imagens:
                return imagens[0].relative_to(BASE_DIR).as_posix()

    return ""

def listar_series():
    series = []
    for item in BASE_DIR.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            html_files = list(item.glob("*_completo.html")) or list(item.glob("*.html"))
            if html_files:
                ficheiro_html = html_files[0]
                titulo_real, genero, curtidas = obter_metadados_serie(item)
                capa = encontrar_capa_serie(item)
                
                series.append({
                    "titulo": titulo_real,
                    "genero": genero,
                    "curtidas": curtidas,
                    "url": ficheiro_html.relative_to(BASE_DIR).as_posix(),
                    "capa": capa
                })
    return sorted(series, key=lambda x: x["titulo"])

def gerar_html_index():
    series = listar_series()
    total_series = len(series)
    avatar_path = encontrar_avatar_local()

    avatar_html = f'<img src="{avatar_path}" alt="{NOME_AUTOR}" class="avatar">' if avatar_path else f'<div class="avatar-placeholder">{NOME_AUTOR[0]}</div>'

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{NOME_AUTOR} | Tapas (Acervo Preservado)</title>
    <style>
        :root {{
            --bg-main: #0f0f10;
            --bg-card: #18181c;
            --text-primary: #ffffff;
            --text-secondary: #9999a1;
            --accent: #ffcc00;
            --border-color: #27272e;
        }}

        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}

        body {{
            background-color: var(--bg-main);
            color: var(--text-primary);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1100px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: 260px 1fr;
            gap: 40px;
        }}

        @media (max-width: 768px) {{
            .container {{
                grid-template-columns: 1fr;
            }}
        }}

        .sidebar {{
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
        }}

        .avatar {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            margin-bottom: 20px;
            border: 3px solid var(--border-color);
            background: #222;
        }}

        .avatar-placeholder {{
            width: 150px;
            height: 150px;
            border-radius: 50%;
            margin-bottom: 20px;
            border: 3px solid var(--border-color);
            background: #222;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            font-weight: bold;
            color: var(--accent);
        }}

        .author-name {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 8px;
        }}

        .author-meta {{
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 5px;
            justify-content: center;
        }}

        .support-btn {{
            background-color: #3b3b4f;
            color: #fff;
            text-decoration: none;
            padding: 10px 24px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.95rem;
            margin: 15px 0;
            display: inline-block;
            transition: background 0.2s;
        }}

        .support-btn:hover {{
            background-color: #4a4a63;
        }}

        .bio {{
            color: var(--text-secondary);
            font-size: 0.95rem;
            margin: 15px 0;
            line-height: 1.4;
        }}

        .social-links {{
            margin-top: 15px;
            display: flex;
            flex-direction: column;
            gap: 8px;
            width: 100%;
        }}

        .social-link {{
            color: var(--text-secondary);
            text-decoration: none;
            font-size: 0.95rem;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            padding: 8px;
            border-radius: 6px;
            background: var(--bg-card);
            transition: color 0.2s;
        }}

        .social-link:hover {{
            color: var(--text-primary);
        }}

        .main-content {{
            display: flex;
            flex-direction: column;
        }}

        .header-tabs {{
            display: flex;
            align-items: baseline;
            gap: 20px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px;
            margin-bottom: 25px;
        }}

        .header-tabs h2 {{
            font-size: 1.2rem;
            font-weight: 700;
            color: var(--text-primary);
            border-bottom: 2px solid var(--text-primary);
            padding-bottom: 10px;
            margin-bottom: -13px;
        }}

        .series-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
            gap: 20px;
        }}

        .series-card {{
            background: var(--bg-card);
            border-radius: 8px;
            overflow: hidden;
            text-decoration: none;
            color: inherit;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s, box-shadow 0.2s;
            border: 1px solid var(--border-color);
        }}

        .series-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        }}

        .card-thumb {{
            width: 100%;
            height: 180px;
            object-fit: cover;
            background: #25252b;
            display: block;
        }}

        .card-info {{
            padding: 12px;
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}

        .card-title {{
            font-size: 0.95rem;
            font-weight: 700;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}

        .card-author {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}

        .card-tag {{
            font-size: 0.75rem;
            color: var(--accent);
            margin-top: 2px;
        }}
    </style>
</head>
<body>

    <div class="container">
        <aside class="sidebar">
            {avatar_html}
            <h1 class="author-name">{NOME_AUTOR}</h1>
            <div class="author-meta">
                <span>📍 {LOCALIZACAO}</span>
            </div>

            <a href="{LINKTREE_URL}" target="_blank" class="support-btn">💬 Linktree / Suporte</a>

            <p class="bio">{BIO_AUTOR}</p>

            <div class="social-links">
                <a href="{TWITTER_URL}" target="_blank" class="social-link">
                    🐦 Twitter / X
                </a>
                <a href="{LINKTREE_URL}" target="_blank" class="social-link">
                    🔗 Linktree
                </a>
            </div>
        </aside>

        <main class="main-content">
            <div class="header-tabs">
                <h2>{total_series} Series</h2>
            </div>

            <div class="series-grid">
"""

    for item in series:
        thumb_html = f'<img src="{item["capa"]}" alt="{item["titulo"]}" class="card-thumb">' if item["capa"] else '<div class="card-thumb"></div>'
        tag_html = f'<div class="card-tag">{item["genero"]}</div>' if item["genero"] else ''
        
        html_content += f"""
                <a href="{item['url']}" class="series-card">
                    {thumb_html}
                    <div class="card-info">
                        <div class="card-title" title="{item['titulo']}">{item['titulo']}</div>
                        <div class="card-author">{NOME_AUTOR}</div>
                        {tag_html}
                    </div>
                </a>
"""

    html_content += """
            </div>
        </main>
    </div>

</body>
</html>
"""

    caminho_index = BASE_DIR / "index.html"
    with open(caminho_index, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✅ 'index.html' regerado com sucesso!")

if __name__ == "__main__":
    gerar_html_index()