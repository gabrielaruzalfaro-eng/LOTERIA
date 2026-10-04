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
- 3.280 sorteos (n° 0–3287, 1990-09-19 a 2026-10-02); 2.481 de la era 14 de 25 (desde el 799).
- Fuentes GitHub: FernandoLizana/kino-lab (1990–2024), Nicovh (2362–3264), gaaguile vía cmiloarevalo-hash/Estadis (0–3267), Fernando8955/kino `kino-polla.json` (recientes). 3.263 sorteos confirmados por ≥2 fuentes, 0 conflictos.
- Faltan 8: 3268–3275. Descartado `resultados.json` de Fernando8955 (sorteo diario, no coincide con el Kino).
- Loto (`python3 consolidar_loto.py` → `data/loto_historico.csv`): 2.409 sorteos (3077–5485, 2011-05-08 a 2026-10-01), 0 faltantes, 0 conflictos. Fuentes: Kaggle + Nicovh + chileresultados. Antes de 2011 no hay fuente accesible (polla.cl tiene antibot Incapsula).
- Sitios oficiales y kinohistorico.cl/chileresultados.com/kaggle bloqueados por la red del entorno.

## Resultados
- Kino 2.481 sorteos: p≈0,17 → sin sesgo. 10 el más frecuente (+72), 14 el menos (−36).
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

## Protocolo del sorteo Kino (texto aportado por el usuario, sin fuente verificada)
- Hay varios sets de bolitas (A, B, C...) sellados; el notario elige uno al azar antes de cada sorteo y pesa las 25 bolitas.
- Implicancia: un sesgo de un set se diluye al mezclar sorteos de todos los sets. Para probarlo se necesitaría saber qué set se usó en cada sorteo (actas notariales); sin ese dato no es analizable.

## Backtest Kino (`python3 backtest_kino.py`, 2.389 sorteos)
- Azar 7,83 · calientes 7,86–7,92 · fríos 7,79–7,85 · repetir último 7,88 aciertos (esperado 7,84). Ninguno predice.
- El usuario solo quiere predicción/ganar dinero. Respuesta: no hay método que prediga; única palanca es valor esperado (pozos acumulados, no compartir premio).

## Modelo IA Kino (`python3 modelo_ia_kino.py`; requiere numpy y scikit-learn)
- Logística, gradient boosting y red neuronal; entrenamiento con 1.602 sorteos, prueba con los 687 más recientes.
- AUC 0,502–0,507 y log-loss igual o peor que el azar (0,6859). Aciertos 7,85–7,93 vs 7,84 esperado (error estándar ≈0,05; con 3 modelos probados no es significativo). La IA no predice.

## Fútbol (carpeta `futbol/`)
- Datos (no se suben a git; regenerar): `python3 futbol/descargar_futbol.py` (football-data.co.uk: 22 ligas europeas 2005–2026 + 16 ligas del resto del mundo; ojo: CHL = China, no Chile) y `python3 futbol/descargar_chile.py` (betexplorer: Chile, cuotas solo desde 2020; antes de 2020 solo partidos parciales).
- Modelo `python3 futbol/modelo_futbol.py`: Elo + regresión logística, entrenado año a año con años previos.
- 228.130 partidos, 203.570 evaluados fuera de muestra. Acierto: modelo 48,6% vs casas de apuestas 50,1% (log-loss 1,025 vs 1,005).
- ROI apostando cuando el modelo ve valor: −11,7% con cuota promedio; −3,4% con la mejor cuota del mercado. Ninguna liga positiva (mejor Austria −2,5%; Chile −12%).

## Fútbol v2 (`python3 futbol/modelo_futbol_v2.py`, ~75 s)
- Gradient boosting con Elo, goles, tiros al arco, forma y descanso. Acierto 48,7%, log-loss 1,0231 vs casas 1,0050. Apostando solo con el modelo: ROI −10,9% (cuota promedio), −3,1% (mejor cuota).
- Mercado + modelo con mejor cuota: ROI +1,4% (ventaja>0%), +4,8% (>5%). PERO el control sin modelo (mercado recalibrado + mejor cuota) da lo mismo o más: +1,2% / +5,2% / +8,5%. El modelo no aporta información (log-loss 1,0041 vs 1,0040 del control).
- La "ganancia" viene de una ineficiencia conocida: recalibrar el sesgo favorito/batacazo de las casas y apostar a la cuota máxima. En la práctica las cuotas máximas suelen ser de casas que limitan o cierran cuentas ganadoras, o son cuotas desactualizadas/erróneas.

## Estado
- [x] Datos Kino + análisis
- [x] Base Kino consolidada (faltan 8 sorteos)
- [x] Loto consolidado
