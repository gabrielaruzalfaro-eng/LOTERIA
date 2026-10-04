"""Descarga sorteos del Kino y Loto desde chileresultados.com a data/raw/.

Uso: python3 descargar_chileresultados.py kino 3268 3275
     python3 descargar_chileresultados.py loto 4239 5484
Guarda: data/raw/chileresultados_<juego>.csv (sorteo, fecha, numeros, comodin). Agrega sin duplicar.
"""
import csv
import os
import re
import sys
import time
import urllib.request

MESES = {m: i for i, m in enumerate(["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
                                      "septiembre", "octubre", "noviembre", "diciembre"], 1)}
CANTIDAD = {"kino": 14, "loto": 6}


def descargar(juego, n):
    req = urllib.request.Request(f"https://chileresultados.com/{juego}/sorteos/{n}",
                                 headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    marca = "Sorteo KINO</b>" if juego == "kino" else 'class="shadow'
    bloque = html.split(marca, 1)[1] if marca in html else ""
    patron = r'badge rounded-pill bg-\w+(?: text-dark)?">(\d+)<' if juego == "kino" else r'badge rounded-pill bg-danger">(\d+)<'
    nums = [int(x) for x in re.findall(patron, bloque)][:CANTIDAD[juego]]
    if len(nums) < CANTIDAD[juego]:
        return None
    comodin = re.search(r'bg-warning text-danger">(\d+)<', bloque)
    m = re.search(r"(\d{1,2}) de (\w+) de (\d{4})", html)
    fecha = f"{m[3]}-{MESES[m[2].lower()]:02d}-{int(m[1]):02d}" if m and m[2].lower() in MESES else ""
    return [n, fecha, " ".join(map(str, sorted(nums))), comodin[1] if comodin and juego == "loto" else ""]


def main():
    juego, desde, hasta = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
    ruta = f"data/raw/chileresultados_{juego}.csv"
    filas = {}
    if os.path.exists(ruta):
        with open(ruta) as f:
            filas = {int(r[0]): r for r in list(csv.reader(f))[1:]}
    sin_datos = []
    for n in range(desde, hasta + 1):
        if n in filas:
            continue
        try:
            fila = descargar(juego, n)
        except Exception as e:  # noqa: BLE001 - registrar y seguir
            fila = None
            print(f"  {n}: error {e}")
        if fila:
            filas[n] = fila
        else:
            sin_datos.append(n)
        time.sleep(0.3)
    with open(ruta, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["sorteo", "fecha", "numeros", "comodin"])
        w.writerows(filas[k] for k in sorted(filas))
    print(f"{juego}: {len(filas)} sorteos en {ruta}; sin datos: {len(sin_datos)} {sin_datos[:30]}")


if __name__ == "__main__":
    main()
