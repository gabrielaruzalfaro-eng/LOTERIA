# Contexto del proyecto LOTERIA

## Objetivo
Investigación sobre sorteos de lotería en Chile y modelos predictivos.

## Juegos principales
| Juego | Operador | Formato | Prob. premio mayor |
|---|---|---|---|
| Loto | Polla Chilena de Beneficencia | 6 de 41 | 1 en 4.496.388 |
| Kino | Lotería de Concepción | 14 de 25 | 1 en 4.457.400 |

## Premisa clave
Los sorteos son aleatorios e independientes. Ningún modelo puede predecir los resultados.
Lo que sí se puede investigar con rigor:
- Pruebas de aleatoriedad (chi-cuadrado, rachas, frecuencias) sobre datos históricos.
- Comparar modelos predictivos (ML, frecuencias, "números calientes") contra el azar mediante backtesting.
- Valor esperado y sesgos de los jugadores (números populares → premios compartidos).

## Meta del usuario
Encontrar los números con mayor probabilidad de salir.
Respuesta: en un sorteo justo todos los números tienen igual probabilidad. Plan: (1) probar sesgo con datos
históricos; (2) si no hay sesgo, elegir combinaciones poco populares para no compartir el premio.

## Datos
- `data/kino_principal.csv`: 889 sorteos Kino (2362–3264), faltan 14. Fuente: github.com/Nicovh-Analytics/analisis-loteria-chile (MIT, scraping de chileresultados.com). Ese repo también tiene Loto (~1.222 sorteos, 4 bombos).
- polla.cl y loteria.cl están bloqueados por la red del entorno.

## Base consolidada Kino (`python3 consolidar_kino.py` → `data/kino_historico.csv`)
- 3.275 sorteos (n° 0–3287, 1990-09-19 a 2026-10-02); 2.476 de la era 14 de 25 (desde el 799).
- Fuentes GitHub: FernandoLizana/kino-lab (1990–2024, con fechas), Nicovh (2362–3264), Fernando8955/kino (recientes). 576 sorteos cruzados sin conflictos.
- Faltan 13: 2981, 3155, 3265–3275.
- Loto: solo `data/loto_*.csv` de Nicovh (sorteos 4239–5463, ~1.222 de ~5.400). Historial completo no disponible en fuentes accesibles.
- Sitios oficiales y kinohistorico.cl/chileresultados.com/kaggle bloqueados por la red del entorno.

## Resultados
- Kino 2.476 sorteos: p=0,172 → sin sesgo. 10 el más frecuente (+72), 14 el menos (−36).
- Kino: prueba de uniformidad Monte Carlo p=0.418 → sin sesgo. Más frecuente: 10 (+28); menos: 14 (−26), dentro del azar.
- Script: `python3 analisis_kino.py [n]` → frecuencias, prueba y n combinaciones al azar.

## Hallazgos de otra conversación del usuario (no verificados aquí)
- Fuente: API kinohistorico.cl (bloqueada en este entorno). 2.466 sorteos Kino desde el 799 (antes era 15 de 25). Archivo `kino_consolidado.csv` (1,2 MB, 14.935 filas, filtrar game_code=="KINO"); el usuario aún no lo sube aquí.
- 10 pruebas de aleatoriedad, todas nulas. Backtest (calientes/fríos/atrasados/azar) empatados en ~7,84 aciertos.
- Anomalía "calientes, ventana 100" z=3,35 → con corrección por 20 configuraciones p=0,093; ReKino p=0,88. No significativa.
- Número 10: 1.455 vs 1.381 esperado (z=+3,00), normal como máximo de 25.
- Estimación ~536.000 cartones/sorteo; con pozo $8.240 M el valor esperado salía positivo, pero varianza enorme (Kelly ≈ $0,67 con $10 M).
- Informe: https://claude.ai/code/artifact/6b0a1891-7df5-45b0-9d9c-84c0d486fc6e
- Combinaciones entregadas: Loto 6-19-28-33-36-41. Kino: (1) 1 3 6 7 9 11 13 15 17 18 20 22 24 25; (2) 2 3 4 6 7 8 11 12 13 15 16 19 21 22; (3) 1 4 5 9 11 12 14 16 18 20 21 23 24 25; (4) 2 5 6 7 8 10 14 16 17 18 19 22 23 24.

## Estado
- [x] Datos Kino + análisis
- [x] Base Kino consolidada (faltan 13 sorteos)
- [ ] Loto
