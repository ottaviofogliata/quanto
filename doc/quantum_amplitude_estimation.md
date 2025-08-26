# Quantum Amplitude Estimation

## English
Quantum amplitude estimation (QAE) is a quantum algorithm that speeds up Monte Carlo. Instead of sampling paths one by one, a quantum computer prepares a superposition where the amplitude of a "good" state equals $\sqrt{p}$. Measuring many times would reveal $p$, but QAE uses interference and phase estimation to estimate $p$ with about $O(1/\epsilon)$ applications of the underlying circuit, improving on the classical $O(1/\epsilon^2)$ scaling.

Formally, if $A$ prepares the state $A\lvert0\rangle = \sqrt{p}\lvert\psi_1\rangle + \sqrt{1-p}\lvert\psi_0\rangle$, then the Grover operator $Q = -A S_0 A^\dagger S_{\psi_1}$ has eigenvalues $e^{\pm 2 i \theta}$ where $p = \sin^2 \theta$. Phase estimation on $Q$ yields $\theta$ and thus $p$.

## Italiano
La Quantum Amplitude Estimation (QAE) è un algoritmo quantistico che accelera il Monte Carlo. Invece di campionare i percorsi uno alla volta, un computer quantistico prepara una sovrapposizione in cui l'ampiezza di uno stato "buono" vale $\sqrt{p}$. Misurando molte volte si otterrebbe $p$, ma la QAE sfrutta interferenza e phase estimation per stimare $p$ con circa $O(1/\epsilon)$ applicazioni del circuito di base, migliorando la scalabilità classica $O(1/\epsilon^2)$.

Formalmente, se $A$ prepara lo stato $A\lvert0\rangle = \sqrt{p}\lvert\psi_1\rangle + \sqrt{1-p}\lvert\psi_0\rangle$, allora l'operatore di Grover $Q = -A S_0 A^\dagger S_{\psi_1}$ ha autovalori $e^{\pm 2 i \theta}$ con $p = \sin^2 \theta$. La phase estimation su $Q$ restituisce $\theta$ e quindi $p$.
