"""Descarga resultados y cuotas de apuestas desde football-data.co.uk a futbol/raw/.

Ligas europeas: un CSV por liga y temporada (2005/06 en adelante).
Otras ligas (Argentina, Brasil, México, etc.): un CSV por liga con todas las temporadas.
Uso: python3 futbol/descargar_futbol.py
"""
import os
import time
import urllib.request

BASE = "https://www.football-data.co.uk/"
EUROPA = ["E0", "E1", "E2", "E3", "EC", "SC0", "SC1", "SC2", "SC3", "D1", "D2", "I1", "I2", "SP1", "SP2",
          "F1", "F2", "N1", "B1", "P1", "T1", "G1"]
OTRAS = ["ARG", "BRA", "MEX", "USA", "AUT", "CHN", "DNK", "FIN", "IRL", "JPN", "NOR", "POL", "ROU",
         "RUS", "SWE", "SWZ"]
TEMPORADAS = [f"{a % 100:02d}{(a + 1) % 100:02d}" for a in range(2005, 2026)]
DESTINO = os.path.join(os.path.dirname(__file__), "raw")


def bajar(ruta, archivo):
    destino = os.path.join(DESTINO, archivo)
    if os.path.exists(destino) and os.path.getsize(destino) > 0:
        return True
    try:
        req = urllib.request.Request(BASE + ruta, headers={"User-Agent": "Mozilla/5.0"})
        datos = urllib.request.urlopen(req, timeout=30).read()
    except Exception:  # noqa: BLE001 - liga/temporada inexistente
        return False
    if len(datos) < 500:
        return False
    with open(destino, "wb") as f:
        f.write(datos)
    time.sleep(0.3)
    return True


def main():
    os.makedirs(DESTINO, exist_ok=True)
    ok = sum(bajar(f"mmz4281/{t}/{liga}.csv", f"{liga}_{t}.csv") for liga in EUROPA for t in TEMPORADAS)
    ok += sum(bajar(f"new/{liga}.csv", f"{liga}.csv") for liga in OTRAS)
    print(f"Archivos descargados: {ok}")


if __name__ == "__main__":
    main()
