"""Descarga mercados binarios ya resueltos de Polymarket y su historial diario de precios.

Uso: python3 mercados/descargar_polymarket.py [volumen_minimo_usd]
Genera: mercados/raw/polymarket.jsonl (un mercado por línea, con historial de precio del "Sí").
"""
import json
import os
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

GAMMA = "https://gamma-api.polymarket.com/markets/keyset?closed=true&limit=500&volume_num_min={}"
HIST = "https://clob.polymarket.com/prices-history?market={}&interval=max&fidelity=1440"
DESTINO = os.path.join(os.path.dirname(__file__), "raw", "polymarket.jsonl")


def get(url, intentos=4):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception:  # noqa: BLE001 - reintentar
            time.sleep(2 ** i)
    return None


def mercados(vol_min):
    cursor, revisados = None, 0
    while True:
        resp = get(GAMMA.format(vol_min) + (f"&after_cursor={cursor}" if cursor else ""))
        if not resp or not resp.get("markets"):
            return
        revisados += len(resp["markets"])
        for m in resp["markets"]:
            try:
                outcomes, precios = json.loads(m["outcomes"]), [float(x) for x in json.loads(m["outcomePrices"])]
                tokens = json.loads(m["clobTokenIds"])
            except (KeyError, TypeError, ValueError):
                continue
            if len(outcomes) != 2 or max(precios) < 0.99:
                continue  # solo binarios con resultado claro
            yield {"id": m["id"], "pregunta": m["question"], "slug": m.get("slug"), "volumen": m.get("volumeNum"),
                   "inicio": m.get("startDate"), "fin": m.get("closedTime") or m.get("endDate"),
                   "opciones": outcomes, "gana": precios.index(max(precios)), "token": tokens[0],
                   "categoria": m.get("category")}
        print(f"  {revisados:,} mercados revisados", flush=True)
        cursor = resp.get("next_cursor")
        if not cursor:
            return


def con_historial(m):
    h = get(HIST.format(m["token"]))
    m["historial"] = [(x["t"], x["p"]) for x in (h or {}).get("history", [])]
    return m


def main():
    vol_min = int(sys.argv[1]) if len(sys.argv) > 1 else 10000
    os.makedirs(os.path.dirname(DESTINO), exist_ok=True)
    lista = list(mercados(vol_min))
    print(f"Mercados binarios resueltos con volumen ≥ ${vol_min:,}: {len(lista):,}", flush=True)
    with ThreadPoolExecutor(8) as ex, open(DESTINO, "w") as f:
        for i, m in enumerate(ex.map(con_historial, lista)):
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
            if i % 2000 == 0:
                print(f"  historial {i:,}/{len(lista):,}", flush=True)
    print(f"Listo: {DESTINO}")


if __name__ == "__main__":
    main()
