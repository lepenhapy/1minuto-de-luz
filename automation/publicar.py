"""Publicador estático semanal, sem serviços pagos nem dados pessoais."""
import datetime as dt
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "automation" / "pautas.json").read_text(encoding="utf-8"))
DEST = ROOT / "leituras"
DEST.mkdir(exist_ok=True)
published = sorted(DEST.glob("*.html"))
used = {p.stem for p in published}
entry = next((item for item in DATA if item["slug"] not in used), None)
if entry is None:
    print("Sem pautas inéditas; nenhuma publicação criada.")
    raise SystemExit(0)

esc = lambda value: html.escape(str(value), quote=True)
slug = entry["slug"]
if not re.fullmatch(r"[a-z0-9-]+", slug):
    raise ValueError("Slug inválido")
sections = "\n".join(
    f'<section class="item"><h2>{i}. {esc(title)}</h2><p>{esc(body)}</p></section>'
    for i, (title, body) in enumerate(entry["items"], 1)
)
images = {
    "Casa prática": "https://images.unsplash.com/photo-1556911220-bff31c812dba?w=1200&q=80",
    "Relacionamentos": "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=1200&q=80",
    "Curiosidades": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80",
}
image = images.get(entry["category"], images["Curiosidades"])
related = "".join(
    f'<a class="recommend" href="/leituras/{esc(other["slug"])}.html">{esc(other["title"])} →</a>'
    for other in DATA if other["slug"] != slug and (DEST / f'{other["slug"]}.html').exists()
)
page = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(entry["title"])} | 1 Minuto de Luz</title>
<meta name="description" content="{esc(entry["intro"])}">
<meta property="og:title" content="{esc(entry["title"])}">
<meta property="og:description" content="{esc(entry["intro"])}">
<meta property="og:image" content="{image}">
<link rel="stylesheet" href="/leituras/editorial.css"></head>
<body><header class="top"><nav class="nav"><a class="logo" href="/"><span>✳</span> 1 minuto de luz</a><div class="navlinks"><a href="/#achadinhos">Achadinhos</a><a href="/#historias">Histórias</a><a href="/#desafios">Desafios</a></div></nav></header>
<div class="stripe">UMA DESCOBERTA PUXA A OUTRA</div>
<div class="layout"><main class="article"><p class="tag">{esc(entry["category"])} · Leitura rápida</p>
<h1>{esc(entry["title"])}</h1><p class="lead">{esc(entry["intro"])}</p>
<img class="hero" src="{image}" alt="Imagem ilustrativa do tema {esc(entry["category"])}" loading="eager">
{sections}
<div class="next"><strong>Gostou desta descoberta?</strong><p>Continue explorando ideias úteis e histórias curiosas.</p><a href="/leituras/">Ver mais leituras →</a> · <a href="/#achadinhos">Explorar achadinhos →</a></div>
</main><aside class="aside"><h3>Você também vai gostar</h3>{related or '<a class="recommend" href="/#desafios">Você acerta as cinco perguntas? Faça o desafio →</a>'}<a class="recommend" href="/#achadinhos">Ideias úteis para sua casa →</a><p class="small">Conteúdo informativo. Imagens ilustrativas.</p></aside></div>
<footer class="footer">1 Minuto de Luz · <a href="/">Página inicial</a> · <a href="/privacidade.html">Privacidade</a></footer></body></html>"""
(DEST / f"{slug}.html").write_text(page, encoding="utf-8")
cards = []
for item in DATA:
    if (DEST / f'{item["slug"]}.html').exists():
        picture = images.get(item["category"], images["Curiosidades"])
        cards.append(f'<a class="card" href="./{esc(item["slug"])}.html"><img loading="lazy" src="{picture}" alt=""><div class="card-body"><span class="tag">{esc(item["category"])}</span><h2>{esc(item["title"])}</h2><span>Leia agora →</span></div></a>')
index = '<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Novas leituras | 1 Minuto de Luz</title><link rel="stylesheet" href="/leituras/editorial.css"><body><header class="top"><nav class="nav"><a class="logo" href="/">✳ 1 minuto de luz</a><div class="navlinks"><a href="/#achadinhos">Achadinhos</a><a href="/#desafios">Desafios</a></div></nav></header><div class="stripe">DESCUBRA ALGO NOVO</div><div class="layout"><main class="listing"><p class="tag">Histórias e descobertas</p><h1>Novas leituras</h1><p class="lead">Ideias úteis, curiosidades e relações humanas para explorar.</p><div class="cards">' + "".join(cards) + '</div></main><aside class="aside"><h3>Explore também</h3><a class="recommend" href="/#achadinhos">Achadinhos para casa →</a><a class="recommend" href="/#desafios">Desafios rápidos →</a></aside></div><footer class="footer">1 Minuto de Luz · <a href="/">Voltar ao início</a></footer></body></html>'
(DEST / "index.html").write_text(index, encoding="utf-8")

# Atualiza a vitrine de leituras da página inicial em cada nova publicação.
homepage = ROOT / "index.html"
start_marker = "<!-- LEITURAS_AUTO_INICIO -->"
end_marker = "<!-- LEITURAS_AUTO_FIM -->"
source = homepage.read_text(encoding="utf-8")
if start_marker not in source or end_marker not in source:
    raise RuntimeError("Marcadores de leituras ausentes na página inicial")
recent = [item for item in DATA if (DEST / f'{item["slug"]}.html').exists()][-6:]
recent.reverse()
highlights = "".join(
    f'<a href="/leituras/{esc(item["slug"])}.html"><span class="mini-tag">{esc(item["category"])}</span><strong>{esc(item["title"])}</strong><span>Leia agora →</span></a>'
    for item in recent
)
block = (
    '<section id="novas-leituras" class="section"><div class="section-heading"><div>'
    '<span class="kicker">CONTEÚDO NOVO</span><h2>Novas leituras</h2></div>'
    '<p>Descobertas práticas e curiosidades para explorar em poucos minutos.</p></div>'
    '<div class="more-stories">' + highlights + '</div>'
    '<p><a class="cta" href="/leituras/">Ver todas as leituras →</a></p></section>'
)
before, remainder = source.split(start_marker, 1)
_, after = remainder.split(end_marker, 1)
homepage.write_text(before + start_marker + "\n" + block + "\n" + end_marker + after, encoding="utf-8")

print(f"Publicado: {slug} ({dt.date.today().isoformat()})")
