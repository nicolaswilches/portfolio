---
layout: page
title: "Solar Photovoltaic Generation in Spain: Time Series Modeling and Forecast"
---

### 1. Project Overview

Spain has significantly expanded its renewable energy capacity in the last decade, and solar photovoltaic (PV) is one of the fastest-growing contributors. In this project, I analyze the **monthly evolution of renewable electricity generation in Spain** and develop a **time-series forecasting model** for **solar PV energy sold** up to 2027.

The main goals are:

- To understand how solar PV generation has evolved over time.
- To identify and model its trend and seasonality.
- To build a statistically sound **SARIMA model** and generate a **multi-year forecast**.
- To interpret the results in terms of **operational and policy-relevant insights**.

---

### 2. Data

**Source**

The data comes from the Spanish National Commission on Markets and Competition (CNMC) open data portal:

> Monthly evolution of electricity generated from renewable energies, cogeneration and waste.  
> Energy sold and installed capacity by technology in Spain.

(Original Spanish dataset: "Evolución mensual de energía eléctrica de origen renovable, cogeneración y residuos. Energía vendida y potencia instalada por tecnología.")

**Granularity & Period**

- **Frequency:** Monthly
- **Geographical scope:** Spain (national)
- **Technologies covered:** solar PV, wind, hydro, biomass, waste, cogeneration, etc.
- **Variables (per technology and month):**
  - Energy sold (GWh)
  - Installed capacity (MW)
  - Number of installations

The analysis focuses on the period where the series is complete and consistent, and uses it to fit a model and **forecast 24 months ahead** (through 2027).

**Preprocessing**

Key cleaning and preparation steps:

- API extraction from the CNMC datastore using `requests`.
- Conversion of raw records into a pandas `DataFrame`.
- Standardization of technology names (e.g., mapping original labels to readable categories like *Solar PV*, *Wind*, *Hydro*).
- Conversion of the `date` column to a proper `datetime` index with monthly frequency.
- Aggregation of **energy sold by technology and date** into time series.

---

### 3. Exploratory Analysis

#### 3.1 Metrics considered

For each technology, three main metrics are available:

- **Energy sold** (actual electricity fed into the grid).
- **Installed capacity** (infrastructure size).
- **Number of installations** (count of assets).

From a time series perspective:

- **Installed capacity** and **number of installations** behave like *cumulative infrastructure* — generally upward trending with relatively smooth changes and limited seasonal structure.
- **Energy sold** shows:
  - Clear **seasonal patterns**.
  - Strong **monthly variation**.
  - Dynamics tied to **weather, demand and grid operation**.

Because we are interested in **operational output and seasonal behavior**, the project models **energy sold**, not installed capacity or installation counts.

<div class="chart-container">
<iframe src="/assets/plots/metrics_evaluation.html" width="100%" height="520" loading="lazy"></iframe>
</div>

#### 3.2 Comparing technologies

The dataset covers multiple renewable technologies. I evaluated several series as potential modeling targets:

- **Total renewable energy sold**
- **Wind energy sold**
- **Solar PV energy sold**

These candidates are attractive because:

- They represent a **large share** of Spain's renewable mix.
- Their time series are **long enough** and show **clear trend and seasonality**.
- They are relevant for **policy, grid planning, and investment**.

After comparing behavior across technologies and considering Spain's current energy transition, **Solar PV energy sold** was selected as the primary modeling target:

- It is **one of the fastest-growing series**.
- It exhibits **strong and interpretable seasonality**.
- It is highly relevant for **future renewable expansion**.

<div class="chart-container">
<iframe src="/assets/plots/technologies_comparison.html" width="100%" height="620" loading="lazy"></iframe>
</div>

---

### 4. Time-Series Structure of Solar PV

#### 4.1 Decomposition

Using classical time-series decomposition on the Solar PV energy sold series:

- **Trend component:** shows a clear upward trajectory, consistent with strong growth in installed PV capacity and increasing utilization.
- **Seasonal component:** reveals a **regular annual pattern** with higher generation in sunnier months and lower levels in winter.
- **Residual component:** captures short-term fluctuations and irregular shocks (e.g., unusual weather or demand conditions).

This confirms that Solar PV energy sold is **non-stationary**, with:

- Long-term growth (trend).
- Strong and systematic yearly seasonality.

<div class="chart-container">
<iframe src="/assets/plots/decomposition.html" width="100%" height="920" loading="lazy"></iframe>
</div>

---

### 5. Transformations and Stationarity

To make the series suitable for ARIMA-type modeling, I applied a sequence of transformations.

#### 5.1 Log transformation

A **log transformation** was applied to:

- Stabilize the **variance** (reduce the increasing spread as the series grows).
- Convert a multiplicative seasonal pattern into something closer to **additive**, which ARIMA handles better.

The log-transformed series is more stable but still non-stationary.

#### 5.2 Non-seasonal differencing

Next, I applied **first-order differencing** to the logged series:

- This removes much of the **long-term trend**, making the series fluctuate around a more constant mean.
- The series gets closer to stationarity, but residual seasonal structure persists.

#### 5.3 Seasonal differencing

To address seasonality, I added **seasonal differencing at lag 12** (monthly data with yearly seasonality):

- This explicitly removes recurring yearly patterns.
- After this step, I re-checked stationarity using the **Augmented Dickey–Fuller (ADF) test**.

The final transformed series (log + first difference + seasonal difference at 12):

- Passes the ADF stationarity test.
- Shows no obvious remaining trend or strong remaining seasonal patterns.
- Is appropriately prepared for ARIMA modeling.

<div class="chart-container">
<iframe src="/assets/plots/transformations.html" width="100%" height="920" loading="lazy"></iframe>
</div>

---

### 6. Model Specification: SARIMA

