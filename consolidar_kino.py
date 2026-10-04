"""Consolida el histórico del Kino desde varias fuentes públicas en data/kino_historico.csv.

Fuentes (data/raw y data/):
- kinolab_historico.csv  (github.com/FernandoLizana/kino-lab): fecha + números, 1990–2024, sin n° de sorteo.
- kino_principal.csv     (github.com/Nicovh-Analytics/analisis-loteria-chile): n° de sorteo + números, 2362–3264.
- gaaguile_kino_history.json (vía github.com/cmiloarevalo-hash/Estadis): n° + fecha + números.
- chileresultados_kino.csv (descargar_chileresultados.py): n° + fecha + números, recientes.
- fernando8955_kino_polla.json (github.com/Fernando8955/kino): n° + fecha + números, sorteos recientes.
El n° de sorteo de kino-lab se asigna alineando sus combinaciones con las de Nicovh.
"""
import csv
import json
from datetime import datetime

kinolab = []  # (fecha, nums)
with open("data/raw/kinolab_historico.csv") as f:
    for fila in csv.reader(f):
        fecha = datetime.strptime(fila[0], "%d-%m-%Y").date().isoformat()
        kinolab.append((fecha, tuple(sorted(int(x) for x in fila[1:] if x.strip()))))

nicovh = {}
with open("data/kino_principal.csv") as f:
    for fila in csv.DictReader(f):
        nicovh[int(fila["sorteo"])] = tuple(sorted(int(fila[f"n{i}"]) for i in range(1, 15)))

with open("data/raw/fernando8955_kino_polla.json") as f:
    recientes = {s["numero"]: (s["fecha"], tuple(sorted(s["nums"]))) for s in json.load(f)["sorteos"]}

# Alinear: desfase entre índice de fila de kino-lab y n° de sorteo (el más frecuente entre coincidencias).
por_combo = {nums: s for s, nums in nicovh.items()}
desfases = {}
for i, (_, nums) in enumerate(kinolab):
    if nums in por_combo:
        d = por_combo[nums] - i
        desfases[d] = desfases.get(d, 0) + 1
desfase = max(desfases, key=desfases.get)
print(f"Desfase kino-lab→sorteo: {desfase} ({desfases[desfase]} coincidencias; otros: "
      f"{ {k: v for k, v in desfases.items() if k != desfase} })")

sorteos = {}  # n° -> dict
for i, (fecha, nums) in enumerate(kinolab):
    sorteos[i + desfase] = {"fecha": fecha, "nums": nums, "fuente": "kinolab"}

conflictos = []
for s, nums in nicovh.items():
    if s in sorteos:
        if sorteos[s]["nums"] != nums:
            conflictos.append(s)
        else:
            sorteos[s]["fuente"] += "+nicovh"
    else:
        sorteos[s] = {"fecha": "", "nums": nums, "fuente": "nicovh"}
with open("data/raw/gaaguile_kino_history.json") as f:
    gaaguile = {d["drawNumber"]: (datetime.strptime(d["date"], "%A, %b %d, %Y").date().isoformat(),
                                  tuple(sorted(d["numbers"]))) for d in json.load(f)}
for s, (fecha, nums) in gaaguile.items():
    if s in sorteos:
        if sorteos[s]["nums"] != nums:
            conflictos.append(s)
        else:
            sorteos[s]["fuente"] += "+gaaguile"
            sorteos[s]["fecha"] = sorteos[s]["fecha"] or fecha
    else:
        sorteos[s] = {"fecha": fecha, "nums": nums, "fuente": "gaaguile"}

with open("data/raw/chileresultados_kino.csv") as f:
    chileres = {int(r["sorteo"]): (r["fecha"], tuple(sorted(map(int, r["numeros"].split())))) for r in csv.DictReader(f)}

for fuente, datos in (("fernando8955", recientes), ("chileresultados", chileres)):
    for s, (fecha, nums) in datos.items():
        if s in sorteos:
            if sorteos[s]["nums"] != nums:
                conflictos.append(s)
            else:
                sorteos[s]["fuente"] += "+" + fuente
        else:
            sorteos[s] = {"fecha": fecha, "nums": nums, "fuente": fuente}

ids = sorted(sorteos)
faltantes = sorted(set(range(ids[0], ids[-1] + 1)) - set(ids))
with open("data/kino_historico.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sorteo", "fecha", "cantidad", "numeros", "fuente"])
    for s in ids:
        d = sorteos[s]
        w.writerow([s, d["fecha"], len(d["nums"]), " ".join(map(str, d["nums"])), d["fuente"]])

c14 = [s for s in ids if len(sorteos[s]["nums"]) == 14]
print(f"Sorteos: {len(ids)} (n° {ids[0]}–{ids[-1]}), {len(c14)} con 14 números (desde el {c14[0]})")
print(f"Conflictos entre fuentes: {len(conflictos)} {conflictos[:20]}")
print(f"Faltantes: {len(faltantes)} {faltantes[:40]}")
