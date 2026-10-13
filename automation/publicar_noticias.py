"""Publica noticias recentes somente com pauta revisada e fonte rastreavel."""
import datetime as dt
import html
import json
import pathlib
import re
from urllib.parse import urlparse

ROOT = pathlib.Path(__file__).resolve().parents[1]
QUEUE = ROOT / "automation" / "noticias.json"
items = json.loads(QUEUE.read_text(encoding="utf-8"))
today = dt.datetime.now(dt.timezone.utc).date()
dest = ROOT / "leituras"
dest.mkdir(exist_ok=True)
created = []
for item in items:
    slug = item["slug"]
    if not re.fullmatch(r"[a-z0-9-]+", slug):
        raise ValueError("Slug invalido")
    if (dest / (slug + ".html")).exists():
        continue
    if not item.get("revisado"):
        continue
    published = dt.date.fromisoformat(item["data"])
    if not 0 <= (today - published).days <= 2:
        continue
    sources = item.get("fontes", [])
    if not sources or not item.get("paragrafos") or len(item["paragrafos"]) < 2:
        raise ValueError("Noticia sem fontes ou texto suficiente: " + slug)
    if any(urlparse(u).scheme != "https" or not urlparse(u).netloc for u in sources):
        raise ValueError("Fonte invalida: " + slug)
    e = lambda s: html.escape(str(s), quote=True)
    paragraphs = "".join('<section class="story-paragraph"><p>' + e(p) + "</p></section>" for p in item["paragrafos"])
    links = "".join('<li><a href="' + e(u) + '" rel="noopener noreferrer" target="_blank">' + e(urlparse(u).netloc) + "</a></li>" for u in sources)
    image = item.get("imagem", "")
    if image and not (image.startswith("https://") or image.startswith("/")):
        raise ValueError("Imagem invalida")
    img = ('<img class="hero" src="' + e(image) + '" alt="' + e(item.get("imagem_alt", "Imagem editorial")) + '">' ) if image else ""
    page = f"""<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(item["titulo"])} | 1 Minuto de Luz</title><meta name="description" content="{e(item["resumo"])}"><link rel="stylesheet" href="/leituras/editorial.css"></head><body><header class="top"><nav class="nav"><a class="logo" href="/">✳ 1 minuto de luz</a><a href="/leituras/">Mais leituras</a></nav></header><div class="stripe">FAMOSOS E ATUALIDADES · INFORMAÇÃO VERIFICADA</div><div class="layout"><main class="article"><p class="tag">Entretenimento · {e(item["data"])}</p><h1>{e(item["titulo"])}</h1><p class="lead">{e(item["resumo"])}</p>{img}{paragraphs}<div class="next"><strong>Fontes consultadas</strong><ul>{links}</ul><p class="small">Informações verificadas na data indicada. Notícias podem evoluir.</p></div><a href="/leituras/">Outras descobertas →</a></main><aside class="aside"><h3>Continue explorando</h3><a class="recommend" href="/#desafios">Um desafio de 1 minuto →</a><a class="recommend" href="/leituras/">Mais matérias →</a></aside></div></body></html>"""
    (dest / (slug + ".html")).write_text(page, encoding="utf-8")
    created.append(item)
if created:
    home = ROOT / "index.html"
    source = home.read_text(encoding="utf-8")
    start, end = "<!-- NOTICIAS_AUTO_INICIO -->", "<!-- NOTICIAS_AUTO_FIM -->"
    cards = "".join('<a href="/leituras/' + html.escape(i["slug"]) + '.html"><span class="mini-tag">AGORA · ENTRETENIMENTO</span><strong>' + html.escape(i["titulo"]) + '</strong><span>Ler notícia →</span></a>' for i in reversed(items) if (dest / (i["slug"] + ".html")).exists())
    block = '<section class="section" id="noticias"><div class="section-heading"><div><span class="kicker">EM DESTAQUE</span><h2>Famosos e atualidades</h2></div><p>Notícias verificadas e histórias que estão dando o que falar.</p></div><div class="more-stories">' + cards + '</div></section>'
    if start in source and end in source:
        before, rest = source.split(start, 1)
        _, after = rest.split(end, 1)
        source = before + start + "\n" + block + "\n" + end + after
    else:
        source = source.replace('<section id="desafios"', start + "\n" + block + "\n" + end + "\n<section id="desafios"', 1)
    home.write_text(source, encoding="utf-8")
    print("Noticias publicadas:", ", ".join(i["slug"] for i in created))
else:
    print("Sem noticias revisadas, atuais e ineditas. Nenhuma alteracao.")
