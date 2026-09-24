# U.S. Births in 2025: Provisional CDC Counts

A Streamlit dashboard for exploring provisional CDC birth **counts** (not rates)
by state, month, and infant sex. Built for undergraduate business analytics students.

## Run locally
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Push this folder to a GitHub repository (keep `data/` in the repo).
2. On share.streamlit.io, create an app, pick the repo, and set the main file to `app.py`.

## Structure
- `app.py`: page layout, header, KPI cards, tabs
- `src/config.py`: paths, month order, colors
- `src/data_loader.py`: cached loading and validation checks
- `src/state_codes.py`: state name to abbreviation (for the map)
- `src/filters.py`: sidebar filters, Select All, Reset
- `src/metrics.py`: KPI calculations
- `src/charts.py`: one Plotly figure per chart
- `src/tabs/`: one module per tab
- `data/`: the CDC CSV
