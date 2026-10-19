"""Descobre pautas em RSS públicos; NÃO publica notícias sem revisão."""
import datetime as dt
import json
import pathlib
import re
import urllib.request
import xml.etree.ElementTree as ET
from html import unescape

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "automation" / "tendencias.json"
FEEDS = {
    "Brasil": "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml",
    "Mundo": "https://feeds.bbci.co.uk/portuguese/rss.xml",
    "Casa & decoração": "https://www.archdaily.com.br/br/rss",
}
now = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
existing = []
if OUT.exists():
    try:
        existing = json.loads(OUT.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        pass
by_url = {item["url"]: item for item in existing if item.get("url")}
for category, url in FEEDS.items():
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "1MinutoDeLuzEditorial/1.0"})
        with urllib.request.urlopen(req, timeout=15) as response:
            content = response.read(1024 * 1024)
        root = ET.fromstring(content)
        for node in root.findall(".//item")[:15]:
            title = unescape(" ".join((node.findtext("title") or "").split()))
            link = (node.findtext("link") or "").strip()
            if not title or not link.startswith("https://"):
                continue
            description = re.sub(r"<[^>]*>", " ", node.findtext("description") or "")
            description = unescape(" ".join(description.split()))[:360]
            if link not in by_url:
                by_url[link] = {
                    "titulo_original": title, "url": link, "editoria": category,
                    "resumo_fonte": description, "capturado_em": now,
                    "status": "sugestao_nao_verificada",
                }
    except (OSError, ET.ParseError, TimeoutError) as exc:
        print(f"Feed indisponível ({category}): {type(exc).__name__}")
result = sorted(by_url.values(), key=lambda x: x.get("capturado_em", ""), reverse=True)[:100]
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"{len(result)} sugestões; nenhuma notícia publicada automaticamente.")
