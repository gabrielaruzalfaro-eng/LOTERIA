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

## Resultados
- Kino: prueba de uniformidad Monte Carlo p=0.418 → sin sesgo. Más frecuente: 10 (+28); menos: 14 (−26), dentro del azar.
- Script: `python3 analisis_kino.py [n]` → frecuencias, prueba y n combinaciones al azar.

## Estado
- [x] Datos Kino + análisis
- [ ] Completar sorteos faltantes (el usuario tiene datos en otra conversación)
- [ ] Loto
