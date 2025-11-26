# Urban Informatics Approach **Research Proposal: Sofia Residential Real-Estate Pricing & Risk Map**

## 1. Introduction & Research Framing

**Overall Aim**

To construct a data-driven **Pricing & Risk Map** for the Sofia residential real estate market that:

1. **Models** apartment prices as a function of structural and district-level location attributes.
2. **Identifies** spatial inefficiencies (districts that appear over- or undervalued relative to their fundamentals).
3. **Quantifies** investment risk using **gross price-to-rent ratios (yields)** at the district level and classifies districts into risk quadrants.

The project follows an **urban informatics** approach: using large-scale, listing-level data from real estate portals combined with official statistics (NSI, Eurostat, agency reports) to produce insights that go beyond traditional city-level averages.

---

## 2. Literature Survey & Conceptual Framework

Before data collection, the project will establish a theoretical and empirical basis by reviewing:

- **Conceptual Literature**
    - **Hedonic Pricing Theory** (Rosen, 1974) to justify modeling price as a function of structural (size, rooms, floor, age) and locational (district) characteristics.
    - Urban economics work on **location premiums**, accessibility, and neighborhood quality.
- **Empirical Literature (Post-Socialist & Sofia-Specific)**
    - Studies on **post-socialist suburbanisation and urban sprawl** in Sofia and other capitals in the region (e.g. Sofia + Belgrade), documenting the shift from panel housing to new suburban/gated developments under weak planning and strong market pressure.[[ResearchGate]](https://www.researchgate.net/publication/262223390_Sprawling_Sofia_Post-socialist_Suburban_Growth_in_the_Bulgarian_Capital?utm_source=chatgpt.com)
    - Empirical work on **Sofia’s housing market and urban form**, including analyses of urban sprawl, market-driven development, and the tension between planning goals and market demand, as well as newer work on accessibility and the “15-minute city” / walkability in Sofia. [[ResearchGate]](https://journal.vfu.bg/bg/pdfs/Aleksandar_Slaev-Market_Analysi_of_Urban_Sprawl_in_Sofia.pdf?utm_source=chatgpt.com)
    - Methodological papers using **hedonic pricing and spatial econometrics (incl. GWR)** for housing markets in Eastern European cities (e.g. Warsaw) and elsewhere; these provide the econometric toolkit and typical model specifications. Because our data lacks exact coordinates, we adopt the **district-fixed-effects hedonic approach** rather than full spatial lag/error or GWR models.[[Hedonic Approach]](https://www.researchgate.net/publication/227450840_An_Application_of_Spatial_Econometrics_in_Relation_to_Hedonic_House_Price_Modeling?utm_source=chatgpt.com)
- **Gap Analysis**
    - Local market reports (e.g., Bulgarian Properties, address.bg, imot.bg) mostly provide aggregated average prices by city or broad area and qualitative commentary.
    - There is little published evidence using granular, listing-level data for Sofia to:
        - Formally estimate hedonic price models,
        - Derive residual-based over/under-valuation per district,
        - Combine this with yield metrics into a coherent risk map.
    - This project fills that gap by:
        - Scraping apartment-level offers,
        - Estimating a transparent hedonic model,
        - Aggregating results to produce district-level pricing and risk indicators.

---

## 3. Research Questions & Hypotheses

### R1 - Pricing Fundamentals

> **RQ1**: Which structural attributes (size, rooms, vertical position, new vs old build, heating) and district-level location explain variation in apartment prices across Sofia?
> 

**H1:** 

- After controlling for structural characteristics (area, rooms, floor, newbuild, heating), district dummies are jointly significant and explain a substantial share of residual variation.
- Central and high-status districts are expected to exhibit positive price premiums relative to a baseline peripheral district.

### R2 - Market Efficiency

> **RQ2**: Are specific districts significantly over- or undervalued relative to their structural fundamentals?
> 

**H2:**

- Some central / prestigious areas (e.g. Lozenets, parts of Sredets / Triaditsa) will show positive average residuals (buyers pay a premium beyond what the model predicts from structure alone).
- Some rapidly developing peripheral districts with large new supply may show negative average residuals, suggesting potential undervaluation or slower demand catch-up.

### R3 - Investment Risk & Yield Analysis

> **RQ3**: How do gross rental yields vary across districts, and how does combining yield and valuation (residuals) indicate potential speculative or defensive investment zones?
> 

**H3:**

- Districts with low yields and positive residuals (high price, low income support) will occupy a “Speculative Bubble” quadrant.
- Districts with high yields and negative residuals (relatively cheap but strong rent) will appear as “Undervalued Gems”.
- The remaining combinations (high price / high yield, low price / low yield) correspond to “Cash Cows” and “Value Traps.”

---

## 4. Research Design & Data Strategy

### 4.1 Sampling Design & Justification

- **Universe (for primary data):**
    
    Advertised **residential apartment sale offers** in **Sofia City** on `imot.bg`.
    
- **Scope Restriction - Room Count:**
    - Include only **1-room, 2-room, and 3-room** apartments.
    - Exclude 4+ room apartments and **maisonettes** (different market segment, fewer comparable units).
- **Sampling Method:**
    
    **Non-probability convenience sampling** through systematic web scraping of all matching sale listings on `imot.bg` within the relevant time window.
    
- **Why Custom Data Collection?**
    - Public datasets (NSI, Eurostat, etc.) provide **indices and aggregated averages**, but **not** listing-level structural attributes such as:
        - Floor, rooms, construction type, heating,
        - New vs old build, district mapping at apartment level.
    - Hedonic regression requires these **micro-level attributes** to disentangle structural vs location effects.
    - For RQ3, granular **relative price levels** per district are needed; official rent and price series exist but are not directly linked to individual listings.
- **Buy-Sell Spread Disclaimer:**
    - The analysis uses **asking prices**, not final transaction prices.
    - Interviews and literature suggest that **most deals close with a small discount** (roughly on the order of a few percentage points), but:
        - This spread varies **widely** by location, property type, urgency, and market conditions.
        - Sellers typically do **not** update the advertised price to reflect the negotiated price just before closing.
    - Therefore, we **do not attempt to explicitly estimate or correct** for the ask-bid spread. It is treated as a small noise component; our focus is on **relative differences between districts**, not absolute levels.

### 4.2 Data Collection Sources

1. **Primary Data - Granular Listings (Sales Only):**
    - **Source:** `imot.bg` (Sofia, apartments, for sale).
    - **Target:** All Sofia sale listings for 1/2/3-room apartments ~O(3K) 
    - **Key Variables (per listing):**
        - `price` (asking price, later unified in EUR),
        - `area` (m²),
        - `rooms` (1/2/3), parsed from heading,
        - `district` (standardized from raw neighborhood string),
        - `floor` (numeric),
        - `is_ground_floor`, `is_top_floor` (derived from `floor` and total floors),
        - `heating` (categorical: district/gas/electric/other),
        - `construction_type` (e.g. panel, brick, EPK, other),
        - `newbuild` (0/1 indicator based on construction year / “new build” labels).
2. **Secondary Data - Official & Market Context:**
    - **NSI (National Statistical Institute of Bulgaria):**
        - **Housing Price Index (HPI):** Quarterly indices (national and Sofia-specific) to validate overall price trend and contextualize scraped price levels.
        - **Building Permits / New Dwellings:** Aggregated data on permits issued and dwellings completed (city-level; district-level if available) as a proxy for **supply dynamics** (used mainly for discussion, not directly in the main model).
        - **Income / Affordability Indicators:** Average income for Sofia used qualitatively to discuss affordability (if available at suitable granularity).
    - **Eurostat:**
        - Housing price indicators and urban statistics (for **context and comparison**) - e.g. how Bulgaria’s house price growth compares to EU averages.
    - **Local Market Reports / Portals:**
        - **Imot.bg**, **Bulgarian Properties**, **Colliers**, **Address.bg**, etc.:
            - Aggregated **average sale prices per m²** and **average rents per m²** by district or broader area for Sofia.
            - These are used to:
                - Cross-check and calibrate scraped price levels.
                - Provide **district-level rent estimates** for **gross yield** calculation in RQ3 (no rental listings scraping is planned).
    - **Spatial Layers (for Mapping Only):**
        - **Sofia district boundaries** (shapefile / GeoJSON) for visualizing district-level results as maps (no point-level geocoding; we only operate at district granularity).
    - **Note:**
        - Fine-grained district-level data (e.g., income or permits per district) may not be fully available. Where such data is missing, we rely on city-wide values or a qualitative discussion, rather than forcing these variables into the regression.

---

## 5. Methodology

### 5.1 Data Processing & Pilot Study
- **Outlier Detection:**
    - Remove extreme values (e.g., implausibly low prices per m², suspiciously small or huge areas) based on simple rules / Z-scores.
- **Feature Engineering (Final Modeling Dataset):**
    - Convert `price` to EUR (if necessary) and take **log(price)** for modeling.
    - Convert `area` to numeric m² and use **log(area)** as main size variable.
    - Parse `rooms` (1, 2, 3) from listing heading.
    - Parse `floor` and total floors; create:
        - `is_ground_floor` (0/1),
        - `is_top_floor` (0/1).
    - Clean `heating` into a small set of categories.
    - Map `construction_type` and derive `newbuild` (0/1).
    - Normalize `district` names to a finite set of standard district labels.

The final `processed.csv` contains one row per listing with these standardized variables, treating the dataset as a **cross-sectional snapshot** (no time dimension)

---

## 5.2 Hedonic Regression (RQ1)

**Objective:** Quantify how much of the variation in apartment prices can be explained by structural characteristics vs. district-level location.

We use a semi-log OLS model:

$\ln(P_i) = \alpha + \beta_S' S_i + \beta_L' L_i + \varepsilon_i$

Where:

- $P_i$: asking price of apartment i
- $S_i$: vector of structural attributes (area, rooms, floor, ground/top flags, newbuild, heating)
- $L_i$: vector of locational attributes (district dummies)
- $\varepsilon_i$: error term

**Baseline (Structure-Only) Model**

$$
\ln(P_i) =\beta_0+ \beta_1 \ln(\text{area}_i)+ \beta_2 \,\text{rooms}_i+ \beta_3 \,\text{floor}_i+ \beta_4 \,gf_i+ \beta_5 \,tf_i+ \beta_6 \,\text{newbuild}_i+ \sum_h \gamma_h \,\text{heat}_{i,h}+ \varepsilon_i
$$

**Location-Augmented Model (District Fixed Effects)**

$$
\ln(P_i) =\beta_0+ \beta_1 \ln(\text{area}_i)+ \beta_2 \,\text{rooms}_i+ \beta_3 \,\text{floor}_i+ \beta_4 \,gf_i+ \beta_5 \,tf_i+ \beta_6 \,\text{newbuild}_i+ \sum_h \gamma_h \,\text{heat}_{i,h}+ \sum_d \delta_d \,\text{district}_{i,d}+ \varepsilon_i
$$

- One district is omitted as baseline (e.g. a peripheral district).
- Each  $\delta_d$  is a **location premium/discount** relative to that baseline, after controlling for structure.

**Evidence for RQ1 (“location matters”):**

- Compare R² / adjusted R² between the baseline and location-augmented models.
- Run a joint F-test of all district dummies: rejecting the null (all  $\delta_d$  = 0) means **district location significantly improves model fit** beyond structural attributes.

---

## 5.3 Residual-Based Over/Undervaluation (RQ2)

**Objective:** Identify districts where prices are systematically above or below what fundamentals predict.

From the location-augmented model:

- For each listing i:
    - Predicted log price: $\ln(\hat{P}_i)$
    - Residual (log-scale deviation):

$e_i = \ln(P_i) - \ln(\hat{P}_i)$

Interpretation:

- $e_i$ > 0 → apartment is **overpriced** relative to structure and district
- $e_i$ < 0 → apartment is **underpriced**

Aggregate by district d:

$\overline{e}_d = \frac{1}{N_d} \sum_{i \in d} e_i$

Where:

- $\overline{e}_d$: mean residual in district d
- $N_d$: number of listings in district d

Interpretation:

- $\overline{e}_d$ > 0 → district is, on average, **overpriced**
- $\overline{e}_d$ < 0 → district is, on average, **underpriced**

This $\overline{e}_d$ is the **valuation metric** used to answer RQ2 and as an input to the risk quadrants in RQ3.

---

## 5.4 Risk & Yield Mapping (RQ3)

**Objective:** Combine valuation (from RQ2) with cash flow (gross rental yield) to classify districts into risk quadrants.

### 1. Construct District-Level Panel

For each district d, we gather:

- Median sale price per m² (from `processed.csv` and/or official/agency data)
- Median rent per m² (from external aggregate sources such as imot.bg stats, agency reports, NSI)
- Mean residual $\overline{e}_d$ from RQ2

### 2. Gross Rental Yield

For each district d:

$$
⁍
$$

where:

- ${\text{Median annual rent per } m^2_d}$ = median monthly rent per m² in district d * 12

### 3. Quadrant Classification

Compute reference levels:

- $\overline{Yield}$ = average or median $Yield_d$ across districts
- $\overline{e}$ = average or median $\overline{e}_d$ across districts

Then classify each district:

- **Speculative Bubble:**
    - $Yield_d$ < $\overline{Yield}$ and $\overline{e}_d$ > $\overline{e}$
        
        → high price, low yield; expensive relative to both cash flow and fundamentals.
        
- **Cash Cow:**
    - $Yield_d$ > $\overline{Yield}$ and $\overline{e}_d$ > $\overline{e}$
        
        → high entry price but strong cash flow; established high-demand areas.
        
- **Value Trap:**
    - $Yield_d$ < $\overline{Yield}$ and $\overline{e}_d$ < $\overline{e}$
        
        → cheap but weak rental performance; demand issues.
        
- **Undervalued Gem:**
    - $Yield_d$ > $\overline{Yield}$ and $\overline{e}_d$ < $\overline{e}$
        
        → relatively cheap and strong income; potentially attractive for investors.
        

### 4. Visualization

- Scatter plot (or map) of districts:
    - X-axis: $Yield_d$
    - Y-axis: $\overline{e}_d$
- Draw:
    - Vertical line at $\overline{Yield}$
    - Horizontal line at $\overline{e}$
- Color points by quadrant.

---

### 6. Execution Plan

1. **Phase 1: Feasibility & Setup**
    - Literature review & gap analysis (**done**).
    - Identify and download key NSI / Eurostat / agency data (**HPI, aggregate prices & rents**).
    - Define the final modeling schema (variables we can reliably extract).
    - Run a **pilot scrape + clean** of ~1K listings to validate extraction and cleaning rules.
2. **Phase 2: Data Engineering**
    - Perform full scraping run for **sale listings** (1/2/3 room apartments).
    - Combine and clean all raw files into a single `processed.csv`.
    - Generate district-level sale price metrics (median price per m²).
3. **Phase 3: Modeling & Analysis**
    - Estimate **baseline** and **location-augmented** hedonic models with `statsmodels`.
    - Compute listing-level residuals and district-level **mean residuals** (RQ2).
    - Merge in **district-level rent and price benchmarks** from official/agency sources.
    - Compute **gross rental yields** and construct the **Risk & Yield Map** (RQ3).
4. **Phase 4: Reporting & Interpretation**
    - Produce visualizations: regression diagnostics, district premiums, residual maps, risk quadrants.
    - Write the final report, explicitly answering RQ1-RQ3 and discussing limitations (asking price data, spread, sample selection).

# Methodology Deep Dive: Modeling & Analysis

This document details the mathematical and statistical approach for the Sofia Residential Real Estate Pricing & Risk Map. Read if aquainted with file above

---

## 1. Phase 1: Data Collection & Engineering

**Objective:** Build a clean listing-level dataset for the Hedonic Model (RQ1) by collecting apartment **sale** offers from `imot.bg` and transforming them into a standardized `processed.csv`.

### 1.1 Step 1: The Setup (Targeting the Market) - `src/scraping`

We first define **exactly which part of the market** we are studying.

- **Portal:** `imot.bg` - section for **apartments for sale** in **Sofia City**.
- **Rooms (very important):**
    - We only consider **1-room, 2-room, and 3-room** apartments.
    - 4+ room apartments and мезонети are **excluded** from this research.
- **Example base URL for 1-room apartments in Sofia:**
    
    ```
    https://www.imot.bg/obiavi/prodazhbi/grad-sofiya/ednostaen?type_home=2~3~
    ```
    
    (Similar URLs exist for 2-room and 3-room apartments; we will maintain three base URLs, one per room count.)
    
- **Filters:**
    - Location: **гр. София** (Sofia City only, no villages/области).
    - Type: **Апартаменти**.
    - Market: **Продажби**.

These URLs define our **search territory**. The scraper will iterate separately over the 1-room, 2-room, and 3-room search result pages.

---

### 1.2 Step 2: The Crawling Strategy (Handling the Lists)

For each of the three base URLs (1-, 2-, 3-room), we design a polite crawler.

- **Pagination Handling:**
    - The search results for each category are spread across multiple pages.
    - For each category:
        1. Load page 1.
        2. Collect all listing URLs on that page.
        3. Detect and follow the “Next page” link (or increment a `page=` parameter).
        4. Stop when no further pages exist.
- **Politeness / Rate Limiting:**
    - It appears there is no rate limiting to the website, so we don't need to account for that.

Output of this step (per category): a list of **apartment detail URLs**.

---

### 1.3 Step 3: Variable Extraction (Listing-Level Features)

For each listing URL, we load the detail page and extract a fixed set of variables using **structured fields** and minimal **pattern parsing**.

We now know the room count from the **category and heading**, so room parsing is straightforward.

### Raw Extraction Schema (per listing)

We aim to capture:

- `url`
- `price_raw`
- `area_raw`
- `rooms` (1, 2, or 3 - from heading)
- `district_raw`
- `floor_raw`
- `max_floor_raw` (if available)
- `heat_raw`
- `construction_raw`
- `year_raw` (if present, from Act 16 / description)
- `desc_text` (optional, for later debugging / robustness)

### Extraction Matrix (logic)

| Variable | Extraction Method | Explanation |
| --- | --- | --- |
| **URL** | Structured | Direct link to the listing, used as an identifier (together with source). |
| **Price** | Structured | Read the main price field (e.g. “200 000 EUR”). Strip spaces and currency, keep numeric value in `price_raw` and the currency code separately if needed. |
| **Area (Size)** | Structured | Read the “Quadrature / Area” field. Remove “кв.м” and convert to numeric `area_raw` (m²). |
| **Rooms** | Structured via Heading | The heading contains patterns like “Продава 1-СТАЕН”, “Продава 2-СТАЕН”, “Продава 3-СТАЕН”. We parse the digit (`1`, `2`, `3`) and store it as integer `rooms`. Since the base URL already filters for ednostaen/dvustaen/tristaen, this is robust. |
| **District (raw)** | Structured | Read the location breadcrumb or field (e.g. “гр. София, кв. Лозенец”). Extract the neighborhood/district into `district_raw`. |
| **Floor (raw)** | Pattern | Parse strings like “ет. 3 от 8”, “етаж 5/9”. Extract current floor (`3`, `5`) as `floor_raw` and total floors (`8`, `9`) as `max_floor_raw` if present. |
| **Heating (raw)** | Structured / Keywords | Use the heating field if available; otherwise scan for typical heating terms (“ТЕЦ”, “газ”, “електрическо”, “климатик”, etc.) and store original category in `heat_raw`. |
| **Construction (raw)** | Structured / Keywords | Read construction type: “тухла”, “панел”, “ЕПК”, “ново строителство”, etc., into `construction_raw`. |
| **Year (raw)** | Pattern | Search for “Акт 16” followed by a 4-digit year (e.g. “Акт 16 2022”) or phrases like “строеж 2015 г.”. Use this to later derive a `newbuild` indicator. |
| **Description** | Raw text | Store `desc_text` for potential fallback parsing (optional). |

Note: We **do not** store listing time variables (listing date, scrape date) for modeling purposes. We treat this dataset as a **cross-sectional snapshot** of the market.

---

### 1.4 Step 4: Data Safety & Incremental Saves

- After parsing each listing, we **immediately append** its row to a raw CSV (`data/raw/raw_sofia_partX.csv`).
- No dependency on a giant in-memory list: if the scraper stops unexpectedly, previously written rows remain safe.
- On restart, we can:
    - Read existing raw CSVs,
    - Extract already-scraped URLs,
    - Skip them and continue.

This makes the scraping process robust to crashes / interruptions.

---

### 1.5 Step 5: Data Cleanup & Consolidation - `src/processing`

Once all raw CSVs are collected, we run a dedicated **processing** pipeline.

### 1.5.1 Combine Raw Files

- Script: `src/processing/combine.py`
    - Load all `data/raw/raw_*.csv`.
    - Concatenate into a single DataFrame.
    - Drop exact duplicates based on key fields (e.g. `url`, `price_raw`, `area_raw`).

### 1.5.2 Cleaning & Feature Engineering

- **Price:**
    - Parse `price_raw` to numeric (`price`).
    - If needed, convert BGN to EUR using a fixed rate (store only `price_eur`).
- **Area:**
    - Convert `area_raw` to numeric `area_m2`.
- **Rooms:**
    - Ensure `rooms` is integer 1 / 2 / 3 (by design of the scrape).
    - Listings that somehow end up as 4+ or мезонет are dropped in this phase.
- **Floor & Floor Flags:**
    - Parse `floor_raw` to integer `floor` where possible.
    - Parse `max_floor_raw` to integer `max_floor` when available.
    - Derive:
        - `is_ground_floor` = 1 if `floor == 0` or synonym (e.g. “партер”), else 0.
        - `is_top_floor` = 1 if `max_floor` is known and `floor == max_floor`, else 0.
- **Heating:**
    - Map `heat_raw` into a small set of categories, e.g.:
        - `"district"` (ТЕЦ),
        - `"gas"`,
        - `"electric"`,
        - `"other"`.
    - Store cleaned value as `heat`.
- **Construction & New/Old:**
    - From `construction_raw` and `year_raw`, derive:
        - `construction_type` (e.g. `"panel"`, `"brick"`, `"epk"`, `"other"`).
        - `newbuild` (1 if year is recent or labelled “ново строителство” or similar; otherwise 0).
    - If no evidence of being new, default to `newbuild = 0`.
- **District Naming:**
    - Map `district_raw` strings to a standardized `district` label (e.g. “Lozenets”, “Lyulin”, “Mladost”).
    - This is crucial for grouping and district dummies later.

### 1.5.3 Modeling Dataset Output

Save a final cleaned dataset `data/processed/processed.csv` with (at least) the following columns:

- `price_eur`
- `area_m2`
- `rooms`
- `floor`
- `is_ground_floor`
- `is_top_floor`
- `heat` (cleaned categorical)
- `newbuild` (0/1)
- `construction_type` (optional, if used)
- `district`

This is the **input** for RQ1 and RQ2. RQ3 will use **aggregated district-level** statistics derived from this file plus official rent/price data.

---

## 2. Hedonic Price Modeling (RQ1: Micro View)

**Objective:** Quantify how structural attributes and district location contribute to apartment prices and isolate the **location premium**.

We adopt a semi-log OLS specification: dependent variable = log(price).

### 2.1 Econometric Specification

For each listing *i*:

- $P_i$ – asking price in EUR
- $area_i$ – area in m²
- $rooms_i$ ∈ {1, 2, 3} – number of rooms
- $floor_i$ – floor number (when available)
- $gf_i$ – `is_ground_floor` dummy (1 if ground floor, else 0)
- $tf_i$ – `is_top_floor` dummy (1 if top floor, else 0)
- $newbuild_i$ – 1 if new construction, 0 otherwise
- $heat_{i,h}$ – heating category dummies
- $district_{i,d}$ – district dummies

General semi-log model:

$ln(P_i) = alpha + beta_S' * S_i + beta_L' * L_i + epsilon_i$

where $S_i$  is the vector of structural attributes and $L_i$ is the vector of location (district) dummies.

### 2.1.1 Baseline Structural Model

No explicit location; only physical/structural factors:

$$
\ln(P_i) =\beta_0+ \beta_1 \ln(\text{area}_i)+ \beta_2 \,\text{rooms}_i+ \beta_3 \,\text{floor}_i+ \beta_4 \,gf_i+ \beta_5 \,tf_i+ \beta_6 \,\text{newbuild}_i+ \sum_h \gamma_h \,\text{heat}_{i,h}+ \varepsilon_i
$$

This model explains how much of price is driven by **size, rooms, vertical position, building age, and heating** without any location information.

### 2.1.2 Location-Augmented Model (District Effects)

Add district fixed effects to capture pure location premiums:

$$
\ln(P_i) =\beta_0+ \beta_1 \ln(\text{area}_i)+ \beta_2 \,\text{rooms}_i+ \beta_3 \,\text{floor}_i+ \beta_4 \,gf_i+ \beta_5 \,tf_i+ \beta_6 \,\text{newbuild}_i+ \sum_h \gamma_h \,\text{heat}_{i,h}+ \sum_d \delta_d \,\text{district}_{i,d}+ \varepsilon_i
$$

- One district (e.g. Lyulin) is omitted as baseline.
- Each $\delta_d$ is a **location premium/discount** relative to that baseline, controlling for structural factors.

**Interpretation examples:**

- `rooms` coefficient: additional % effect per extra room, holding area fixed (if you keep it as numeric).
- `is_ground_floor`: negative coefficient → ground-floor units sell at a discount vs otherwise similar non-ground units.
- `is_top_floor`: positive or negative depending on market preferences.
- `newbuild`: e.g. 0.18 ≈ **+18%** price for new construction, all else equal.
- `C(district)[T.Lozenets]`: 0.40 → **≈+40%** vs baseline district after controlling for structure.

**RQ1 (“location matters”) evidence:**

- Compare `R²` / adj `R²` of `model_baseline` vs `model_loc`.
- F-test for all district dummies jointly = 0; strong rejection = location significantly improves explanatory power.

---

## 3. Identifying Spatial Inefficiencies (RQ2: Residuals)

**Objective:** Identify which districts appear overpriced or underpriced relative to **their structural characteristics**.

### 3.1 Residuals from Location Model

From the location-augmented model:

- Let $\hat{P}_i$ be the predicted price of listing i.
- Define **log residual**:
    
    $e_i = ln(P_i) − ln(\hat{P}_i)$
    
- $e_i$ > 0 → actual > predicted → **overpriced listing**
- $e_i$ < 0 → actual < predicted → **underpriced listing**

### 3.2 District-Level Aggregation

Aggregate residuals per district ddd:

$\overline{e}_d = \frac{1}{N_d} \sum_{i \in d} e_i$ 

where:

- $\overline{e}_d$ – mean residual in district d
- $N_d$ – number of listings in district d

Interpretation:

- $\overline{e}_d$ > 0 → district is, on average, **overpriced**
- $\overline{e}_d$ < 0 → district is, on average, **underpriced**

This $\overline{e}_d$ is the **valuation metric** used in RQ2 and as the **Y-axis** in RQ3.

---

## 4. The Risk Map (RQ3: Macro View)

**Objective:** Classify districts into risk profiles by combining:

- **Cash flow**: Gross rental yield per district.
- **Valuation**: Over/under-pricing signal from RQ2.

### 4.1 Inputs (District-Level)

For each district ddd, we obtain:

1. **Sale price side** - median/average sale price per m²:
    - Derived from `processed.csv` (scraped offers) and/or official/agency aggregates.
2. **Rent side** - median/average rent per m²:
    - From **external data** (NSI, imot.bg rental statistics, agency reports).
    - We do **not** scrape rents in this project; we treat this as an official 2025 snapshot.
3. **Valuation signal** - mean residual $\overline{e}_d$ from RQ2.

### 4.2 Yield Formula

$$
⁍
$$

Where ${\text{Median annual rent per } m^2_d}$ = median monthly rent per m² in district d * 12

### 4.3 Quadrant Classification

On a scatter plot:

- **X-axis:** $Yield_d$ (cash flow).
- **Y-axis:** $\overline{e}_d$ (valuation).

Define city-wide thresholds:

- $\overline{Yield}$ = overall mean or median $Yield_d$
- $\overline{e}$ = overall mean or median of $\overline{e}_d$ (often close to zero)

Quadrants:

Then classify each district:

- **Overvalued Low Yield:**
    - $Yield_d$ < $\overline{Yield}$ and $\overline{e}_d$ > $\overline{e}$
        
        → high price, low yield; expensive relative to both cash flow and fundamentals.
        
- **High Price High Yield:**
    - $Yield_d$ > $\overline{Yield}$ and $\overline{e}_d$ > $\overline{e}$
        
        → high entry price but strong cash flow; established high-demand areas.
        
- **Low Price Low Yield:**
    - $Yield_d$ < $\overline{Yield}$ and $\overline{e}_d$ < $\overline{e}$
        
        → cheap but weak rental performance; demand issues.
        
- **Undervalued High Yield:**
    - $Yield_d$ > $\overline{Yield}$ and $\overline{e}_d$ < $\overline{e}$
        
        → relatively cheap and strong income; potentially attractive for investors.
        

| Quadrant | Condition | Interpretation |
| --- | --- | --- |
| Overvalued Low Yield | $Yield_d$ < $\overline{Yield}$ and $\overline{e}_d$ > $\overline{e}$
high price, low yield | High risk - high price / low income support. |
| High Price High Yield | $Yield_d$ > $\overline{Yield}$ and $\overline{e}_d$ > $\overline{e}$
high price, high yield | Moderate risk - expensive but strong cash flow. |
| Low Price Low Yield | $Yield_d$ < $\overline{Yield}$ and $\overline{e}_d$ < $\overline{e}$
low price, low yield | Moderate risk - cheap but poor rental performance. |
| Undervalued High Yield | $Yield_d$ > $\overline{Yield}$ and $\overline{e}_d$ < $\overline{e}$
low price, high yield | Low risk - attractive entry price + strong cash flow. |

### 4.4 Visualization

- Plot each district as a point (X = yield, Y = valuation residual).
- Produce a scatter plot with:
    - X = $Yield_d$
    - Y = $\overline{e}$
    - Each point = one district, optionally labeled.
    - Color points by quadrant(optional again)

This delivers the final **Risk & Yield Map** for Sofia’s districts, grounded in:

- Micro-level hedonic modeling (RQ1),
- Residual-based over/under-valuation (RQ2),
- Yield + valuation quadrant classification (RQ3).

### 5. Project Structure

```
sofia-real-estate-risk-map/
│
├─ README.md               # methodology, limitations, current progress
├─ literature_review.md    # conceptual and empirical notes
├─ data/
│   ├─ raw/                # raw scraped CSVs (sale listings)
│   ├─ official/           # NSI, Eurostat, agency reports
│   └─ processed/          # cleaned modeling tables (done.csv, dist_metrics.csv)
│
├─ notebooks/
│   ├─ 01_scrape_execution.ipynb    # scraping logic & monitoring
│   ├─ 02_clean_and_engineer.ipynb  # cleaning, feature engineering
│   ├─ 03_hedonic_modeling.ipynb    # RQ1 & RQ2: regressions + residuals
│   └─ 04_risk_yield_mapping.ipynb  # RQ3: yield calculation & risk map
│
├─ src/
│   ├─ scraping/                  # scrapers for imot.bg
│   ├─ processing/                # combine + clean + feature engineering
│
└─ reports/                       # exported charts, maps, final write-ups
```

---

### 6. Tech Stack (Consolidated)

The project will rely on a **Python-only** stack:

- **Data Engineering:**
    - `pandas`, `numpy`, `beautifulsoup4`, `requests`.
- **Econometrics / Statistics:**
    - `statsmodels` (OLS regression, inference).
- **Visualization:**
    - `matplotlib`, `plotly`.
- **(Optional, not implemented yet) ML Extensions:**
    - `scikit-learn` (if we want to compare hedonic OLS against simple ML regressors as a robustness check).

## Result

This final **Risk & Yield Map** allows us to:

- See which districts look speculative, balanced, or undervalued.
- Connect back to the narrative: location matters, some areas are mispriced relative to fundamentals, and investors face different risk profiles depending on where they buy.
