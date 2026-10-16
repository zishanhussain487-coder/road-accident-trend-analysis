# Hackathon Presentation Guide (5 slides)

## Slide 1 — Title
**Road Accident Trend Analysis**  
A data-driven dashboard to understand accident frequency, injuries, fatalities, severity, and regional variation.

## Slide 2 — Problem and objective
Road-safety data can be difficult to compare across years and regions. Our objective is to clean the supplied dataset, calculate clearly defined measures, and present evidence-based patterns through an interactive dashboard.

## Slide 3 — Method
1. Load the organizer-provided CSV/Excel dataset.
2. Clean whitespace and missing markers; validate numeric fields.
3. detect and remove exact duplicate rows.
4. Compare accidents, fatalities, and injuries by year and region.
5. Calculate fatalities/injuries per 100 accidents; calculate normalized rates only if valid denominator data is available.

## Slide 4 — Dashboard and findings
Live-demo the uploaded dataset, column mapping, filters, trend chart, regional bar chart, data-quality report, and downloadable cleaned CSV. Add 2–3 exact numerical findings from your real uploaded dataset after running the app. Do not use invented numbers.

## Slide 5 — Conclusion and limitations
The dashboard helps analysts identify where reported accident counts, injuries, and fatalities differ. Counts alone do not establish risk; population, traffic/vehicle, and road-length denominators improve comparisons when available. Missing data, reporting differences, and non-causal descriptive analysis are important limitations.

## 30-second demo script
“First, we upload the official road-accident dataset. The dashboard checks missing values, detects exact duplicate rows, and converts selected measures into numeric format. We can filter by year and region, compare accident counts, injuries and fatalities, and calculate severity indicators such as fatalities per 100 accidents. Where matching population, vehicle or road-length data exists, we can examine normalized rates. Finally, we export the cleaned dataset and cleaning log. The findings describe the available data and do not claim causation.”
