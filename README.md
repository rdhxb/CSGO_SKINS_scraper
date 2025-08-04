# CSGO Skins EV Scraper

A Python tool that scrapes CS:GO case data, computes item and case expected values (EV),  
merges results, and calculates profitability differences.

## Features

- Bypass Cloudflare with `undetected-chromedriver`  
- Parse case listings (name, price, link)  
- Handle both regular and “boosted” cases  
- Extract per-skin price & drop odds  
- Compute EV per item and total EV per case  
- Initialize/reset CSV files (keep only headers) on each run  
- Merge case metadata with EVs and compute price vs EV differential  
- Export all outputs to `data/` as CSVs


## Prerequisites

- Python 3.8+  
- Google Chrome installed  
- Internet connection  

## Installation

1. Clone the repo  
   ```bash
   git clone https://github.com/your-org/CSGO_SKINS.git
   cd CSGO_SKINS
   ```

2. Create & activate a virtual environment  
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies  
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the scraper; it will:

1. Reset all CSVs in `data/` to headers only  
2. Launch Chrome and prompt you to complete any Cloudflare challenge  
3. Scrape cases, items, compute EVs  
4. Merge results and calculate differences  

```bash
python -m csgo_skins.main
```

After the run, inspect:

- `data/cases.csv`  
- `data/items.csv`  
- `data/expected_values.csv`  
- `data/merged_cases_expected_values.csv`  
- `data/cases_with_differences.csv`

## CSV Headers

- **cases.csv**: `case_name`, `case_price`, `case_link`  
- **items.csv**: `Item Name`, `Item Price`, `Item Odds`, `Expected Value`, `Case Name`  
- **expected_values.csv**: `case_link`, `case_total_expected_value`, `case_name`  

## License

MIT