"""Modelo de IA para predecir el Kino, evaluado con honestidad contra el azar.

Para cada sorteo y cada número (1–25) se arman variables con la historia previa
(si salió en los últimos 10 sorteos, frecuencia en ventanas de 10/50/200, sorteos desde
la última aparición) y el modelo estima la probabilidad de que salga en el sorteo siguiente.
Se entrena con el 70% más antiguo y se evalúa en el 30% más reciente (sin mirar el futuro).
Uso: python3 modelo_ia_kino.py
"""
import csv

import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.neural_network import MLPClassifier

N, K = 25, 14
sorteos = [list(map(int, r["numeros"].split())) for r in csv.DictReader(open("data/kino_historico.csv"))
           if r["cantidad"] == "14"]
M = np.zeros((len(sorteos), N), dtype=np.float32)  # M[t, n-1] = 1 si el número n salió en el sorteo t
for t, s in enumerate(sorteos):
    M[t, np.array(s) - 1] = 1


def variables(t):
    """Variables de los 25 números usando solo sorteos anteriores a t."""
    lags = M[t - 10:t][::-1].T                                    # 25 x 10
    frec = np.stack([M[t - v:t].mean(0) for v in (10, 50, 200)], 1)
    desde = np.array([next((k for k in range(1, 200) if M[t - k, n]), 200) for n in range(N)])[:, None]
    numero = np.eye(N)                                            # identidad del número
    return np.hstack([lags, frec, desde, numero])


INICIO = 200
X = np.vstack([variables(t) for t in range(INICIO, len(sorteos))])
y = M[INICIO:].reshape(-1)
corte = int(0.7 * (len(sorteos) - INICIO)) * N
Xtr, ytr, Xte, yte = X[:corte], y[:corte], X[corte:], y[corte:]
n_test = len(yte) // N

modelos = {
    "Regresión logística": LogisticRegression(max_iter=2000),
    "Gradient boosting": HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05),
    "Red neuronal": MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=300, early_stopping=True,
                                  random_state=0),
}
base = K / N
print(f"Entrenamiento: {corte // N} sorteos · Prueba: {n_test} sorteos (los más recientes)")
print(f"Azar puro: log-loss {log_loss(yte, np.full_like(yte, base)):.4f} · AUC 0,500 · 7,84 aciertos\n")
rng = np.random.default_rng(0)
azar = np.mean([yte.reshape(-1, N)[i, rng.choice(N, K, replace=False)].sum() for i in range(n_test)])
print(f"  {'Azar (simulado)':22s} aciertos promedio {azar:.3f}")
for nombre, m in modelos.items():
    m.fit(Xtr, ytr)
    p = m.predict_proba(Xte)[:, 1]
    top = np.argsort(-p.reshape(-1, N), 1)[:, :K]
    aciertos = np.take_along_axis(yte.reshape(-1, N), top, 1).sum(1)
    print(f"  {nombre:22s} aciertos promedio {aciertos.mean():.3f} · AUC {roc_auc_score(yte, p):.3f} · "
          f"log-loss {log_loss(yte, p):.4f} · veces con 14: {(aciertos == K).sum()}")

# Predicción para el próximo sorteo con el último modelo entrenado en toda la historia
final = HistGradientBoostingClassifier(max_iter=300, learning_rate=0.05).fit(X, y)
p = final.predict_proba(variables(len(sorteos)))[:, 1]
elegidos = sorted((np.argsort(-p)[:K] + 1).tolist())
print(f"\n'Predicción' del modelo para el próximo sorteo: {' '.join(f'{x:02d}' for x in elegidos)}")
print(f"Probabilidades que asigna: {p.min():.3f}–{p.max():.3f} (azar = {base:.3f})")
