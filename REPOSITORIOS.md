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
