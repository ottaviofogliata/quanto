# Monte Carlo

## English
Monte Carlo methods solve problems by repeating random experiments. Imagine estimating the average of a function $f(x)$: draw random samples $x_i$ and compute $\frac{1}{N}\sum_{i=1}^N f(x_i)$. As $N$ grows, this average approaches the true expectation $\mathbb{E}[f(X)]$.

A simple option price uses this idea. Simulate many future prices $S_T^{(i)}$ and average their payoffs $f(S_T^{(i)})$ to approximate $V_0 = e^{-rT}\mathbb{E}[f(S_T)]$. More paths reduce the error roughly like $1/\sqrt{N}$.

## Italiano
I metodi Monte Carlo risolvono problemi ripetendo esperimenti casuali. Per stimare la media di una funzione $f(x)$, si estraggono campioni casuali $x_i$ e si calcola $\frac{1}{N}\sum_{i=1}^N f(x_i)$. Quando $N$ aumenta, questa media si avvicina al valore atteso $\mathbb{E}[f(X)]$.

Un semplice prezzo di un'opzione usa questa idea. Si simulano molti prezzi futuri $S_T^{(i)}$ e si media il payoff $f(S_T^{(i)})$ per approssimare $V_0 = e^{-rT}\mathbb{E}[f(S_T)]$. Più percorsi riducono l'errore all'incirca come $1/\sqrt{N}$.
