"""¿Se puede ganar dinero en Polymarket? Calibración de precios y backtest de estrategias simples.

Para cada mercado resuelto toma el precio del "Sí" N días antes del cierre y simula comprar $1.
Supone un costo de 1 centavo por contrato al comprar (diferencial compra/venta).
Uso: python3 mercados/analisis_polymarket.py
"""
import json
import os
from collections import defaultdict
from datetime import datetime

RUTA = os.path.join(os.path.dirname(__file__), "raw", "polymarket.jsonl")
COSTO = 0.01
HORIZONTES = (1, 7, 30)
TRAMOS = [0, .02, .05, .10, .20, .30, .40, .50, .60, .70, .80, .90, .95, .98, 1.0001]


def ts(texto):
    texto = texto.replace(" ", "T").replace("+00", "+00:00") if texto and "+00:00" not in texto else texto
    try:
        return datetime.fromisoformat(texto.replace("Z", "+00:00")).timestamp()
    except (AttributeError, ValueError):
        return None


def cargar():
    for linea in open(RUTA):
        m = json.loads(linea)
        fin = ts(m["fin"])
        if fin and len(m["historial"]) >= 3:
            m["fin_ts"] = fin
            m["si_gana"] = int(m["gana"] == 0)
            yield m


def precio_antes(m, dias):
    limite = m["fin_ts"] - dias * 86400
    previos = [p for t, p in m["historial"] if t <= limite]
    return previos[-1] if previos else None


def ganancia(precio_compra, gana):
    """Ganancia de apostar $1 comprando a precio_compra (+ costo)."""
    p = min(precio_compra + COSTO, 0.999)
    return (1 / p - 1) if gana else -1.0


def main():
    mercados = list(cargar())
    print(f"Mercados binarios resueltos con historial: {len(mercados):,}\n")

    for h in HORIZONTES:
        datos = [(precio_antes(m, h), m) for m in mercados]
        datos = [(p, m) for p, m in datos if p is not None and 0 < p < 1]
        print(f"=== {h} día(s) antes del cierre: {len(datos):,} mercados ===")
        print(" Precio del Sí   mercados   precio prom.   % que salió Sí   diferencia")
        for a, b in zip(TRAMOS, TRAMOS[1:]):
            sel = [(p, m["si_gana"]) for p, m in datos if a <= p < b]
            if len(sel) >= 30:
                pp = sum(p for p, _ in sel) / len(sel)
                fr = sum(g for _, g in sel) / len(sel)
                print(f"  {a:4.0%}–{min(b, 1):4.0%}   {len(sel):8,}   {pp:11.1%}   {fr:14.1%}   {fr - pp:+9.1%}")

        estrategias = {
            "Comprar Sí si cuesta ≤5¢ (batacazo)": lambda p, g: ganancia(p, g) if p <= .05 else None,
            "Comprar No si el Sí cuesta ≤5¢": lambda p, g: ganancia(1 - p, not g) if p <= .05 else None,
            "Comprar No si el Sí cuesta 5–15¢": lambda p, g: ganancia(1 - p, not g) if .05 < p <= .15 else None,
            "Comprar favorito 80–95¢": lambda p, g: (ganancia(p, g) if .80 <= p < .95 else
                                                     ganancia(1 - p, not g) if .05 < p <= .20 else None),
            "Comprar favorito ≥95¢": lambda p, g: (ganancia(p, g) if p >= .95 else
                                                   ganancia(1 - p, not g) if p <= .05 else None),
            "Comprar siempre el Sí": lambda p, g: ganancia(p, g),
        }
        print("\n Estrategia (apostando $1 por mercado)            apuestas      ROI")
        for nombre, f in estrategias.items():
            g = [x for x in (f(p, m["si_gana"]) for p, m in datos) if x is not None]
            if g:
                print(f"  {nombre:46s} {len(g):8,}   {sum(g) / len(g):+7.1%}")

        por_anio = defaultdict(list)
        for p, m in datos:
            if p <= .05:
                por_anio[datetime.fromtimestamp(m["fin_ts"]).year].append(ganancia(1 - p, not m["si_gana"]))
        print("  'Comprar No si el Sí ≤5¢' por año: " +
              " · ".join(f"{a}: {sum(g) / len(g):+.1%} ({len(g)})" for a, g in sorted(por_anio.items())))
        print()


if __name__ == "__main__":
    main()
