"""¿Se puede ganar dinero en Polymarket? Calibración y backtest de estrategias simples.

Toma el precio diario del "Sí" N días antes del cierre y simula apostar $1 por mercado.
Costo: diferencial de compra/venta de 1¢ y 2¢ por contrato (precio medio diario ≠ precio de compra real).
Robustez: resultados por mitad del período (antigua/reciente) y por volumen.
Uso: python3 mercados/analisis_polymarket.py
"""
import json
import math
import os
import re
from collections import defaultdict
from datetime import datetime

RUTA = os.path.join(os.path.dirname(__file__), "raw", "polymarket.jsonl")
TRAMOS = [0, .02, .05, .10, .20, .30, .40, .50, .60, .70, .80, .90, .95, .98, 1.0001]
CATEGORIAS = [
    ("cripto", r"bitcoin|btc|ethereum|\beth\b|solana|\bsol\b|xrp|crypto|price of|up or down"),
    ("deportes", r"\bvs\.?\b|\bnba\b|\bnfl\b|\bmlb\b|\bnhl\b|premier league|champions|win the .*(cup|game|match|series)|ufc|f1\b"),
    ("política", r"elect|trump|biden|harris|president|senate|congress|governor|prime minister|parliament|vote|party"),
]


def ts(texto):
    if not texto:
        return None
    t = texto.replace(" ", "T").replace("Z", "+00:00")
    if re.search(r"[+-]\d\d$", t):
        t += ":00"
    try:
        return datetime.fromisoformat(t).timestamp()
    except ValueError:
        return None


def categoria(pregunta):
    q = pregunta.lower()
    return next((c for c, patron in CATEGORIAS if re.search(patron, q)), "otros")


def cargar():
    for linea in open(RUTA):
        m = json.loads(linea)
        fin = ts(m["fin"])
        if fin and len(m["historial"]) >= 3:
            m["fin_ts"], m["si"] = fin, int(m["gana"] == 0)
            m["cat"] = categoria(m["pregunta"])
            yield m


def precio(m, dias):
    limite = m["fin_ts"] - dias * 86400
    previos = [p for t, p in m["historial"] if t <= limite]
    return previos[-1] if previos and 0 < previos[-1] < 1 else None


def pago(p_compra, gana, costo):
    p = min(p_compra + costo, 0.999)
    return (1 / p - 1) if gana else -1.0


def resumen(nombre, ops):
    """ops: lista de (ganancia, mercado). Imprime ROI con error estándar y robustez."""
    if len(ops) < 30:
        return
    g = [x for x, _ in ops]
    media = sum(g) / len(g)
    de = math.sqrt(sum((x - media) ** 2 for x in g) / (len(g) - 1))
    t = media / (de / math.sqrt(len(g))) if de else 0
    orden = sorted(ops, key=lambda o: o[1]["fin_ts"])
    mitad = len(orden) // 2
    a = sum(x for x, _ in orden[:mitad]) / mitad
    b = sum(x for x, _ in orden[mitad:]) / (len(orden) - mitad)
    peor = min(g)
    print(f"  {nombre:52s} {len(g):7,} ops · ROI {media:+6.1%} (t={t:+5.1f}) · 1ª mitad {a:+6.1%} · "
          f"2ª mitad {b:+6.1%}")


def main():
    mercados = list(cargar())
    print(f"Mercados binarios resueltos con historial: {len(mercados):,}")
    print("Por categoría: " + " · ".join(f"{c}: {sum(m['cat'] == c for m in mercados):,}"
                                         for c in ("política", "deportes", "cripto", "otros")))

    for h in (1, 7, 30):
        datos = [(precio(m, h), m) for m in mercados]
        datos = [(p, m) for p, m in datos if p is not None]
        print(f"\n=== Calibración {h} día(s) antes del cierre ({len(datos):,} mercados) ===")
        print("  Precio Sí    mercados   precio prom.   salió Sí   diferencia")
        for a, b in zip(TRAMOS, TRAMOS[1:]):
            sel = [(p, m["si"]) for p, m in datos if a <= p < b]
            if len(sel) >= 50:
                pp, fr = sum(p for p, _ in sel) / len(sel), sum(s for _, s in sel) / len(sel)
                print(f"  {a:4.0%}–{min(b, 1):4.0%}  {len(sel):9,}   {pp:11.1%}   {fr:8.1%}   {fr - pp:+9.1%}")

    for costo in (0.01, 0.02):
        print(f"\n######## Estrategias con costo de {costo * 100:.0f}¢ por contrato ########")
        for h in (7, 30):
            datos = [(precio(m, h), m) for m in mercados]
            datos = [(p, m) for p, m in datos if p is not None]
            print(f"\n--- Idea 1: comprar No si el Sí cuesta 1–10%, {h} días antes ---")
            base = [(pago(1 - p, not m["si"], costo), m) for p, m in datos if .01 <= p <= .10]
            resumen("Todos", base)
            for nombre, lo, hi in (("Volumen $50k–200k", 5e4, 2e5), ("Volumen $200k–1M", 2e5, 1e6),
                                   ("Volumen > $1M", 1e6, 1e18)):
                resumen(nombre, [o for o in base if lo <= (o[1]["volumen"] or 0) < hi])
            for c in ("política", "deportes", "cripto", "otros"):
                resumen(f"Categoría {c}", [o for o in base if o[1]["cat"] == c])

        print("\n--- Idea 2: comprar No tras una subida fuerte del Sí (reversión) ---")
        for h, sube in ((7, .15), (7, .25), (30, .15), (30, .25)):
            ops = []
            for m in mercados:
                ahora, antes = precio(m, h), precio(m, h + 30)
                if ahora and antes and .15 <= ahora <= .85 and ahora - antes >= sube:
                    ops.append((pago(1 - ahora, not m["si"], costo), m))
            resumen(f"Sí subió ≥{sube:.0%} en 30 días, entrar {h} días antes", ops)
            resumen(f"   solo política y deportes", [o for o in ops if o[1]["cat"] in ("política", "deportes")])

        print("\n--- Idea 3: comprar el favorito a 95–99% ---")
        for h in (1, 7):
            ops = []
            for m in mercados:
                p = precio(m, h)
                if p and .95 <= p <= .99:
                    ops.append((pago(p, m["si"], costo), m))
                elif p and .01 <= p <= .05:
                    ops.append((pago(1 - p, not m["si"], costo), m))
            resumen(f"Favorito 95–99%, {h} días antes", ops)
            if ops:
                perdidas = sum(1 for g, _ in ops if g < 0)
                print(f"     (falla el favorito en {perdidas:,} de {len(ops):,} = {perdidas / len(ops):.1%}; "
                      f"cada falla pierde todo lo apostado)")


if __name__ == "__main__":
    main()
