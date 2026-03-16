# U.S. Airline Market Analysis (1993–2024)

**A 31-year analysis of U.S. domestic airline market data to uncover pricing trends, competition effects, and route-level market structure.**  
This project demonstrates **business-focused exploratory analysis, feature engineering, outlier diagnostics, and competition-aware pricing evaluation** using Python.

---

## Live Interactive Case Study

**View the full HTML dashboard / case study here:**  
[Airline Market Dashboard](https://zakarias21.github.io/zakariasportfolio.github.io/assets/img/webp/airline_dashboard.html)

> The HTML dashboard contains the project’s charts, interpretations, business insights, and executive-style case study.  
> This repository contains the **reproducible Jupyter Notebook** and technical workflow behind the analysis.

---

## Project Objective

Analyze how **competition, route distance, passenger demand, and market load factor** influence airline pricing across the U.S. domestic market over a **31-year period (1993–2024)**.

### Core business questions
- How did airline fares evolve over time?
- Does lower competition lead to higher pricing power?
- How does route distance affect fare structure?
- What does demand concentration reveal about pricing behavior?
- How informative is load factor for fare analysis?

---

## Analytical Workflow

### 1) Data Cleaning & Validation
- Standardized renamed columns for analysis consistency
- Converted numeric-like fields using `pd.to_numeric(..., errors='coerce')`
- Handled invalid values and missing entries safely
- Created time-ready fields such as `year_quarter`

### 2) Feature Engineering
Built business-driven analytical features to make comparisons more meaningful:
- `fare_per_mile` → normalizes fares across route lengths
- `distance_band` → groups routes into operational distance categories
- `load_band` → segments route-quarters by market load factor
- `competition_level` → classifies market structure using dominant carrier share

### 3) Exploratory Data Analysis (EDA)
Used EDA to answer business questions, not just summarize columns:
- Fare trend analysis across 30 years
- Passenger demand distribution analysis
- Distance vs fare structure analysis
- Load factor vs fare comparison
- Competition vs pricing comparison

### 4) Outlier Diagnostics
Applied **IQR (Interquartile Range)** to flag:
- Fare outliers
- Passenger volume outliers

**Why it matters:** Airline fares and passenger counts are highly skewed, so IQR is more robust than mean-based assumptions.  
Outliers were **flagged, not removed**, to preserve strategically important edge cases.

### 5) Competition & Pricing Analysis
- Grouped route-quarters by **largest carrier market share**
- Measured pricing using **fare per mile** instead of raw fare
- Evaluated how pricing changes as competition declines

---

## Key Methodologies Used

- **Time-series trend analysis** for long-run fare movement
- **Segmentation / binning** for distance, load factor, and competition regimes
- **Normalized pricing analysis** using `fare_per_mile`
- **IQR-based outlier detection** for skewed fare and demand distributions
- **Correlation analysis** to validate linear relationships
- **Comparative group analysis** across competition and efficiency categories

---

## Key Insights

- **Average fares show a structural long-run shift**, with stronger pricing power emerging after the mid-2000s.
- **Lower competition is associated with higher fare per mile**, suggesting dominant carriers capture stronger pricing power in concentrated markets.
- **Passenger demand is highly right-skewed**, meaning a small number of routes dominate traffic and simple volume assumptions can be misleading.
- **Load factor supports operational context**, but pricing is driven by multiple structural forces—not efficiency alone.

---

## Tools & Libraries

| Tool / Library | Purpose |
|---|---|
| **Python** | Core analysis environment |
| **Pandas** | Data cleaning, grouping, transformation, feature engineering |
| **NumPy** | Numerical operations and array-based calculations |
| **Matplotlib** | Core static visualizations |
| **Seaborn** | Statistical visualization and distribution-focused charts |
| **Plotly** | Interactive and presentation-oriented visualizations |
| **Jupyter Notebook** | Reproducible analysis workflow |
