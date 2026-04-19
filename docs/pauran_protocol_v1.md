# PAURAN PROTOCOL v1.0

## 1. Introduction

Pauran is an open, deterministic protocol designed to define a **global value standard based on real-world production inputs**.

Unlike fiat currencies, which are subject to monetary policy, or cryptocurrencies, which are often driven by speculation, Pauran aims to provide a **transparent, reproducible, and economically grounded reference unit**.

The protocol does not represent a currency, a financial product, or an investment vehicle.
It is a **calculation standard**.

---

## 2. Design Objectives

Pauran is designed to:

* Reflect **global production cost dynamics**
* Be **fully transparent and reproducible**
* Avoid dependence on any single asset class
* Minimize volatility without distorting economic meaning
* Remain independent from political or institutional control

---

## 3. Conceptual Framework

The value of Pauran is derived from four core categories of global production inputs:

1. Energy
2. Food
3. Industrial Metals
4. Precious Metals

---

## 4. Data Source

**World Bank – Commodity Markets Outlook (Pink Sheet)**
Dataset: *Monthly Indices (Base Year: 2010 = 100)*

Selected indices: Energy Index, Food Index, Metals and Minerals Index, Precious Metals Index

Data is retrieved via manual download of the official Excel file to ensure deterministic reproducibility.

---

## 5. Calculation Method

### 5.1 Raw Index (v2 Weights)

```
Pauran_raw = 0.20 × E + 0.40 × F + 0.30 × M + 0.10 × P
```

### 5.2 Smoothing

```
Pauran_t = (Pauran_raw_t + Pauran_raw_{t-1} + Pauran_raw_{t-2}) / 3
```

---

## 6. Data Integrity Rules

* No interpolation
* No backfilling
* Missing data = no calculation for that period
* All users must use identical source data

---

## 7. Versioning

| Version | Weights | Smoothing |
|---------|---------|-----------|
| v1 | Energy 35%, Food 30%, Metals 20%, Precious 15% | None |
| v2 | Energy 20%, Food 40%, Metals 30%, Precious 10% | 3-month MA |

Historical values are immutable. New versions do not overwrite previous results.

---

## 8. Behavioral Definition

> A production-based value index aligned with global inflation dynamics.

Pauran is **not** a crash hedge, speculative asset, or fixed-value instrument.

---

## 9. Governance Principles

* No central authority controls outcomes
* All calculations are publicly verifiable
* Any changes require transparent versioning

---

END OF DOCUMENT
