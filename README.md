# U.S. Airline Market Analysis (1993–2024)
### 31 Years of Market Structure, Pricing Dynamics, and Competitive Intelligence in the U.S. Airline Industry

**Value Proposition:**  
This project analyzes **31 years of U.S. domestic airline market data (1993–2024)** to uncover how **market concentration, route structure, demand intensity, and operational efficiency** influence fare behavior over time.  
Built as a **business intelligence case study**, it demonstrates the ability to handle **large-scale historical data**, apply **robust statistical methods**, and translate raw transportation data into **strategic commercial insights**.

---

## Live Project Dashboard / Case Study

**Interactive HTML Case Study:**  
[View the full airline dashboard and visual case study](https://zakarias21.github.io/zakariasportfolio.github.io/assets/img/webp/airline_dashboard.html)

> **Note:** The HTML dashboard contains the project’s charts, interpretations, insights, and business case narrative.  
> This GitHub repository provides the **reproducible analytical notebook**, methodology, and technical workflow behind the findings.

---

## Project Snapshot

| Category | Details |
|---|---|
| **Project Type** | Longitudinal Business Intelligence / Exploratory Market Analysis |
| **Industry** | Aviation / Transportation / Pricing Strategy |
| **Time Horizon** | **1993–2024** (31 years) |
| **Primary Goal** | Understand how competition, distance, demand, and load efficiency shape airline pricing |
| **Analysis Style** | Descriptive Analytics, Market Structure Analysis, Pricing Diagnostics |
| **Output** | Jupyter Notebook + Interactive HTML Case Study |

---

## Business Problem

The U.S. airline market is shaped by structural forces that evolve over decades:  
- **Carrier dominance on routes**
- **Fare sensitivity to competition**
- **Demand concentration**
- **Distance-driven pricing behavior**
- **Operational efficiency reflected in load factor**

This project investigates:

- How did average fares evolve across **three decades of industry change**?
- Does **reduced competition** consistently lead to **higher normalized pricing**?
- How does **distance** influence fare distributions across route types?
- Are **high-demand routes** associated with lower or higher fares?
- What do **load factors** reveal about pricing discipline and route efficiency?

---

## Dataset Overview

This project analyzes a **30-year historical airline market dataset** spanning **1993 to 2024**, with each record representing a **route-quarter observation** in the U.S. domestic airline market.

### Core Fields Used

- `year`, `quarter`, `year_quarter`
- `origin_airport`, `destination_airport`
- `origin_market_id`, `destination_market_id`
- `distance_miles`
- `passenger_count`
- `average_fare`
- `largest_carrier`
- `largest_carrier_market_share`
- `largest_carrier_fare`
- `lowest_fare_carrier`
- `lowest_carrier_fare`
- `market_load_factor`

### Why this dataset is strong for portfolio value

This is not a short toy dataset. It demonstrates:

- **Long-horizon trend analysis**
- **Handling structurally evolving markets**
- **Mixed data cleaning across categorical + numeric fields**
- **Distribution-aware statistical analysis**
- **Business framing beyond simple charting**

---

## Analytical Workflow (Pipeline)

### 1) Data Cleaning & Validation

The project begins with a structured cleaning and validation process designed for **historical consistency across 30 years**.

**Key tasks included:**
- Renaming and standardizing raw column names
- Converting numeric-like fields using `pd.to_numeric(..., errors='coerce')`
- Handling invalid strings and malformed entries as `NaN`
- Verifying data types for pricing, demand, distance, market share, and load factor
- Creating derived analytical fields such as:
  - `year_quarter`
  - `fare_per_mile`
  - `distance_band`
  - `load_band`
  - `competition_level`
- Flagging outliers rather than deleting them, preserving business-relevant edge cases
---

### 2) Exploratory Data Analysis (EDA)

EDA was designed to answer **business questions**, not just summarize columns.

**Exploration themes included:**
- Long-term fare trend analysis across quarters and years
- Passenger volume distribution and demand concentration
- Fare dispersion across route distance categories
- Load factor segmentation and operational efficiency patterns
- Structural comparison of pricing under different competition regimes

This stage combines:
- Trend analysis
- Distribution diagnostics
- Segmentation logic
- Correlation validation
- Group-level pricing comparisons

---

### 3) Competition & Pricing Impact Analysis

A core focus of the project is the relationship between **market concentration** and **normalized pricing behavior**.

To avoid misleading conclusions from route length differences, the analysis uses:

- **`fare_per_mile = average_fare / distance_miles`**

Then, route-quarters are classified by dominant carrier market share:

| Competition Level | Largest Carrier Market Share |
|---|---|
| **Highly competitive** | 0% – 40% |
| **Moderate** | 40% – 60% |
| **Low competition** | 60% – 80% |
| **Near monopoly** | 80% – 100% |
---

## Technical Deep Dive

### Outlier Detection Using IQR (Interquartile Range)

Because airline fares and passenger volumes are typically **right-skewed**, traditional mean-based assumptions can be misleading.

This project uses the **IQR (Interquartile Range) method** to identify outliers

### Why IQR was necessary here

Airline market data contains:
- premium long-haul fares
- unusually low promotional fares
- highly concentrated high-demand routes
- structurally extreme passenger counts

These distributions are **not normally distributed**.

Using IQR was the correct choice because it is:

- **robust to skewness**
- **less distorted by extreme values**
- **better suited for real-world pricing distributions**
- **appropriate for business diagnostics without over-cleaning**

### Important methodological choice

Instead of removing outliers, the project **flags them** using:

- `is_fare_outlier`
- `is_passenger_outlier`

This preserves analytically valuable edge cases while maintaining transparency.

---

## Feature Engineering Highlights

The notebook includes several business-driven derived variables:

| Engineered Feature | Purpose |
|---|---|
| **`year_quarter`** | Enables time-series trend analysis |
| **`fare_per_mile`** | Normalizes pricing across route lengths |
| **`distance_band`** | Converts route length into operationally meaningful categories |
| **`load_band`** | Segments route-quarters by load efficiency |
| **`competition_level`** | Translates carrier market share into market structure language |
| **`is_fare_outlier`** | Flags unusually high/low fare observations |
| **`is_passenger_outlier`** | Flags unusually high-demand routes |

This is a strong signal to recruiters because it shows **analytical thinking**, not just plotting.

---

## Visual Storytelling

The project uses both **static** and **interactive** visualizations to communicate findings clearly.

### 1) Long-Term Fare Trend (1993–2024)
**Purpose:** Identify structural shifts in pricing across three decades.

**Business value:**
- Reveals long-cycle fare compression and expansion
- Highlights post-2005 upward pricing regime
- Captures disruption around 2020 and subsequent recovery
- Shows the highest observed fare levels in the latest period

---

### 2) Fare per Mile by Competition Level
**Purpose:** Test whether market concentration influences normalized pricing.

**Business value:**
- Controls for route distance bias
- Makes cross-market comparison fairer
- Shows that weaker competition is associated with higher pricing power
- Supports the pricing strategy narrative with clearer economic logic than raw fares alone

---

### 3) Fare Distribution by Distance Band
**Purpose:** Examine how route length changes fare structure.

**Business value:**
- Shows that fare behavior is not linear with distance
- Reveals spread and dispersion across short-, medium-, and long-haul markets
- Helps distinguish absolute fare effects from route composition effects

---

## Strategic Insights (Outcome)

### 1) The market experienced a structural pricing shift, not just normal fluctuation
Over the 30-year period, average fares did not move randomly. The data suggests a **long-run transition from early fare softening to a stronger sustained pricing regime**, especially after the mid-2000s.

**Implication:**  
This points to structural industry changes—likely driven by consolidation, capacity discipline, and more rational yield management.

---

### 2) Competition matters more when measured correctly
Raw fare comparisons can be misleading because longer routes naturally cost more. Once fares are normalized using **fare per mile**, the relationship becomes clearer:

- **Higher competition → lower fare per mile**
- **Lower competition / near-monopoly → higher fare per mile**

**Implication:**  
Market concentration appears to strengthen **pricing power**, especially in concentrated route markets.

---

### 3) Demand does not mechanically force lower prices
Passenger volume is heavily right-skewed, meaning a small number of routes dominate traffic. This makes simple demand assumptions unreliable.

**Implication:**  
High traffic alone does not guarantee lower fares. Market structure and route economics still matter.

---

### 4) Load efficiency is informative, but not sufficient alone
Load factor segmentation helps explain operational efficiency, but pricing is not determined by load alone.

**Implication:**  
Airline pricing is multi-factorial: efficiency matters, but so do competition, route distance, and strategic market position.

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
