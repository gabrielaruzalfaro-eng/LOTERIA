# Repositorios relacionados (investigados 2026-10-04)

## Lotería Chile
| Repo | Qué aporta |
|---|---|
| [Nicovh-Analytics/analisis-loteria-chile](https://github.com/Nicovh-Analytics/analisis-loteria-chile) | Datos Loto/Kino (chileresultados) y ~40 tests de aleatoriedad. Conclusión: no predecible. |
| [FernandoLizana/kino-lab](https://github.com/FernandoLizana/kino-lab) | Histórico Kino 1990–2024; prueba redes neuronales y random forest (sin ventaja). |
| [cmiloarevalo-hash/Estadis](https://github.com/cmiloarevalo-hash/Estadis) | Base auditable multi-fuente del Kino. |
| [Fernando8955/kino](https://github.com/Fernando8955/kino) | Resultados recientes en JSON. |
| [cortega26/polla](https://github.com/cortega26/polla) | Ingesta de pozos del Loto. |

## Mercados de predicción (Polymarket / Kalshi)
| Repo | Qué aporta |
|---|---|
| [wcsmars/Polymarket-Calibration-and-Favorite-Longshot-Bias](https://github.com/wcsmars/Polymarket-Calibration-and-Favorite-Longshot-Bias) | Calibración y sesgo favorito/batacazo. Comprar No en batacazos de 1–10% a 7 días: +1,2% antes de costos, +0,1% después de 1¢ de diferencial. |
| [wcsmars/Polymarket-Forecasting-and-Market-Efficiency](https://github.com/wcsmars/Polymarket-Forecasting-and-Market-Efficiency) | Recalibración logística, isotónica y LightGBM con validación mensual. |
| [zee229/polymarket-research-kit](https://github.com/zee229/polymarket-research-kit) | Backtests con ejecución realista. "Intentamos ganarle al mercado dos veces; el mercado ganó." |
| [CH4RL3I/honest-odds](https://github.com/CH4RL3I/honest-odds) | Calibración con validación fuera de muestra en 2.946 mercados. |
| [Jon-Becker/prediction-market-analysis](https://github.com/Jon-Becker/prediction-market-analysis) | El dataset público más grande de mercados y operaciones de Polymarket y Kalshi. |
| [namanhzz/predictionmarket-calibration](https://github.com/namanhzz/predictionmarket-calibration) | Matriz de calibración de Kalshi por dominio (paper arXiv 2602.19520). |
| [saksham002/prediction-markets](https://github.com/saksham002/prediction-markets) | Market making y arbitraje Polymarket–Kalshi. |
| [kyleyhw/prediction_markets](https://github.com/kyleyhw/prediction_markets) | Microestructura, diferenciales, detección de arbitraje. |
| [aland4747/awesome-prediction-markets](https://github.com/aland4747/awesome-prediction-markets) | Lista de APIs, datasets y herramientas. |

## Apuestas de fútbol
| Repo | Qué aporta |
|---|---|
| [harrigregor/clv-backtester](https://github.com/harrigregor/clv-backtester) | ¿El modelo le gana a la cuota de cierre de Pinnacle? Usa football-data.co.uk, sin fuga de datos. |
| [miaoqi1222/closing-line](https://github.com/miaoqi1222/closing-line) | Modelo vs cierre Pinnacle: CLV −0,4%, ROI +0,5% (intervalos incluyen cero). |
| [ryan00x/Bet-Model](https://github.com/ryan00x/Bet-Model) | El modelo nunca le gana al cierre; la única ventaja viene de casas que actualizan lento sus cuotas. |
| [footballbettingh/football-hub](https://github.com/footballbettingh/football-hub) | Backtest de apuestas de valor: un modelo no le gana al cierre. |
| [navysum/Sports-Betting-Analysis](https://github.com/navysum/Sports-Betting-Analysis) | Dixon-Coles + XGBoost con seguimiento de CLV. |

## Patrón común
Todos los análisis honestos llegan a lo mismo que este proyecto: los modelos no le ganan al mercado; las únicas
ventajas medibles vienen de ineficiencias de precio (cuotas lentas o desactualizadas, sesgo favorito/batacazo) y
suelen desaparecer al incluir costos reales o límites de las casas.

## Bots y copy trading (Polymarket)
⚠ **Alerta de seguridad**: varios repos de "copy trading bot" en GitHub contenían código que roba la clave privada
de la billetera (lee el `.env` y la envía a un servidor del atacante; caso conocido: autor "Trust412", paquete
`excluder-mcp-package`). Muchos repos con nombres repetidos tipo "polymarket bot polymarket bot..." son spam/SEO.
Nunca poner una clave privada con fondos en código de terceros sin auditarlo.

| Repo | Qué es | Nota |
|---|---|---|
| [Polymarket/py-sdk](https://github.com/Polymarket/py-sdk) y clientes oficiales en [github.com/Polymarket](https://github.com/Polymarket) | SDK oficial (py-clob-client fue archivado en mayo 2026) | Base segura para cualquier bot propio |
| [Drakkar-Software/OctoBot-prediction-market](https://github.com/Drakkar-Software/OctoBot-prediction-market) | Bot con copy trading, arbitraje y modo simulado (paper trading) | Proyecto conocido (OctoBot) |
| [ent0n29/polybot](https://github.com/ent0n29/polybot) | Infraestructura de trading y "ingeniería inversa" de estrategias | Útil para estudiar |
| [realfishsam/Polymarket-Copy-Trader](https://github.com/realfishsam/Polymarket-Copy-Trader) | Copia posiciones de billeteras elegidas | Auditar antes de usar |
| dexorynlabs, CoinMLabs, Benjam1nCup, CodeX2124 (copy-trading-bot) | Bots de copy trading | Descripciones spam: tratar como sospechosos |

Pregunta clave del copy trading: ¿los traders que ganaron en el pasado siguen ganando después? (persistencia de
habilidad). Además, al copiar entras después y a peor precio que el trader original.

## Revisión a fondo (resultados reportados por cada repo; no verificados por nosotros)
| Estrategia | Resultado neto, fuera de muestra | Credibilidad |
|---|---|---|
| Fútbol: apostar cuando una casa blanda paga >2% sobre Pinnacle sin margen ([ryan00x/Bet-Model](https://github.com/ryan00x/Bet-Model)) | +4,86% ROI, 20.676 apuestas, CLV +3%, positivo las 13 temporadas | La mejor, pero cae a +1,75% en 2022–24 y las casas limitan a quien gana |
| Polymarket: comprar Sí en cripto a 97–99¢ ([zee229](https://github.com/zee229/polymarket-research-kit)) | +0,65% con precios reales de ejecución | Alta pero diminuta; no pasa corrección por pruebas múltiples |
| Polymarket: comprar No si el Sí cuesta 1–10%, 30 días antes ([wcsmars](https://github.com/wcsmars/Polymarket-Calibration-and-Favorite-Longshot-Bias)) | +0,93% (t=3,0); a 7 días +0,11% | Media: costo fijo de 1¢, sin ejecución real |
| Kalshi: market making pasivo (Darson2004/prediction-market-microstructure) | +0,9¢ por contrato | Media: solo simulación, no replicó al mes siguiente |
| Arbitraje Polymarket–Kalshi (Darson2004) | −1,39¢ por contrato; ventanas de ~48 ms | No funciona para personas |
| Copiar modelos ML/LightGBM | Peor que el precio de mercado | — |

- zee229: de 200 estrategias candidatas, 25 "ganan" usando precio medio, solo 1 con precios reales de ejecución.
- Akey et al. (588 M de operaciones en Polymarket): el 1% de las cuentas se lleva el 76,5% de las ganancias; ganan sobre todo los que ponen órdenes límite (proveen liquidez), no los que apuestan.
- Bürgi, Deng y Whelan (Kalshi): contratos <10¢ pierden >60%; los >50¢ tienen retorno levemente positivo.
- Dataset de Jon-Becker: `https://s3.jbecker.dev/data.tar.zst` (33,5 GB comprimido, Parquet con operaciones de Polymarket y Kalshi).