To capture both short-term dynamics and yearly seasonality, I used a **Seasonal ARIMA (SARIMA)** model on the transformed Solar PV series.

The general structure is:

- **SARIMA(p, d, q)(P, D, Q)[s]**
  - `d = 1` (non-seasonal differencing)
  - `D = 1` (seasonal differencing)
  - `s = 12` (monthly seasonality)

#### 6.1 ACF and PACF diagnostics

I examined the **autocorrelation function (ACF)** and **partial autocorrelation function (PACF)** of the transformed series:

- ACF:
  - Strong spike at lag 1, then decaying.
  - Noticeable seasonal pattern at multiples of 12.
- PACF:
  - Strong spike at lag 1, then quickly decreasing.

This pattern suggests:

- Low-order **MA** components to handle short-term noise.
- A **seasonal MA term** to capture yearly dependencies.

<div class="chart-container">
<iframe src="/assets/plots/acf_pacf.html" width="100%" height="920" loading="lazy"></iframe>
</div>

#### 6.2 Model selection

I evaluated a grid of candidate SARIMA models around the patterns seen in ACF/PACF, comparing models using:

- **AIC** (Akaike Information Criterion)
- **BIC** (Bayesian Information Criterion)
- Residual diagnostics (checking remaining autocorrelation and approximate normality).

The selected model is:

> **SARIMA(0,1,1)(0,1,1)[12]**

This model:

- Uses first differences plus seasonal differences.
- Includes a **non-seasonal MA(1)** term.
- Includes a **seasonal MA(1)** term at lag 12.
- Balances **good fit** with **parsimony** (few parameters, interpretable structure).

Residual analysis indicates:

- No major remaining autocorrelation.
- Residuals consistent with a white-noise process.
- The model is statistically adequate for forecasting.

<div class="chart-container">
<iframe src="/assets/plots/residuals_diagnostic.html" width="100%" height="920" loading="lazy"></iframe>
</div>

---

### 7. Forecasting Results

Using the fitted SARIMA(0,1,1)(0,1,1)[12] model on the **log-transformed series**, I generated:

- **In-sample fitted values** (back-transformed to original units).
- **Out-of-sample forecasts** for the next **24 months**.
- **95% confidence intervals** around the forecast.

After exponentiating the predictions back to the original scale:

- The model closely tracks the **historical Solar PV series**, reproducing:
  - The growth trajectory.
  - The regular yearly peaks and troughs.
- The **forecast** shows:
  - Continued **upward trend** in solar PV generation.
  - Seasonal peaks that grow higher over time (reflecting both increased capacity and persistent seasonality).
  - Notable growth into 2026–2027, with summer peaks substantially higher than those observed at the start of the sample.

The confidence bands:

- Stay reasonably tight in the short term.
- Widen as the horizon extends, reflecting **increasing uncertainty** typical of multi-step ahead forecasts.

<div class="chart-container">
<iframe src="/assets/plots/forecast_trimmed.html" width="100%" height="620" loading="lazy"></iframe>
</div>

---

### 8. Interpretation and Implications

#### 8.1 Operational and business implications

The forecast suggests that:

- Solar PV will continue to **increase its contribution** to Spain's electricity mix.
- Seasonal peaks in generation will become **larger and more pronounced**, especially in summer months.

This has several practical consequences:

- **Grid operators** need to anticipate higher solar output during peak months and adjust dispatch, storage, and backup resources.
- **Storage and flexibility solutions** (batteries, demand response, interconnections) become more valuable as solar's seasonal and intrayear variability increases.
- **Investors and policymakers** can use these forecasts as a baseline scenario when planning infrastructure, incentives, and integration with other renewables.

#### 8.2 Methodological implications

From a modeling perspective:

- A relatively **simple SARIMA(0,1,1)(0,1,1)[12]** model, correctly specified and diagnosed, can capture:
  - Long-term growth (via differencing and back-transformation).
  - Strong yearly seasonality (via seasonal components).
  - Short-term dynamics (via MA terms).
- Time-series diagnostics (stationarity tests, ACF/PACF) are crucial: blindly fitting an ARIMA to a raw trending, seasonal series would violate assumptions and produce misleading forecasts.

---

### 9. Limitations and Next Steps

#### 9.1 Limitations

Despite its good statistical behavior, the model has important limitations:

- It is **purely univariate**:
  - Does not explicitly include exogenous drivers such as weather, policy changes, electricity prices, or installed capacity.
- It assumes that **historical patterns will continue**:
  - Structural breaks (e.g., new regulations, shocks in energy markets) are not modeled explicitly.
- The forecast uncertainty grows with horizon:
  - Long-term forecasts (several years ahead) should be interpreted as **scenarios**, not precise predictions.

#### 9.2 Future improvements

Potential extensions:

- Upgrade to **SARIMAX** (ARIMA with exogenous variables) by adding:
  - Installed PV capacity.
  - Solar radiation or climate indicators.
  - Policy dummy variables (e.g., major subsidy schemes).
- Explore **nonlinear or machine learning models** (e.g., gradient boosting, RNNs) and compare to SARIMA as a baseline.
- Perform **scenario analysis**:
  - Different capacity expansion paths.
  - Different climate or demand assumptions.
- Build a small **dashboard** to visualize historical data and forecast scenarios interactively.

---

### 10. Code and Notebook

- **Full interactive notebook:** [View complete analysis notebook](/notebooks/solar-pv-spain-forecast.html)
- **GitHub repository:** [nicolaswilches/portfolio](https://github.com/nicolaswilches)

The notebook includes:

- Full data extraction from the CNMC API.
- Cleaning and transformation steps.
- All exploratory plots, decompositions, and diagnostics.
- SARIMA model selection, fitting, residual checks, and forecast visualization.