# Quanto

[Versione originale in inglese](README.md) – questa è una traduzione completa del README inglese.

Questo README è la traduzione completa del file in inglese.

Laboratorio sperimentale di trading per confrontare metodi classici e simulati quantistici su
opzioni, azioni ed ETF.

## Panoramica del Progetto

Quanto è un ambiente di ricerca che indaga come gli algoritmi quantistici possano accelerare la
matematica delle strategie su derivati e, più in generale, su titoli ed ETF. Il codice affianca
tecniche classiche ben note a controparti ispirate al quantum per confrontarne costi e accuratezza.
Al centro, Quanto prezza le opzioni stimando il valore atteso scontato dei payoff,

$$ V_0 = e^{-rT} \mathbb{E}[f(S_T)], $$

ed esplora se routine in stile amplitude estimation possano ridurre la complessità campionaria da
$O(1/\epsilon^2)$ a $O(1/\epsilon)$ per un errore target $\epsilon$. Oltre al pricing, il progetto
mira a prototipare ottimizzazione di portafoglio, backtesting del rischio e altre attività rilevanti
per strategie sistematiche su opzioni, ponendo le basi per futuri esperimenti su hardware
quantistico reale.

## Installazione e Setup

Questi comandi installano le dipendenze e avviano gli strumenti in locale. Il progetto usa
[Poetry](https://python-poetry.org/) per la gestione dei pacchetti; assicurati che Python 3.11+ e
Poetry siano disponibili sul sistema.

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

- Accelerazione GPU (MPS): installare `torch` con una build MPS:

  ```bash
  pip install torch torchvision torchaudio -f https://download.pytorch.org/whl/metal.html
  ```

  Il codice seleziona automaticamente il dispositivo `mps` quando disponibile.
- Strumenti quantistici: installare le primitive basate su Qiskit con:

  ```bash
  poetry install -E quantum
  ```

  In assenza di queste, vengono usati fallback classici.

## Flusso tipico

Prima di eseguire i comandi, scegli la classe di asset con `--asset-class options`
per i contratti su opzioni o `--asset-class stocks` per azioni ed ETF.

```bash
poetry run quanto price --asset-class options --ticker SPY --dte 30 --strike -5% --config examples/config.yaml
# {"price": 5.624190052301251, "device": "cpu"}

poetry run quanto price --asset-class stocks --ticker SPY --config examples/config.yaml
# {"price": 500.12, "device": "cpu"}
```

In entrambi i casi, `price` rappresenta il premio dell'opzione o il prezzo
dell'azione, mentre `device` indica il backend di calcolo.

Una volta configurato l'ambiente, un ciclo di ricerca di base è il seguente:

1. **Prezzare gli strumenti** per ottenere rendimenti o payoff attesi:
   `poetry run quanto price --asset-class options --ticker SPY --dte 30 --strike -5% --config examples/config.yaml`
   Per le azioni specificare `--asset-class stocks --ticker AAPL` per ottenere l'ultimo prezzo.
2. **Ottimizzare un portafoglio** con il MILP classico o con la routine quantistica:
   `poetry run quanto optimize --asset-class options --method classical --config examples/config.yaml`
3. **Backtestare la strategia** per valutarne le prestazioni storiche:
   `poetry run quanto backtest --asset-class options --config examples/config.yaml`

`entangle` può essere eseguito facoltativamente prima dell'ottimizzazione per ispezionare le correlazioni tra i titoli. Modifica il file di configurazione tra un passo e l'altro per sperimentare universi o vincoli diversi.

## Documentazione

Il progetto utilizza [MkDocs](https://www.mkdocs.org/) per la documentazione bilingue nella cartella `doc/`. Avvia una anteprima locale con:

```bash
poetry run mkdocs serve
```

Poi apri [http://127.0.0.1:8000](http://127.0.0.1:8000) nel tuo browser per visualizzare le pagine.


## Notebook Jupyter

La directory `notebooks/` contiene una raccolta di notebook che rispecchiano i comandi della CLI e
offrono esplorazioni visive. Ogni notebook carica la configurazione di esempio e produce grafici o
tabelle utili per l'analisi interattiva.

## Guida completa alla CLI `quanto`

Questa sezione fornisce un tour auto-contenuto dell'interfaccia a riga di comando `quanto`.
L'obiettivo è offrire ai nuovi arrivati abbastanza contesto per comprendere i comandi e le idee
finanziarie o computazionali sottostanti. Si assume che le dipendenze siano state installate con
`poetry install` e che i comandi vengano eseguiti dalla radice del repository. Ogni comando può
essere applicato a contratti su opzioni o direttamente a titoli ed ETF a seconda dei simboli
forniti.

Il progetto legge le impostazioni da un file di configurazione YAML—questo repository ne include uno
di esempio in `examples/config.yaml`. La configurazione inizia con un campo `asset_class`, ad esempio
`options` o `stocks`, e poi specifica elementi come la lista di ticker da considerare (l'*universo*),
parametri numerici per le simulazioni e dove memorizzare i file di dati. Ogni comando menzionato sotto
fa riferimento a quel file con `--config examples/config.yaml`.

### Valutare un'opzione con il motore classico

Il pricing classico stima il valore equo di un derivato usando la tecnica Monte Carlo. Per
un'opzione europea con funzione di payoff $f(S_T)$, tempo a scadenza $T$ e tasso privo di rischio
$r$, un prezzo Monte Carlo di base utilizza

$$ V_0 = e^{-rT} \frac{1}{N}\sum_{i=1}^{N} f(S_T^{(i)}), $$

dove $S_T^{(i)}$ sono i prezzi finali simulati. Aumentare il numero di percorsi $N$ migliora
l'accuratezza al costo di maggiore tempo di calcolo.

Il comando seguente valuta un'opzione put su SPY con strike al 5% fuori dal denaro (`--strike -5%`)
e trenta giorni alla scadenza (`--dte 30`). Il modello di default simula percorsi di prezzo secondo
un moto browniano geometrico.

```bash
poetry run quanto price --asset-class options --ticker SPY --dte 30 --strike -5% --method classical --config examples/config.yaml
```

Il comando stampa un oggetto JSON come `{ "price": 1.23, "device": "cpu" }`.
Qui `price` è il premio equo da pagare o ricevere per l'opzione secondo questo
modello, mentre `device` indica il backend numerico (NumPy o Torch) usato per
simulare i percorsi.

### Valutare un'opzione con il motore quantistico simulato

L'amplitude estimation quantistica può accelerare quadraticamente il Monte Carlo riducendo il numero
di percorsi necessari per stimare il payoff atteso. Invece di girare su hardware quantistico reale,
`quanto` usa un simulatore, quindi funziona su qualsiasi macchina. Concettualmente, l'algoritmo
prepara una sovrapposizione che codifica tutti i possibili percorsi di prezzo, applica la funzione
di payoff e poi usa la phase estimation quantistica per stimare il valore medio $\mu$ con errore
dell'ordine $1/M$ anziché $1/\sqrt{M}$ per $M$ valutazioni.

Il comando seguente ripete l'esempio precedente utilizzando il motore quantistico simulato.
Confrontare il suo output con quello del motore classico illustra come le tecniche quantistiche
potrebbero migliorare l'efficienza nelle future generazioni di hardware.

```bash
poetry run quanto price --asset-class options --ticker SPY --dte 30 --strike -5% --method quantum --config examples/config.yaml
```

L'output rispecchia il comando classico, restituendo campi come
`{ "price": 1.20, "device": "qiskit_simulator" }`. Il valore `price` rappresenta
ancora il premio modellizzato dell'opzione e `device` identifica il simulatore
che fornisce la stima così da confrontare direttamente i due approcci.

### Ottimizzazione di portafoglio

Una volta che le singole opzioni possono essere prezzate, la domanda successiva è come assemblarle
in un portafoglio interessante. Il comando `optimize` esegue una semplice ottimizzazione media-
varianza sul modello di Markowitz. Se $w$ è un vettore di pesi, $\mu$ sono i rendimenti attesi e
$\Sigma$ è la matrice di covarianza, un obiettivo comune è

$$ \min_w \; w^\top \Sigma w - \lambda w^\top \mu, $$

dove $\lambda$ regola il trade-off tra rischio e rendimento. L'ottimizzatore esplora l'universo di
ticker definito in `config.yaml` e cerca la combinazione di pesi che soddisfa al meglio l'obiettivo
scelto e gli eventuali vincoli.

```bash
poetry run quanto optimize --asset-class options --method classical --config examples/config.yaml
```

Il flag `--method` seleziona l'ottimizzatore: `classical` esegue un baseline
MILP, mentre `quantum` mappa il problema di selezione con vincolo di budget in
un'ottimizzazione quadratica binaria non vincolata e applica una routine in
stile QAOA. QAOA alterna Hamiltoniane del problema e di mixing in un piccolo
circuito parametrizzato; un ottimizzatore classico regola gli angoli affinché il
circuito approssimi il portafoglio ottimale. In assenza delle librerie
quantistiche, il comando ricade su un annealing simulato. Un esempio di
risposta è:

```json
{
  "selection": [0, 1],
  "method": "milp"
}
```

`selection` elenca gli strumenti scelti per indice e `method` indica quale
ottimizzatore ha generato il risultato.

Per un'analisi più approfondita della routine quantistica, consulta la
[documentazione sull'ottimizzazione QAOA del portafoglio](doc/qaoa_portfolio.md).

### Backtesting della strategia

Il backtesting rigioca una strategia di trading su dati storici per verificarne
la performance. Una strategia combina un modello di pricing $P$ con una regola di
trading $R$: un insieme di istruzioni su quando comprare, vendere o mantenere
posizioni in base allo stato di mercato osservato $S_t$. Il motore attraversa gli
stati di mercato passati $\{S_t\}$, applica $R$ per decidere la posizione,
sottrae il prezzo del modello $P(S_t)$ come costo dell'operazione e accumula i
profitti e le perdite risultanti

$$ \text{PnL} = \sum_t R(S_t) - P(S_t). $$

Le metriche risultanti—rendimento totale, volatilità, drawdown—offrono un'indicazione della
robustezza prima di impiegare capitale reale. Il comando di esempio esegue un backtest usando le
impostazioni definite nel file di configurazione e confronta i risultati con un indice di mercato.

```bash
poetry run quanto backtest --asset-class options --tickers QQQ --benchmark SPY --config examples/config.yaml
```

Aggiungi `--source real` per scaricare i prezzi storici. Il motore interroga prima Yahoo Finance e
poi Stooq, sollevando un errore se entrambe le fonti falliscono. Viene inviato un User-Agent in
stile browser a Yahoo Finance per ridurre gli errori 403. L'output JSON include campi come `days`
(giorni di trading), `pnl` (profitto/perdita cumulativo) e `benchmark` (rendimento di mercato) sullo
stesso periodo:

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

Alcune dinamiche di mercato sembrano collegate in modi che ricordano l'entanglement quantistico: il
movimento di uno strumento può preannunciare quello di un altro. Il comando `entangle` esegue un
algoritmo ispirato al quantum che può simulare questi legami oppure scaricare dati reali per azioni
ed ETF. In modalità simulata applica una forza di correlazione configurabile e genera una semplice
regola di trading basata sul ticker più "entangled". La regola è diretta: investire
tutto il capitale nello strumento con la correlazione media più alta rispetto agli
altri e mantenere la posizione per l'intera finestra di test.

```bash
poetry run quanto entangle --tickers SPY,QQQ,IWM --source real --config examples/config.yaml
```

Passando `--source real` vengono recuperati i dati storici dei ticker indicati. La routine interroga
prima Yahoo Finance e poi Stooq, sollevando un errore se entrambe le fonti falliscono. Viene inviato
un User-Agent in stile browser a Yahoo Finance per evitare i blocchi 403. Con `--source random`, la
sezione `experiment.entanglement.strength` del file di configurazione controlla le correlazioni
fuori diagonale dei percorsi di prezzo sintetici. Il comando restituisce un riepilogo JSON come:

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
- `correlation_matrix` contiene le correlazioni a coppie tra i rendimenti simulati per ciascun ticker; valori vicini a ±1 indicano un forte legame e guidano l'euristica di entanglement.

Il notebook corrispondente in `notebooks/entanglement_backtest.ipynb` visualizza la matrice di
correlazione come heatmap e traccia l'andamento della strategia rispetto al benchmark per ulteriori
esplorazioni.

### Dimostrazione della curva di Hilbert

La curva di Hilbert è un frattale riempitivo di spazio che mappa un indice unidimensionale su una
griglia bidimensionale preservando la località: punti vicini sulla curva restano vicini anche nel
piano. È costruita ricorsivamente. Sia $H_1$ un semplice percorso attraverso quattro quadranti. Per
costruire $H_{n+1}$, ruota e collega quattro copie di $H_n$, ottenendo un cammino che visita
ciascuna delle $2^{2(n+1)}$ celle della griglia esattamente una volta. Quando $n \to \infty$ la
curva riempie l'intero quadrato unitario.

Questa proprietà rende le curve di Hilbert utili per indicizzare dati multidimensionali. `quanto`
include una piccola demo che mostra come un punto $(x, y)$ nel quadrato unitario viene mappato al
proprio indice di Hilbert $h$. La mappatura inversa—recuperare $(x, y)$ da $h$—è anch'essa
illustrata, evidenziando come la località sia ampiamente preservata nonostante la riduzione di
dimensionalità.

```bash
poetry run quanto hilbert-demo --config examples/config.yaml
```

L'esecuzione della demo stampa una tabella di coordinate affiancata ai relativi indici di Hilbert e,
in alcune configurazioni, traccia la curva per fornire intuizione visiva.

---

Questo progetto utilizza massicciamente l'IA e gli agenti per automatizzare ricerca e sviluppo. Le
linee guida per questi agenti sono definite in [AGENTS.md](https://agents.md), una specifica che
spiega come le istruzioni specifiche del repository aiutino i contributori automatizzati a mantenere
coerenza e qualità.
