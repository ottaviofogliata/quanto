# Quanto

[Versione originale in inglese](README.md)

Laboratorio sperimentale di trading per confrontare metodi classici e simulati quantistici su opzioni, azioni ed ETF.

## Panoramica del Progetto

Quanto è un ambiente di ricerca che indaga come gli algoritmi quantistici possano accelerare la matematica delle strategie su derivati e, più in generale, su titoli ed ETF. Il codice mette affianco tecniche classiche ben note a controparti ispirate al quantum per confrontarne costi e accuratezza. Al centro, Quanto prezza le opzioni stimando il valore atteso scontato dei payoff,

$$
V_0 = e^{-rT} \mathbb{E}[f(S_T)],
$$

ed esplora se routine in stile amplitude estimation possano ridurre la complessità campionaria da $O(1/\epsilon^2)$ a $O(1/\epsilon)$ per un errore target $\epsilon$. Oltre al pricing, il progetto mira a prototipare ottimizzazione di portafoglio, backtesting del rischio e altre attività rilevanti per strategie sistematiche su opzioni, ponendo le basi per futuri esperimenti su hardware quantistico reale.

## Installazione e Setup

Questi comandi installano le dipendenze e avviano gli strumenti in locale. Il progetto usa [Poetry](https://python-poetry.org/) per la gestione dei pacchetti; assicurati che Python 3.11+ e Poetry siano disponibili sul sistema.

```bash
# clonare il repository ed entrarvi
git clone https://github.com/your-org/quanto.git
cd quanto

# installare le dipendenze principali e di sviluppo
poetry install --with dev

# extra opzionali per gli algoritmi quantistici
poetry install -E quantum

# eseguire la suite di test per verificare l'installazione
poetry run pytest

# esplorare l'interfaccia a riga di comando
poetry run quanto --help

# avviare JupyterLab per eseguire i notebook di esempio
poetry run jupyter lab

```

Funzionalità opzionali:

- Accelerazione GPU (MPS): installare `torch` con una build MPS; il codice seleziona automaticamente il dispositivo `mps` quando disponibile.
- Strumenti quantistici: l'extra `-E quantum` installa primitive basate su Qiskit. In assenza di queste, vengono usati fallback classici.

## Documentazione

Il progetto utilizza [MkDocs](https://www.mkdocs.org/) per la documentazione bilingue nella cartella `doc/`. Avvia una anteprima locale con:

```bash
poetry run mkdocs serve
```

Poi apri [http://127.0.0.1:8000](http://127.0.0.1:8000) nel tuo browser per visualizzare le pagine.


## Notebook Jupyter

La directory `notebooks/` contiene una raccolta di notebook che rispecchiano i comandi della CLI e offrono esplorazioni visive. Ogni notebook carica la configurazione di esempio e produce grafici o tabelle utili per l'analisi interattiva.

## Guida completa alla CLI `quanto`

Questa sezione fornisce un tour auto-contenuto dell'interfaccia a riga di comando `quanto`. L'obiettivo è offrire ai nuovi arrivati abbastanza contesto per comprendere i comandi e le idee finanziarie o computazionali sottostanti. Si assume che le dipendenze siano state installate con `poetry install` e che i comandi vengano eseguiti dalla radice del repository. Ogni comando può essere applicato a contratti su opzioni o direttamente a titoli ed ETF a seconda dei simboli forniti.

Il progetto legge le impostazioni da un file di configurazione YAML—questo repository ne include uno di esempio in `examples/config.yaml`. La configurazione specifica elementi come la lista di ticker da considerare (l'*universo*), parametri numerici per le simulazioni e dove memorizzare i file di dati. Ogni comando menzionato sotto fa riferimento a quel file con `--config examples/config.yaml`.

### Valutare un'opzione con il motore classico

Il pricing classico stima il valore equo di un derivato usando la tecnica Monte Carlo. Per un'opzione europea con funzione di payoff $f(S_T)$, tempo a scadenza $T$ e tasso privo di rischio $r$, un prezzo Monte Carlo di base utilizza

$$
V_0 = e^{-rT} \frac{1}{N}\sum_{i=1}^{N} f(S_T^{(i)}),
$$

dove $S_T^{(i)}$ sono i prezzi finali simulati. Aumentare il numero di percorsi $N$ migliora l'accuratezza al costo di maggiore tempo di calcolo.

Il comando seguente valuta un'opzione put su SPY con strike al 5% fuori dal denaro (`--strike -5%`) e trenta giorni alla scadenza (`--dte 30`). Il modello di default simula percorsi di prezzo secondo un moto browniano geometrico.

```bash
poetry run quanto price --ticker SPY --dte 30 --strike -5% --method classical --config examples/config.yaml
```

### Valutare un'opzione con il motore quantistico simulato

L'amplitude estimation quantistica può accelerare quadraticamente il Monte Carlo riducendo il numero di percorsi necessari per stimare il payoff atteso. Invece di girare su hardware quantistico reale, `quanto` usa un simulatore, quindi funziona su qualsiasi macchina. Concettualmente, l'algoritmo prepara una sovrapposizione che codifica tutti i possibili percorsi di prezzo, applica la funzione di payoff e poi usa la phase estimation quantistica per stimare il valore medio $\mu$ con errore dell'ordine $1/M$ anziché $1/\sqrt{M}$ per $M$ valutazioni.

Il comando seguente ripete l'esempio precedente utilizzando il motore quantistico simulato. Confrontare il suo output con quello del motore classico illustra come le tecniche quantistiche potrebbero migliorare l'efficienza nelle future generazioni di hardware.

```bash
poetry run quanto price --ticker SPY --dte 30 --strike -5% --method quantum --config examples/config.yaml
```

### Ottimizzazione di portafoglio

Una volta che le singole opzioni possono essere prezzate, la domanda successiva è come assemblarle in un portafoglio interessante. Il comando `optimize` esegue una semplice ottimizzazione media-varianza sul modello di Markowitz. Se $w$ è un vettore di pesi, $\mu$ sono i rendimenti attesi e $\Sigma$ è la matrice di covarianza, un obiettivo comune è

$$
\min_w \; w^\top \Sigma w - \lambda w^\top \mu,
$$

dove $\lambda$ regola il trade-off tra rischio e rendimento. L'ottimizzatore esplora l'universo di ticker definito in `config.yaml` e cerca la combinazione di pesi che soddisfa al meglio l'obiettivo scelto e gli eventuali vincoli.

```bash
poetry run quanto optimize --config examples/config.yaml
```

### Backtesting della strategia

Il backtesting rigioca una strategia su dati storici per verificarne la performance. Dato un modello di pricing $P$ e una regola di trading $R$, il motore percorre gli stati di mercato passati $\{S_t\}$ e registra profitti e perdite ipotetici

$$
\text{PnL} = \sum_t R(S_t) - P(S_t).
$$

Le metriche risultanti—rendimento totale, volatilità, drawdown—offrono un'indicazione della robustezza prima di impiegare capitale reale. Il comando di esempio esegue un backtest usando le impostazioni definite nel file di configurazione e confronta i risultati con un indice di mercato.

```bash
poetry run quanto backtest --config examples/config.yaml --ticker QQQ --benchmark SPY
```

Aggiungi `--source real` per scaricare i prezzi storici. Il motore interroga
prima Yahoo Finance e poi Stooq, sollevando un errore se entrambe le fonti
falliscono. Viene inviato un User-Agent in stile browser a Yahoo Finance per
ridurre gli errori 403. L'output JSON include un campo `benchmark` che mostra il
rendimento cumulato dell'indice di riferimento sullo stesso periodo:

```json
{
  "days": 10,
  "pnl": 0.0123,
  "benchmark": 0.0087
}
```

Dove:

- `days` è il numero di giorni di trading simulati.
- `pnl` è il rendimento cumulativo della strategia nel periodo.
- `benchmark` è il rendimento cumulativo dell'indice di mercato scelto.

### Backtest di entanglement quantistico

Alcune dinamiche di mercato sembrano collegate in modi che ricordano l'entanglement quantistico: il movimento di uno strumento può preannunciare quello di un altro. Il comando `entangle` esegue un algoritmo ispirato al quantum che può simulare questi legami oppure scaricare dati reali per azioni ed ETF. In modalità simulata applica una forza di correlazione configurabile e genera una semplice regola di trading basata sul ticker più "entangled".

```bash
poetry run quanto entangle --tickers SPY,QQQ,IWM --source real --config examples/config.yaml
```

Passando `--source real` vengono recuperati i dati storici dei ticker indicati. La
routine interroga prima Yahoo Finance e poi Stooq, sollevando un errore se entrambe
le fonti falliscono. Viene inviato un User-Agent in stile browser a Yahoo Finance
per evitare i blocchi 403. Con `--source random`, la sezione
`experiment.entanglement.strength` del file di configurazione controlla le
correlazioni fuori diagonale dei percorsi di prezzo sintetici. Il comando
restituisce un riepilogo JSON come:

```json
{
  "tickers": ["SPY", "QQQ", "IWM"],
  "chosen": "SPY",
  "entanglement": 0.714,
  "pnl": 0.839,
  "benchmark": 0.467,
  "correlation_matrix": [
    [1.0, 0.716, 0.725],
    [0.716, 1.0, 0.700],
    [0.725, 0.700, 1.0]
  ]
}
```

Qui:

- `tickers` elenca gli strumenti analizzati.
- `chosen` è il simbolo con la correlazione media più alta rispetto agli altri.
- `entanglement` è la media assoluta delle correlazioni fuori diagonale.
- `pnl` è il rendimento cumulativo investendo solo nel ticker `chosen`.
- `benchmark` è il rendimento di un portafoglio a pesi uguali di tutti i ticker.
- `correlation_matrix` contiene le correlazioni a coppie tra i rendimenti simulati
  per ciascun ticker; valori vicini a ±1 indicano un forte legame e guidano
  l'euristica di entanglement.

Il notebook corrispondente in `notebooks/entanglement_backtest.ipynb` visualizza la matrice di correlazione come heatmap e traccia l'andamento della strategia rispetto al benchmark per ulteriori esplorazioni.
