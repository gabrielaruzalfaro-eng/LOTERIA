"""Modelo de predicción de fútbol (Elo + regresión logística) y backtest de apuestas contra las cuotas.

1. Carga todos los partidos con cuotas 1X2 (football-data.co.uk + Chile desde betexplorer).
2. Calcula un rating Elo por equipo, actualizado partido a partido (solo usa información previa).
3. Cada temporada, entrena una regresión logística (diferencia de Elo -> local/empate/visita) con las
   temporadas anteriores y predice la temporada siguiente.
4. Apuesta $1 cuando el modelo ve valor: prob_modelo * cuota - 1 > umbral. Mide la ganancia (ROI).
Uso: python3 futbol/modelo_futbol.py
"""
import csv
import glob
import os
from collections import defaultdict
from datetime import datetime

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss

RAW = os.path.join(os.path.dirname(__file__), "raw")
NOMBRES = {"E0": "Inglaterra 1", "E1": "Inglaterra 2", "E2": "Inglaterra 3", "E3": "Inglaterra 4",
           "EC": "Inglaterra 5", "SC0": "Escocia 1", "SC1": "Escocia 2", "SC2": "Escocia 3", "SC3": "Escocia 4",
           "D1": "Alemania 1", "D2": "Alemania 2", "I1": "Italia 1", "I2": "Italia 2", "SP1": "España 1",
           "SP2": "España 2", "F1": "Francia 1", "F2": "Francia 2", "N1": "Holanda", "B1": "Bélgica",
           "P1": "Portugal", "T1": "Turquía", "G1": "Grecia", "CHILE": "Chile"}


def num(x):
    try:
        v = float(x)
        return v if v > 1 else None
    except (TypeError, ValueError):
        return None


def fecha(t):
    for f in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
        try:
            return datetime.strptime(t.strip(), f).date()
        except ValueError:
            pass
    return None


def cargar():
    partidos = []
    for ruta in glob.glob(os.path.join(RAW, "*.csv")):
        base = os.path.basename(ruta)[:-4]
        liga = base.split("_")[0]
        with open(ruta, encoding="latin-1") as f:
            for r in csv.DictReader(f):
                r = {k.strip().lstrip("﻿").lstrip("ï»¿"): v for k, v in r.items() if k}
                if liga == "CHILE":
                    d, h, a, hg, ag = fecha(r["fecha"]), r["local"], r["visita"], r["gl"], r["gv"]
                    odds = [num(r["cuota_l"]), num(r["cuota_e"]), num(r["cuota_v"])]
                    mejor = None
                    tiros = (None, None)
                    temp = r["temporada"]
                elif "HomeTeam" in r or "Home" in r:
                    d = fecha(r.get("Date", ""))
                    h, a = r.get("HomeTeam") or r.get("Home"), r.get("AwayTeam") or r.get("Away")
                    hg, ag = r.get("FTHG") or r.get("HG"), r.get("FTAG") or r.get("AG")
                    odds = None
                    for p in ("Avg", "BbAv", "AvgC", "B365", "B365C", "BW", "IW", "WH"):
                        o = [num(r.get(p + s)) for s in "HDA"]
                        if all(o):
                            odds = o
                            break
                    mejor = None
                    for p in ("Max", "BbMx", "MaxC"):
                        o = [num(r.get(p + s)) for s in "HDA"]
                        if all(o):
                            mejor = o
                            break
                    hst, ast = r.get("HST", ""), r.get("AST", "")
                    tiros = (int(hst), int(ast)) if hst.strip().isdigit() and ast.strip().isdigit() else (None, None)
                    temp = base.split("_")[1] if "_" in base else (r.get("Season") or "")
                    liga = liga if "_" in base else (r.get("Country") or liga)
                else:
                    continue
                if not (d and h and a and hg and ag and hg.strip().isdigit() and ag.strip().isdigit()):
                    continue
                # Año de inicio de la temporada: "0506" -> 2005, "2014/2015" -> 2014, "2023" -> 2023
                anio = 2000 + int(temp[:2]) if "_" in base else int(str(temp)[:4] or d.year)
                res = 0 if int(hg) > int(ag) else (1 if hg == ag else 2)
                partidos.append({"liga": liga, "anio": anio, "fecha": d, "h": h, "a": a,
                                 "gd": int(hg) - int(ag), "gh": int(hg), "ga": int(ag),
                                 "tiros": tiros, "res": res, "odds": odds if odds and all(odds) else None,
                                 "mejor": mejor})
    partidos.sort(key=lambda p: (p["fecha"], p["liga"]))
    return partidos


