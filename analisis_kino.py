"""Análisis de aleatoriedad del Kino (14 de 25) y generador de combinaciones.

Uso: python3 analisis_kino.py [cantidad_de_combinaciones]
Datos: data/kino_historico.csv (generado por consolidar_kino.py). Solo era 14 de 25 (sorteo 799 en adelante).
"""
import csv
import random
import secrets
import sys
from collections import Counter

N, K = 25, 14
ARCHIVO = "data/kino_historico.csv"
SIMULACIONES = 2000


def cargar():
    sorteos = {}
    with open(ARCHIVO) as f:
        for fila in csv.DictReader(f):
            if fila["cantidad"] != str(K):
                continue
            nums = sorted(int(x) for x in fila["numeros"].split())
            if len(set(nums)) == K and all(1 <= x <= N for x in nums):
                sorteos[int(fila["sorteo"])] = nums
    return sorteos


def estadistico(conteos, n):
    esperado = n * K / N
    return sum((conteos.get(x, 0) - esperado) ** 2 / esperado for x in range(1, N + 1))


def main():
    sorteos = cargar()
    ids = sorted(sorteos)
    faltantes = sorted(set(range(ids[0], ids[-1] + 1)) - set(ids))
    n = len(ids)
    print(f"Sorteos válidos: {n} (del {ids[0]} al {ids[-1]})")
    print(f"Faltantes en ese rango: {len(faltantes)} -> {faltantes}\n")

    conteos = Counter(x for nums in sorteos.values() for x in nums)
    esperado = n * K / N
    print(f"Frecuencia por número (esperado al azar: {esperado:.0f})")
    for x, c in sorted(conteos.items(), key=lambda t: -t[1]):
        print(f"  {x:2d}: {c:4d}  ({c - esperado:+.0f})")

    # p-valor Monte Carlo: ¿la dispersión observada es rara para un sorteo justo?
    obs = estadistico(conteos, n)
    rng = random.Random(0)
    mayores = 0
    for _ in range(SIMULACIONES):
        sim = Counter(x for _ in range(n) for x in rng.sample(range(1, N + 1), K))
        mayores += estadistico(sim, n) >= obs
    p = (mayores + 1) / (SIMULACIONES + 1)
    print(f"\nPrueba de uniformidad: estadístico={obs:.1f}, p-valor={p:.3f}")
    print("=> " + ("Posible sesgo, revisar." if p < 0.01 else
                   "Sin evidencia de sesgo: los números calientes/fríos son azar."))

    cantidad = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print(f"\nCombinaciones al azar (todas tienen la misma probabilidad: 1 en 4.457.400):")
    for _ in range(cantidad):
        nums = sorted(secrets.SystemRandom().sample(range(1, N + 1), K))
        print("  " + " ".join(f"{x:02d}" for x in nums))


if __name__ == "__main__":
    main()
