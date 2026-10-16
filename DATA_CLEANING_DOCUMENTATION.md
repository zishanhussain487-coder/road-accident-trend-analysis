# Data-Cleaning Documentation — Road Accident Trend Analysis

## Objective
Prepare the supplied road-accident dataset for consistent descriptive analysis of accident frequency, fatalities, injuries, severity indicators, and regional/time differences.

## Cleaning operations performed by the dashboard
1. Preserve the original uploaded file; process a working copy.
2. Trim spaces from column headers and text cells.
3. Convert mapped year and count/denominator columns to numeric values. Unparseable values are set to missing, not guessed.
4. Treat blank text and common `NA`, `N/A`, and `None` markers as missing.
5. Detect and remove exact duplicate rows.
6. Report missing values by column.
7. Flag negative values in mapped count/denominator columns for review rather than silently replacing them.
8. Export the cleaned working data as CSV.

## Measures
- **Accident frequency:** sum of reported accidents.
- **Fatalities:** sum of persons killed / fatalities as defined by the source.
- **Injuries:** sum of persons injured as defined by the source.
- **Fatalities per 100 accidents:** fatalities ÷ accidents × 100, where accident total is positive.
- **Injuries per 100 accidents:** injuries ÷ accidents × 100, where accident total is positive.
- **Normalized rates:** only when population, registered vehicles, or road length data is available, correctly mapped, unit-compatible, and aligned by geography and year.

## Quality checks to complete before submission
- Confirm each mapped column against the source data dictionary.
- Check whether totals, subtotals, and category rows are mixed together; remove/handle them only when the source documentation supports doing so.
- Check for duplicated geography-year rows that are not exact duplicates.
- Review missing values and any negative or implausible values.
- Confirm whether fatalities/injuries are people counts or another measure.
- Confirm road-length units and whether population/vehicle data is for the same year and geography.
- Record any manual edits and reasons here before submitting.

## Limitations
- Results are limited to the provided file, time period, categories, and reporting coverage.
- Missing data, reporting differences, and inconsistent definitions can affect comparisons.
- Accident counts alone do not measure risk; high-population or high-traffic regions may have higher counts.
- Normalized comparisons require a reliable denominator for the same region and period.
- Fatalities per 100 accidents is a descriptive severity measure, not proof that a particular road or region causes accidents.
- Regional patterns show association/differences, not causation.
- Automatic column detection can select the wrong field; manual verification is required.
