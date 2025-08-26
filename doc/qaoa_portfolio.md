# QAOA Portfolio Optimization / Ottimizzazione di Portafoglio QAOA

## English
Quantum Approximate Optimization Algorithm (QAOA) is a variational approach for
solving combinatorial problems on near‑term quantum hardware. In Quanto the
portfolio selection task is encoded as a quadratic unconstrained binary
optimization: each asset $x_i$ is a binary decision variable, the objective
maximizes expected profits, and a linear constraint enforces a budget. The
problem is translated into a cost Hamiltonian using Qiskit's
`QuadraticProgram`. QAOA alternates applications of the cost Hamiltonian and a
mixing Hamiltonian, producing a parameterized circuit. A classical optimizer
(COBYLA in this toy example) tunes the rotation angles to minimize the expected
energy. The bitstring with highest probability indicates the selected assets.

If the required quantum packages are missing, Quanto falls back to a simple
simulated annealing routine that randomly flips bits while obeying the budget.

## Italiano
Il Quantum Approximate Optimization Algorithm (QAOA) è un approccio
variazionale per risolvere problemi combinatori su hardware quantistico di
prossima generazione. In Quanto il compito di selezione del portafoglio è
codificato come un'ottimizzazione quadratica binaria non vincolata: ogni asset
$x_i$ è una variabile decisionale binaria, l'obiettivo massimizza i profitti
attesi e un vincolo lineare impone il budget. Il problema viene tradotto in una
Hamiltoniana di costo tramite il `QuadraticProgram` di Qiskit. QAOA alterna
applicazioni dell'Hamiltoniana di costo e di mixing, generando un circuito
parametrizzato. Un ottimizzatore classico (COBYLA in questo esempio) regola gli
angoli di rotazione per minimizzare l'energia attesa. Il bitstring con
probabilità più alta indica gli asset selezionati.

Se i pacchetti quantistici richiesti non sono disponibili, Quanto ricorre a una
semplice routine di annealing simulato che inverte casualmente i bit rispettando
il budget.
