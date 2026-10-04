"""Consolida el histórico del Loto (sorteo principal, 6 de 41) en data/loto_historico.csv.

Fuentes:
- data/raw/kaggle_loto_historico.csv (kaggle.com/datasets/rigobertomanchu/loto-chile-historico-080511-090424): 3077–5351.
- data/loto_principal.csv (github.com/Nicovh-Analytics/analisis-loteria-chile): 4239–5463.
- data/raw/chileresultados_loto.csv (descargar_chileresultados.py): 4239 en adelante.
"""
import csv
from datetime import datetime

sorteos, conflictos = {}, []


def agregar(fuente, s, fecha, nums, comodin):
    nums = tuple(sorted(nums))
    if len(nums) != 6 or len(set(nums)) != 6 or not all(1 <= x <= 41 for x in nums):
        return
    if s in sorteos:
        if sorteos[s]["nums"] != nums:
            conflictos.append((s, fuente))
            return
        sorteos[s]["fuente"] += "+" + fuente
        sorteos[s]["fecha"] = sorteos[s]["fecha"] or fecha
        sorteos[s]["comodin"] = sorteos[s]["comodin"] or comodin
    else:
        sorteos[s] = {"fecha": fecha, "nums": nums, "comodin": comodin, "fuente": fuente}


with open("data/raw/kaggle_loto_historico.csv") as f:
    for r in csv.DictReader(f):
        fecha = datetime.strptime(r["Fecha"], "%d-%m-%y").date().isoformat()
        agregar("kaggle", int(r["Sorteo"]), fecha, [int(r[f"Num{i}"]) for i in range(1, 7)], r["Comodin"])

with open("data/loto_principal.csv") as f:
    for r in csv.reader(f, delimiter=";"):
        if r and r[0].isdigit() and all(x.strip().isdigit() for x in r[1:7]):
            agregar("nicovh", int(r[0]), "", [int(x) for x in r[1:7]], r[7].strip() if len(r) > 7 else "")

with open("data/raw/chileresultados_loto.csv") as f:
    for r in csv.DictReader(f):
        agregar("chileresultados", int(r["sorteo"]), r["fecha"], map(int, r["numeros"].split()), r["comodin"])

ids = sorted(sorteos)
faltantes = sorted(set(range(ids[0], ids[-1] + 1)) - set(ids))
with open("data/loto_historico.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sorteo", "fecha", "numeros", "comodin", "fuente"])
    for s in ids:
        d = sorteos[s]
        w.writerow([s, d["fecha"], " ".join(map(str, d["nums"])), d["comodin"], d["fuente"]])

print(f"Sorteos: {len(ids)} (n° {ids[0]}–{ids[-1]}, {sorteos[ids[0]]['fecha']} a {sorteos[ids[-1]]['fecha']})")
print(f"Conflictos: {len(conflictos)} {conflictos[:20]}")
print(f"Faltantes: {len(faltantes)} {faltantes[:40]}")
