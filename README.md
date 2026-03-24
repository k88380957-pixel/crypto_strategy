# AI‑Driven Crypto Strategy

This repository implements an AI‑driven cryptocurrency screening framework.  It combines off‑chain news sentiment with on‑chain flows – including total value locked (TVL), active address counts, large (whale) transactions, exchange net inflows/outflows and price drawdown patterns – to identify tokens that may be oversold yet poised for recovery.  The aim is to find situations where prices have fallen significantly and moved sideways for a prolonged period, capital is moving ahead of price, and the narrative is heating up.

## Background

Working directly with raw blockchain data is challenging because blocks must be indexed, normalized and decoded before they can be queried.  Public blockchain data APIs provide a translation layer that converts complex chain data into structured, queryable formats【708659317754951†L21-L59】.  This project uses open APIs such as DeFiLlama for TVL and protocol statistics【461408456811976†L130-L143】 and Whale Alert for monitoring large transactions; the latter offers developers live and historical data on significant transfers, giving traders early warnings ahead of market moves【580609619903190†L16-L22】【580609619903190†L29-L36】.  Active address counts are a popular proxy for the number of users on a network【686144395634181†L178-L186】, while exchange inflow/outflow metrics measure how many coins move on and off exchanges and can foreshadow future price action【402545572630671†L154-L170】 – large inflows often precede rallies, whereas large outflows can precede declines【402545572630671†L245-L259】.  Price drawdown measures the maximum peak‑to‑trough decline for an asset, providing a key risk indicator【509913816655550†L44-L63】.

## Features

* **News sentiment** – fetches RSS feeds from major crypto news outlets, performs sentiment analysis with VaderSentiment and identifies tokens mentioned positively or negatively.
* **TVL and DeFi flows** – uses the DeFiLlama API to download protocol TVL histories and compute recent percentage changes.
* **Price history and drawdown** – pulls price data from the CoinGecko API and calculates short‑term returns, volatility and maximum drawdown to assess momentum and oversold conditions.
* **Active addresses** – optional integration with services such as CoinMetrics to retrieve daily active address counts, which proxy network usage【686144395634181†L178-L186】.
* **Whale flows** – optional integration with Whale Alert to track large transactions and detect capital moving into or out of token contracts【580609619903190†L16-L22】【580609619903190†L29-L36】.
* **Exchange net flows** – optional integration with on‑chain analytics services (e.g. Santiment) to compute net inflow/outflow of tokens from exchanges; the metric is defined as inflow minus outflow【402545572630671†L154-L170】, and spikes in inflows/outflows often precede price moves【402545572630671†L245-L259】.
* **Composite scoring** – a configurable scoring function combines normalized metrics to rank tokens by recovery potential.  Lower drawdown and volatility, improving TVL and on‑chain metrics, and positive sentiment contribute to higher scores.
* **Risk assessment** – evaluates volatility, drawdown and TVL declines to flag assets with elevated risk.
* **Explainable report** – outputs a human‑readable summary containing top candidates, their quantitative scores, key drivers and risks.

## Repository structure

```
crypto_strategy/
├── data/                   # Modules for fetching data
│   ├── news.py            # News and sentiment analysis
│   ├── defillama.py       # TVL and on‑chain TVL data
│   ├── coingecko.py       # Price and market data
│   └── onchain.py         # Active addresses, whale and exchange flows (optional)
├── analysis/               # Modules for feature engineering and scoring
│   ├── features.py        # Derives metrics from raw data
│   ├── scoring.py         # Combines metrics into a composite score
│   ├── risk.py            # Risk assessment logic
│   └── report.py          # Generates human‑readable report
├── config.py               # Configuration (tokens, weights, API keys)
├── main.py                 # Orchestrates pipeline and outputs results
├── requirements.txt        # Python dependencies
└── .github/workflows/crypto-strategy.yml # GitHub Actions workflow
```

## Installation

1. Clone the repository and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. *(Optional)* set environment variables for services that require API keys:

   - `CM_API_KEY` for CoinMetrics (active addresses).
   - `SAN_API_KEY` for Santiment (exchange flows).
   - `WHALE_ALERT_API_KEY` for Whale Alert (whale flows).

3. Edit `config.py` to customise the list of tokens, news feeds and weighting scheme.

## Usage

Run the pipeline locally with:

```bash
python main.py
```

The script will fetch data for each token, compute features, score them and print a ranking with risk levels and explanations.  On GitHub, the workflow file runs this script daily and can be scheduled to post results to chat services.

## Disclaimer

This project is for educational and research purposes.  It does not constitute financial advice.  Use at your own risk.
