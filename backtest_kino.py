"""Backtest: ¿algún método predice el Kino mejor que el azar?
Para cada sorteo, elige 14 números usando solo sorteos anteriores y cuenta aciertos.
Al azar se esperan 14*14/25 = 7,84 aciertos por sorteo.
"""
import csv
import random
from collections import Counter

sorteos = [list(map(int, r["numeros"].split())) for r in csv.DictReader(open("data/kino_historico.csv"))
           if r["cantidad"] == "14"]
rng = random.Random(1)


def calientes(prev, v):
    c = Counter(x for s in prev[-v:] for x in s)
    return sorted(range(1, 26), key=lambda x: (-c[x], x))[:14]


def frios(prev, v):
    c = Counter(x for s in prev[-v:] for x in s)
    return sorted(range(1, 26), key=lambda x: (c[x], x))[:14]


metodos = {
    "Azar": lambda p: rng.sample(range(1, 26), 14),
    "Calientes (últimos 20)": lambda p: calientes(p, 20),
    "Calientes (últimos 100)": lambda p: calientes(p, 100),
    "Calientes (toda la historia)": lambda p: calientes(p, len(p)),
    "Fríos (últimos 20)": lambda p: frios(p, 20),
    "Fríos (últimos 100)": lambda p: frios(p, 100),
    "Repetir último sorteo": lambda p: p[-1],
}
INICIO = 100
print(f"Sorteos evaluados: {len(sorteos) - INICIO}  (esperado al azar: 7,84 aciertos; 14 = premio mayor)")
for nombre, f in metodos.items():
    aciertos = [len(set(f(sorteos[:i])) & set(sorteos[i])) for i in range(INICIO, len(sorteos))]
    prom = sum(aciertos) / len(aciertos)
    print(f"  {nombre:30s} promedio {prom:.3f}   máx {max(aciertos)}   veces con 14: {aciertos.count(14)}")
