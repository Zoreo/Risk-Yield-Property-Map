# Risk & Yield Mapping Summary

## Data sources
- `data/processed/district_metrics.csv`: per-district sale/official rent ppm², log-price residual (scaled), gross rental yield, and assigned quadrant.
- `data/official/official_sale_flat_final.csv` / `data/official/official_rent_flat_final.csv`: flattened official sale/rent per m² tables used to derive yield inputs.
- `data/processed/district_residuals.csv`: hedonic residual signal that supplies the vertical axis for the risk map.

## Mapping logic
1. **Yield** is calculated as `(median rent per m² × 12) / (median sale price per m²)` using the official tables. Values naturally fall between 0 and 1 and are expressed as percentages in the visualization.
2. **Valuation residuals** are taken from the district-augmented hedonic regression and averaged per district; they are close to zero, so the notebook multiplies them (and exposes the `resid_display` column) to make the quadrant plot more interpretable.
3. **Quadrants** classify districts as:
   - **Overvalued Low-Yield Districts**: high residual, low yield.
      Example: в.з.Симеоново - Драгалевци,3182 sale_ppm2, 5.18 rent_ppm2, 6.039613253960853e-14 resid
      - Location premium just doesn't make up for the sale cost. The rent can't keep up either, really bad investment idea (0.16 yield)

   - **Low-Price Low-Yield Districts**: low residual, low yield.
      Example: Изгрев, 4632 sale_ppm2, 10.68 rent_ppm2, 3.0198066269804264e-14 resid
      - Huge location premium that makes this sale cost make sense. The rents however, don't match that (0.23 yield)
   
   - **Undervalued High-Yield Districts**: low residual, high yield.
      Example: Зона Б-19, 2025 sale_ppm2, 9.93 rent_ppm2, 3.618158404462616e-14 resid
      - priced a little above what we’d expect (tiny positive residual), but the income yield is still very strong (0.49 yield).

   - **High-Price High-Yield Districts**: high residual, high yield.
      Example: в.з.Малинова долина,2811 sale_ppm2, 18.12 rent_ppm2, 5.2783174656464593e-14 resid
      - notceably positive residual and massive rental power(0.64 yield)

   - **Unknown/others**: bookmarks where either yield or residual data is missing/not enough to make sensible deductions.

## Visual & narrative takeaways

<img width="879" height="420" alt="image (1)" src="https://github.com/user-attachments/assets/d5f08c98-83bf-4d22-945b-25aa7c990b89" />

- Districts such as **Докторски паметник** and **Център** score high on residuals and yields, landing in the `high_price_high_yield` quadrant. Peripheral districts like **Надежда** and **Люлин** sit closer to the `low_price_low_yield` or `undervalued` quadrants depending on their yield.
- The scatter plot generated in `notebooks/04_risk_yield_mapping.ipynb` includes ID labels pulled from `district_metrics.csv`, and the numeric legend helps map each point back to district names if you need to reproduce the figure in a report.
