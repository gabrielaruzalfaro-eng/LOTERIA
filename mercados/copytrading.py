"""¿Funciona copiar a los mejores traders de Polymarket? Prueba de persistencia con datos reales.

1. Toma una muestra de mercados binarios resueltos (jul-2024 a sep-2026, volumen $100k–3M).
2. Descarga sus operaciones (billetera, compra/venta, opción, precio, tamaño) desde data-api.polymarket.com.
3. Período de formación (mercados cerrados antes de CORTE): ranking de billeteras por ganancia.
4. Período de evaluación (después de CORTE): simula copiar cada COMPRA de las mejores billeteras con $1,
   pagando un recargo por entrar después que ellas (1¢ y 3¢). Compara con copiar a cualquiera al azar.
Uso: python3 mercados/copytrading.py [n_mercados]
"""
import json
import math
import os
import random
import sys
import time
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

RAW = os.path.join(os.path.dirname(__file__), "raw")
META = os.path.join(RAW, "polymarket_meta.jsonl")
TRADES = os.path.join(RAW, "copytrading_trades.jsonl")
CORTE = "2026-02-01"


def get(url, intentos=4):
    for i in range(intentos):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            return json.loads(urllib.request.urlopen(req, timeout=30).read())
        except Exception:  # noqa: BLE001 - reintentar
            time.sleep(2 ** i)
    return None


def muestra(n):
    cand = []
    for linea in open(META):
        m = json.loads(linea)
        fin = (m["fin"] or "")[:10]
        if ("2024-07-01" <= fin <= "2026-09-30" and 1e5 <= (m["volumen"] or 0) <= 3e6
                and "up or down" not in m["pregunta"].lower()):
            cand.append(m)
    random.Random(0).shuffle(cand)
    return cand[:n]


def operaciones(m):
    info = get(f"https://gamma-api.polymarket.com/markets/{m['id']}")
    if not info or not info.get("conditionId"):
        return None
    ops = []
    for offset in range(0, 10001, 1000):
        pag = get(f"https://data-api.polymarket.com/trades?market={info['conditionId']}&limit=1000&offset={offset}"
                  "&takerOnly=false")
        if not pag:
            break
        ops += [(t["proxyWallet"], t["side"], t["outcomeIndex"], t["price"], t["size"], t["timestamp"])
                for t in pag if t.get("outcomeIndex") in (0, 1)]
        if len(pag) < 1000:
            break
    return {"id": m["id"], "fin": m["fin"][:10], "gana": m["gana"], "pregunta": m["pregunta"], "ops": ops}


def descargar(n):
    hechos = {json.loads(x)["id"] for x in open(TRADES)} if os.path.exists(TRADES) else set()
    pendientes = [m for m in muestra(n) if m["id"] not in hechos]
    print(f"Mercados en muestra: {n:,} · ya descargados: {len(hechos):,} · pendientes: {len(pendientes):,}", flush=True)
    with ThreadPoolExecutor(12) as ex, open(TRADES, "a") as f:
        for i, r in enumerate(ex.map(operaciones, pendientes), 1):
            if r:
                f.write(json.dumps(r) + "\n")
            if i % 500 == 0:
                f.flush()
                print(f"  {i:,}/{len(pendientes):,}", flush=True)


def ganancia_op(lado, opcion, precio, tam, gana):
    """Ganancia en USDC de una operación si se mantiene hasta la resolución."""
    vale = 1.0 if opcion == gana else 0.0
    return tam * (vale - precio) if lado == "BUY" else tam * (precio - vale)


def roi_copia(compras, recargo):
    """ROI de apostar $1 en cada compra copiada, pagando precio + recargo."""
    g = [(vale / min(p + recargo, 0.999)) - 1 for p, vale in compras if 0.01 <= p <= 0.97]
    if len(g) < 30:
        return None, len(g), None
    media = sum(g) / len(g)
    de = math.sqrt(sum((x - media) ** 2 for x in g) / (len(g) - 1))
    return media, len(g), (media / (de / math.sqrt(len(g))) if de else 0.0)


