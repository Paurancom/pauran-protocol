# Pauran Protocol

Pauran is a production-based global value index.

It tracks real-world production costs — energy, food, industrial metals, and precious metals — using publicly available World Bank data. The result is a transparent, reproducible reference unit that reflects global economic activity, not market sentiment.

---

## How It Works

Pauran is calculated from four components:

| Component       | Weight |
|----------------|--------|
| Food            | 40%    |
| Metals          | 30%    |
| Energy          | 20%    |
| Precious Metals | 10%    |

**Formula:**
```
Pauran_raw = 0.20 × Energy + 0.40 × Food + 0.30 × Metals + 0.10 × Precious
Pauran     = 3-month moving average of Pauran_raw
```

A 3-month moving average is applied to reduce short-term noise while preserving responsiveness to real economic shifts.

---

## Data Source

**World Bank – Commodity Markets Outlook (Pink Sheet)**
Dataset: *Monthly Indices (Base Year: 2010 = 100)*

Download: [https://www.worldbank.org/en/research/commodity-markets](https://www.worldbank.org/en/research/commodity-markets)

File: `CMO-Historical-Data-Monthly.xlsx` → Sheet: `Monthly Indices`

---

## Running the Pipeline

### Requirements

```bash
pip install pandas openpyxl numpy
```

### Usage

```bash
python3 pauran_pipeline.py CMOHistoricalDataMonthly.xlsx output
```

This produces:
- `output/pauran_output.csv` — full monthly series
- `output/pauran_output.json` — same data with protocol metadata

### Output Format

```
Date, Energy, Food, Metals, Precious_Metals, Pauran_raw, Pauran
1960-03, 2.134449, 21.057413, 12.720559, 3.268735, 12.992896, 13.026580
...
2021-02, 79.209480, 114.260994, 106.517786, 142.949688, 107.796598, 103.813407
```

---

## Integrity Rules

- No interpolation
- No backfilling
- Missing data = no calculation for that period
- All calculations are deterministic and reproducible

Anyone using the same source file will produce identical output.

---

## Sample Output

See [`sample_output.csv`](sample_output.csv) and [`sample_output.json`](sample_output.json) for reference output generated from the March 2021 Pink Sheet release.

---

## Protocol Documentation

Full protocol specification: [`docs/pauran_protocol_v1.md`](docs/pauran_protocol_v1.md)

---

## Versioning

| Version | Weights                        | Smoothing |
|---------|-------------------------------|-----------|
| v1      | Energy 35%, Food 30%, Metals 20%, Precious 15% | None |
| v2      | Energy 20%, Food 40%, Metals 30%, Precious 10% | 3-month MA |

Historical values are immutable. New versions do not overwrite previous results.

---

## What Pauran Is Not

- Not a cryptocurrency
- Not a stablecoin
- Not a financial product
- Not an investment recommendation

---

## License

Protocol and code are released under the MIT License.