def agregar_elo(partidos, k=20, ventaja=60):
    elo = defaultdict(lambda: 1500.0)
    for p in partidos:
        kh, ka = (p["liga"], p["h"]), (p["liga"], p["a"])
        p["dif"] = elo[kh] + ventaja - elo[ka]
        esperado = 1 / (1 + 10 ** (-p["dif"] / 400))
        real = 1.0 if p["gd"] > 0 else (0.5 if p["gd"] == 0 else 0.0)
        cambio = k * np.log1p(abs(p["gd"]) or 1) * (real - esperado)
        elo[kh] += cambio
        elo[ka] -= cambio


def main():
    partidos = cargar()
    agregar_elo(partidos)
    con_cuotas = [p for p in partidos if p["odds"]]
    print(f"Partidos: {len(partidos):,} · con cuotas: {len(con_cuotas):,} · ligas: {len({p['liga'] for p in partidos})}")

    anios = sorted({p["anio"] for p in con_cuotas})
    apuestas = []  # (liga, anio, ganancia, ev)
    mejores = []   # (ganancia, ev) usando la mejor cuota del mercado
    probs_modelo, probs_mercado, reales = [], [], []
    for anio in anios[3:]:
        entren = [p for p in partidos if p["anio"] < anio and p["anio"] >= anio - 6]
        prueba = [p for p in con_cuotas if p["anio"] == anio]
        if not prueba:
            continue
        X = np.array([[p["dif"] / 100] for p in entren])
        clf = LogisticRegression(max_iter=1000).fit(X, [p["res"] for p in entren])
        P = clf.predict_proba(np.array([[p["dif"] / 100] for p in prueba]))
        for p, prob in zip(prueba, P):
            imp = np.array([1 / o for o in p["odds"]])
            probs_modelo.append(prob)
            probs_mercado.append(imp / imp.sum())
            reales.append(p["res"])
            for i in range(3):
                ev = prob[i] * p["odds"][i] - 1
                apuestas.append((p["liga"], anio, (p["odds"][i] - 1) if p["res"] == i else -1.0, ev))
                if p["mejor"]:
                    evm = prob[i] * p["mejor"][i] - 1
                    mejores.append(((p["mejor"][i] - 1) if p["res"] == i else -1.0, evm))

    reales = np.array(reales)
    acierto = lambda P: np.mean(np.argmax(P, 1) == reales)  # noqa: E731
    print(f"\nPartidos evaluados (fuera de muestra): {len(reales):,}")
    print(f"  Modelo Elo:      acierto {acierto(np.array(probs_modelo)):.1%} · log-loss {log_loss(reales, probs_modelo):.4f}")
    print(f"  Casas de apuesta: acierto {acierto(np.array(probs_mercado)):.1%} · log-loss {log_loss(reales, probs_mercado):.4f}")
    print("  (log-loss más bajo = mejores probabilidades)")

    print("\nBacktest apostando $1 cuando el modelo ve valor:")
    for umbral in (0.0, 0.05, 0.10, 0.20):
        sel = [g for _, _, g, ev in apuestas if ev > umbral]
        if sel:
            print(f"  ventaja estimada > {umbral:.0%}: {len(sel):6,} apuestas · ROI {np.mean(sel):+.1%}")
    print("Con la MEJOR cuota entre todas las casas (requiere cuentas en muchas casas):")
    for umbral in (0.0, 0.05, 0.10, 0.20):
        sel = [g for g, ev in mejores if ev > umbral]
        if sel:
            print(f"  ventaja estimada > {umbral:.0%}: {len(sel):6,} apuestas · ROI {np.mean(sel):+.1%}")
    todas = [g for _, _, g, _ in apuestas]
    print(f"  Apostar a todo:            {len(todas):6,} apuestas · ROI {np.mean(todas):+.1%}")

    print("\nROI por liga (ventaja estimada > 5%):")
    por_liga = defaultdict(list)
    for liga, _, g, ev in apuestas:
        if ev > 0.05:
            por_liga[liga].append(g)
    for liga, gs in sorted(por_liga.items(), key=lambda t: -np.mean(t[1])):
        if len(gs) >= 200:
            print(f"  {NOMBRES.get(liga, liga):14s} {len(gs):6,} apuestas · ROI {np.mean(gs):+.1%}")


if __name__ == "__main__":
    main()
