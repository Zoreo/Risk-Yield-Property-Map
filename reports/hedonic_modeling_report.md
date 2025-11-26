# Sofia Hedonic Modeling Summary

## Data sources
- `data/processed/processed.csv`: cleaned imot.bg sales listings.
- `data/processed/district_residuals.csv`: district-level mean log-price residual from the district-augmented model.
- `data/processed/district_effects.csv`: district fixed effects (premiums/discounts).

## OLS results

**Baseline structural model (no district FEs)**  
Dep. Variable: `log_price`  
R² = 0.735, Adj R² = 0.734, F-statistic = 863.4 (p<0.001), Log-Likelihood = 18.07, AIC = -16.14, BIC = 43.26.  
Key coefficients:
- `log_area` ≈ 0.707: a 1% bigger apartment raises price by ~0.7%.
- `rooms` ≈ 0.129: each additional room adds ~13% to the asking price, controlling for area.
- `floor` ≈ 0.0075; `is_top_floor` ≈ -0.0885; `is_ground_floor` ≈ 0: vertical position still matters (top floors discounted, higher floors slightly premium).
- `newbuild` ≈ -0.2127 and construction dummies (panel, epk) remain large negatives (~-20% to -23%), showing new/build materials are priced below mature stock.
Residual diagnostics: Omnibus=84.12, Jarque-Bera=130.26, Prob(JB)=5.17e-29, Skew=0.285, Kurtosis=3.888, Durbin-Watson≈0.99—there is mild skew/kurtosis but little serial correlation.

**District-augmented model**  
R² = 0.844, Adj R² = 0.838, F-statistic = 134.1 (p<0.001), Log-Likelihood = 761.97, AIC = -1304.0, BIC = -650.6.  
Adding district fixed effects improves fit by ~11 percentage points, meaning most remaining variation after structural controls is spatial.  
Key changes:
- `log_area` stays high (~0.68) and room/floor controls remain positive, so apartment geometry still dominates price.
- `newbuild` shrinks to -0.0938 but remains negative, reflecting that new developments still come with slightly lower per-m² tags even after controlling for district.
- Panel/EPK coefficients move toward zero, indicating their prior effects were largely driven by the neighborhoods where those buildings cluster.
- District premiums: central neighborhoods (Докторски паметник, Център, Лозенец, Изток, Иван Вазов, Медицинска академия, Яворов) deliver log-price boosts of 0.3–0.6, while peripheral districts like Люлин variants, Обеля, Модерно предградие, Суходол, Левски stay significantly negative.
Diagnostics: Omnibus=116.39, Jarque-Bera=329.47, Prob(JB)=2.86e-72, Skew=0.142, Kurtosis=4.654, Durbin-Watson=1.211; the residual distribution tightens once location is absorbed.

## Interpretation notes
- **R² jump (0.73 → 0.84)**: adding district fixed effects captures ≈11% of price variation, so geography still drives a sizeable chunk beyond the structural controls.
- **Area comes first**: log(area) is the strongest predictor (≈0.68), which means a 1% larger listing raises price by ~0.7%.
- **Newbuilds discount**: flag stays negative (~-9%) even with location controls, because the scraped “new” stock is typically larger, higher-end, and priced more aggressively per m².
- **Construction premiums shrink**: panel/EPK penalties vanish after introducing districts—those building types are concentrated in the same neighborhoods that already have lower prices.
- **Diagnostics matter**: Omnibus/Jarque-Bera indicate the residuals are slightly skewed/heavy-tailed, but Durbin-Watson near 1.2 suggests limited autocorrelation; the regression is robust for comparative purposes.
