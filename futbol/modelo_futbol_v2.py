"""Modelo de fútbol mejorado: Elo + goles + tiros al arco + forma + descanso (gradient boosting).

Variables por equipo, calculadas solo con partidos anteriores (promedios móviles exponenciales):
goles a favor/en contra, tiros al arco a favor/en contra (solo ligas europeas), puntos de los
últimos 5 partidos, días de descanso y partidos jugados. Se entrena cada año con los 6 anteriores.
Además prueba si el modelo aporta información que el mercado no tiene: combina la probabilidad de
las casas con la del modelo y mide si mejora.
Uso: python3 futbol/modelo_futbol_v2.py
"""
import os
import sys
from collections import defaultdict, deque

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

sys.path.insert(0, os.path.dirname(__file__))
from modelo_futbol import NOMBRES, agregar_elo, cargar  # noqa: E402

ALFA = 0.15  # peso de cada partido nuevo en los promedios móviles


def agregar_variables(partidos):
    ew = defaultdict(lambda: [np.nan] * 4)  # goles a favor, en contra, tiros a favor, en contra
    puntos = defaultdict(lambda: deque(maxlen=5))
    ultimo, jugados = {}, defaultdict(int)
    for p in partidos:
        fila = [p["dif"] / 100]
        for lado, rival in (("h", "a"), ("a", "h")):
            k = (p["liga"], p[lado])
            descanso = (p["fecha"] - ultimo[k]).days if k in ultimo else np.nan
            forma = np.mean(puntos[k]) if puntos[k] else np.nan
            fila += ew[k] + [forma, min(descanso, 30), min(jugados[k], 100)]
        p["x"] = fila
        # actualizar después del partido
        for lado, gf, gc, tf, tc in (("h", p["gh"], p["ga"], *p["tiros"]), ("a", p["ga"], p["gh"], *p["tiros"][::-1])):
            k = (p["liga"], p[lado])
            for i, v in enumerate((gf, gc, tf, tc)):
                if v is not None:
                    o = ew[k][i]
                    ew[k][i] = v if np.isnan(o) else o + ALFA * (v - o)
            puntos[k].append(3 if gf > gc else (1 if gf == gc else 0))
            ultimo[k], jugados[k] = p["fecha"], jugados[k] + 1


def backtest(nombre, filas):
    print(f"\n{nombre}")
    for clave, etiqueta in (("odds", "cuota promedio"), ("mejor", "mejor cuota del mercado")):
        for umbral in (0.0, 0.05, 0.10):
            g = [((p[clave][i] - 1) if p["res"] == i else -1.0)
                 for p, prob in filas if p[clave] for i in range(3) if prob[i] * p[clave][i] - 1 > umbral]
            if g:
                print(f"  {etiqueta:24s} ventaja > {umbral:4.0%}: {len(g):7,} apuestas · ROI {np.mean(g):+.1%}")


def main():
    partidos = cargar()
    agregar_elo(partidos)
    agregar_variables(partidos)
    con_cuotas = [p for p in partidos if p["odds"]]
    anios = sorted({p["anio"] for p in con_cuotas})
    print(f"Partidos: {len(partidos):,} · con tiros al arco: {sum(p['tiros'][0] is not None for p in partidos):,}")

    oos = []  # (partido, prob_modelo) fuera de muestra
    for anio in anios[3:]:
        entren = [p for p in partidos if anio - 6 <= p["anio"] < anio]
        prueba = [p for p in con_cuotas if p["anio"] == anio]
        if not prueba or not entren:
            continue
        clf = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.05, max_leaf_nodes=15,
                                             l2_regularization=1.0, random_state=0)
        clf.fit(np.array([p["x"] for p in entren]), [p["res"] for p in entren])
        oos += list(zip(prueba, clf.predict_proba(np.array([p["x"] for p in prueba]))))

    reales = np.array([p["res"] for p, _ in oos])
    pm = np.array([pr for _, pr in oos])
    mk = np.array([(lambda v: v / v.sum())(np.array([1 / o for o in p["odds"]])) for p, _ in oos])
    print(f"Partidos evaluados (fuera de muestra): {len(oos):,}")
    print(f"  Modelo v2:        acierto {np.mean(pm.argmax(1) == reales):.1%} · log-loss {log_loss(reales, pm):.4f}")
    print(f"  Casas de apuesta: acierto {np.mean(mk.argmax(1) == reales):.1%} · log-loss {log_loss(reales, mk):.4f}")

    # ¿El modelo aporta algo que el mercado no sabe? Combinar ambos, entrenando con años previos.
    anio_oos = np.array([p["anio"] for p, _ in oos])
    comb = np.full_like(pm, np.nan)
    solo_mk = np.full_like(pm, np.nan)  # control: mercado recalibrado, sin modelo
    Z = np.hstack([np.log(mk), np.log(pm)])
    for anio in sorted(set(anio_oos)):
        tr, te = anio_oos < anio, anio_oos == anio
        if tr.sum() < 5000:
            continue
        comb[te] = LogisticRegression(max_iter=1000).fit(Z[tr], reales[tr]).predict_proba(Z[te])
        solo_mk[te] = LogisticRegression(max_iter=1000).fit(Z[tr, :3], reales[tr]).predict_proba(Z[te, :3])
    ok = ~np.isnan(comb[:, 0])
    print(f"\n¿El modelo agrega información al mercado? ({ok.sum():,} partidos)")
    print(f"  Solo mercado:     log-loss {log_loss(reales[ok], mk[ok]):.4f}")
    print(f"  Mercado recalibrado (control): log-loss {log_loss(reales[ok], solo_mk[ok]):.4f}")
    print(f"  Mercado + modelo: log-loss {log_loss(reales[ok], comb[ok]):.4f}")

    backtest("Apostando con el modelo v2:", oos)
    backtest("CONTROL sin modelo: probabilidad de las casas tal cual:", [(p, m) for (p, _), m in zip(oos, mk)])
    backtest("CONTROL sin modelo: mercado recalibrado:", [(p, c) for (p, _), c, o in zip(oos, solo_mk, ok) if o])
    backtest("Apostando con mercado + modelo:", [(p, c) for (p, _), c, o in zip(oos, comb, ok) if o])

    por_liga = defaultdict(list)
    for (p, _), c, o in zip(oos, comb, ok):
        if o and p["mejor"]:
            for i in range(3):
                if c[i] * p["mejor"][i] - 1 > 0.02:
                    por_liga[p["liga"]].append((p["mejor"][i] - 1) if p["res"] == i else -1.0)
    print("\nMercado + modelo, mejor cuota, ventaja > 2%, ligas con ≥100 apuestas:")
    for liga, g in sorted(por_liga.items(), key=lambda t: -np.mean(t[1])):
        if len(g) >= 100:
            print(f"  {NOMBRES.get(liga, liga):14s} {len(g):6,} apuestas · ROI {np.mean(g):+.1%}")


if __name__ == "__main__":
    main()
