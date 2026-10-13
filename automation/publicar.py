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
page = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(entry["title"])} | 1 Minuto de Luz</title>
<meta name="description" content="{esc(entry["intro"])}">
<style>body{{margin:0;background:#f7f7f4;color:#171c28;font:18px/1.7 system-ui,sans-serif}}header,main,footer{{max-width:760px;margin:auto;padding:24px}}header a,footer a{{color:#b83d24}}h1{{font-size:clamp(2rem,5vw,3.3rem);line-height:1.12}}h2{{font-size:1.35rem;line-height:1.3}}.item{{padding:20px 0;border-top:1px solid #ddd}}.tag{{color:#a63722;font-size:14px;font-weight:700;text-transform:uppercase}}a{{color:#a63722}}footer{{border-top:1px solid #ddd;font-size:14px}}</style></head>
<body><header><a href="/">✳ 1 minuto de luz</a></header>
<main><p class="tag">{esc(entry["category"])}</p><h1>{esc(entry["title"])}</h1>
<p>{esc(entry["intro"])}</p>{sections}
<p>Gostou da leitura? <a href="/#historias">Explore outras histórias</a> ou <a href="/#achadinhos">veja ideias para casa</a>.</p>
</main><footer>Conteúdo informativo e recreativo. <a href="/">Voltar ao início</a>.</footer></body></html>"""
(DEST / f"{slug}.html").write_text(page, encoding="utf-8")
cards = []
for item in DATA:
    if (DEST / f'{item["slug"]}.html').exists():
        cards.append(f'<li><a href="./{esc(item["slug"])}.html">{esc(item["title"])}</a> — {esc(item["category"])}</li>')
index = '<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Novas leituras | 1 Minuto de Luz</title><body style="font:18px/1.6 system-ui;max-width:740px;margin:50px auto;padding:20px"><a href="/">← 1 minuto de luz</a><h1>Novas leituras</h1><ul>' + "".join(cards) + '</ul></body></html>'
(DEST / "index.html").write_text(index, encoding="utf-8")
print(f"Publicado: {slug} ({dt.date.today().isoformat()})")
