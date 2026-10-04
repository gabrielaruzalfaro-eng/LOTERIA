"""Descarga resultados (2005+) y cuotas promedio 1X2 (2020+) de la Primera División de Chile desde betexplorer.com.

Uso: python3 futbol/descargar_chile.py
Genera: futbol/raw/CHILE.csv (temporada, fecha, local, visita, goles, cuotas H/D/A).
"""
import csv
import html
import os
import re
import time
import urllib.request

URL = "https://www.betexplorer.com/football/chile/{}/results/"
FILA = re.compile(r'<tr><td class="h-text-left"><a[^>]*class="in-match"><span>(.*?)</span> - <span>(.*?)</span></a>'
                  r'</td><td class="h-text-center"><a[^>]*>(\d+):(\d+)(?:[^<]*)</a></td>(.*?)'
                  r'<td class="h-text-right h-text-no-wrap">([^<]*)</td></tr>', re.S)


def limpiar(t):
    return html.unescape(re.sub(r"<[^>]+>", "", t)).strip()


def temporada(nombre, anio):
    req = urllib.request.Request(URL.format(nombre), headers={"User-Agent": "Mozilla/5.0"})
    try:
        pagina = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")
    except Exception:  # noqa: BLE001 - temporada inexistente
        return []
    filas = []
    for local, visita, gl, gv, celdas, fecha in FILA.findall(pagina):
        cuotas = re.findall(r'data-odd="([\d.]+)"', celdas)
        m = re.match(r"(\d{2})\.(\d{2})\.(\d{4})?", fecha.strip())
        if not m:
            continue
        cuotas = cuotas if len(cuotas) == 3 else ["", "", ""]  # antes de 2020 no hay cuotas
        filas.append([anio, f"{m[3] or anio}-{m[2]}-{m[1]}", limpiar(local), limpiar(visita), gl, gv, *cuotas])
    return filas


def main():
    slugs = [(f"primera-division-{a}", a) for a in range(2005, 2013)]
    slugs += [("primera-division-2013", 2013), ("primera-division-2013-2014", 2014),
              ("primera-division-2014-2015", 2015), ("primera-division-2015-2016", 2016),
              ("primera-division-2016-2017", 2017)]
    slugs += [(f"primera-division-{a}", a) for a in range(2017, 2025)]
    slugs += [("liga-de-primera-2025", 2025), ("liga-de-primera", 2026)]
    filas = []
    for nombre, anio in slugs:
        r = temporada(nombre, anio)
        print(f"{nombre}: {len(r)} partidos ({sum(1 for x in r if x[6])} con cuotas)")
        filas += r
        time.sleep(0.5)
    ruta = os.path.join(os.path.dirname(__file__), "raw", "CHILE.csv")
    with open(ruta, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["temporada", "fecha", "local", "visita", "gl", "gv", "cuota_l", "cuota_e", "cuota_v"])
        w.writerows(sorted(filas, key=lambda x: x[1]))
    print(f"Total: {len(filas)} partidos -> {ruta}")


if __name__ == "__main__":
    main()
