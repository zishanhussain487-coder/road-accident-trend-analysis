# Road Accident Trend Analysis Dashboard

A beginner-friendly Streamlit dashboard for the Government of India road-accident dataset.

## Files
- `app.py` — interactive dashboard and analysis
- `requirements.txt` — Python dependencies
- `DATA_CLEANING_DOCUMENTATION.md` — cleaning methodology and limitations
- `PRESENTATION_GUIDE.md` — short hackathon presentation and demo guide

## Run on Windows
1. Install Python 3.10 or newer from https://www.python.org/downloads/ (tick **Add Python to PATH** during installation).
2. Extract this ZIP folder.
3. Open the extracted folder in File Explorer.
4. Click the address bar, type `cmd`, and press Enter.
5. Run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

6. A browser tab opens. Upload your organizer-provided CSV or Excel file in the sidebar.
7. Check the column mappings in the sidebar before trusting the charts.
8. Download the cleaned CSV and cleaning documentation from the bottom of the dashboard.

## Important
This app intentionally does not include fabricated accident totals. Upload the official dataset provided by the organizer. The automatic column detection is a convenience; manually verify every mapped column. Do not claim population-, vehicle-, or road-normalized rates unless denominator data is present, has compatible units, and matches the same geography and year.
