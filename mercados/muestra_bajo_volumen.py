"""Descarga el historial de una muestra al azar de mercados con volumen $10k–50k (control de sesgo de selección).

Uso: python3 mercados/muestra_bajo_volumen.py [n]  -> mercados/raw/polymarket_bajo.jsonl
"""
import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
from descargar_polymarket import META, con_historial  # noqa: E402

DESTINO = os.path.join(os.path.dirname(__file__), "raw", "polymarket_bajo.jsonl")

n = int(sys.argv[1]) if len(sys.argv) > 1 else 15000
lista = [m for m in map(json.loads, open(META)) if 1e4 <= (m["volumen"] or 0) < 5e4]
random.Random(0).shuffle(lista)
with ThreadPoolExecutor(8) as ex, open(DESTINO, "w") as f:
    for i, m in enumerate(ex.map(con_historial, lista[:n]), 1):
        f.write(json.dumps(m, ensure_ascii=False) + "\n")
        if i % 5000 == 0:
            print(f"  {i:,}/{n:,}", flush=True)
print("Listo")