def analizar():
    form = defaultdict(lambda: [0.0, 0.0, 0, set()])   # billetera -> [ganancia, gastado, n_ops, mercados]
    evalu = defaultdict(list)                          # billetera -> [(precio, vale)] compras en evaluación
    evalu_pnl = defaultdict(lambda: [0.0, 0.0])
    n_merc = [0, 0]
    for linea in open(TRADES):
        m = json.loads(linea)
        es_form = m["fin"] < CORTE
        n_merc[0 if es_form else 1] += 1
        for w, lado, op, p, tam, _ in m["ops"]:
            g = ganancia_op(lado, op, p, tam, m["gana"])
            if es_form:
                f = form[w]
                f[0] += g
                f[1] += tam * p if lado == "BUY" else tam * (1 - p)
                f[2] += 1
                f[3].add(m["id"])
            else:
                evalu_pnl[w][0] += g
                evalu_pnl[w][1] += tam * p if lado == "BUY" else tam * (1 - p)
                if lado == "BUY":
                    evalu[w].append((p, 1.0 if op == m["gana"] else 0.0))
    print(f"Mercados: formación {n_merc[0]:,} (antes de {CORTE}) · evaluación {n_merc[1]:,}")
    activos = {w: f for w, f in form.items() if len(f[3]) >= 5 and f[2] >= 20 and w in evalu}
    print(f"Billeteras activas en ambos períodos (≥5 mercados y ≥20 operaciones antes): {len(activos):,}\n")

    def grupo(nombre, billeteras):
        compras = [c for w in billeteras for c in evalu[w]]
        fila = [f"  {nombre:44s} {len(billeteras):5,} billeteras"]
        for rec in (0.0, 0.01, 0.03):
            r, n, t = roi_copia(compras, rec)
            fila.append(f"recargo {rec * 100:.0f}¢: " + (f"{r:+6.1%} (t={t:+.1f})" if r is not None else "  –"))
        pnl = sum(evalu_pnl[w][0] for w in billeteras)
        gasto = sum(evalu_pnl[w][1] for w in billeteras)
        fila.append(f"| ellas mismas ganaron {pnl / gasto:+.1%}" if gasto else "")
        print(" · ".join(fila))

    por_ganancia = sorted(activos, key=lambda w: -activos[w][0])
    por_roi = sorted((w for w in activos if activos[w][1] >= 1000), key=lambda w: -activos[w][0] / activos[w][1])
    print("Copiar cada compra con $1 en el período de evaluación:")
    grupo("Todas las billeteras activas", list(activos))
    for k in (10, 50, 200):
        grupo(f"Top {k} por ganancia total en formación", por_ganancia[:k])
    for k in (10, 50, 200):
        grupo(f"Top {k} por rentabilidad (gastaron ≥$1.000)", por_roi[:k])
    grupo("Peores 200 por ganancia en formación", por_ganancia[-200:])
    print("\n  Detalle top 10 por ganancia (copiando con recargo 1¢):")
    for w in por_ganancia[:10]:
        r, n, _ = roi_copia(evalu[w], 0.01)
        print(f"    {w[:10]}…  compras copiadas {len(evalu[w]):6,} · ROI " + (f"{r:+.1%}" if r is not None else "–"))
    sin_mayor = [w for w in por_ganancia[:10] if w != max(por_ganancia[:10], key=lambda x: len(evalu[x]))]
    grupo("Top 10 sin la billetera con más compras", sin_mayor)
    rng = random.Random(1)
    grupo("200 billeteras al azar", rng.sample(list(activos), min(200, len(activos))))

    # Persistencia: ¿la rentabilidad pasada predice la futura?
    pares = [(activos[w][0] / activos[w][1], evalu_pnl[w][0] / evalu_pnl[w][1])
             for w in activos if activos[w][1] >= 500 and evalu_pnl[w][1] >= 500]
    if len(pares) > 30:
        rx = {v: i for i, v in enumerate(sorted(x for x, _ in pares))}
        ry = {v: i for i, v in enumerate(sorted(y for _, y in pares))}
        n = len(pares)
        d2 = sum((rx[x] - ry[y]) ** 2 for x, y in pares)
        rho = 1 - 6 * d2 / (n * (n * n - 1))
        print(f"\nPersistencia: correlación de rangos entre rentabilidad antes y después = {rho:+.3f} "
              f"({n:,} billeteras con ≥$500 operados en cada período; 0 = ninguna, 1 = total)")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        descargar(int(sys.argv[1]))
    analizar()
