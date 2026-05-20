# Airbnb Madrid Interactive Dashboard

Deliverable 3 for the Data Visualization project by Cristina Morillo Leal,
Vo Thuy Trang, and Ketevan Romanishvili.

## Project Objective

This dashboard explores the structure of the Airbnb market in Madrid. It
focuses on listing volume, price patterns, accommodation types, host
concentration, spatial distribution, and listing activity across the city.

The goal is to make the cleaned Airbnb dataset easier to explore through
coordinated filters, interactive charts, and a map-based view of Madrid.

## Dataset

The app uses a cleaned Inside Airbnb dataset for Madrid, stored in:

```text
data/listings_Madrid_clean.csv
```

The dashboard expects the cleaned file to include listing attributes such as
price, district, room type, host type, activity status, reviews per month,
latitude, and longitude.

District aggregates are built dynamically from the filtered listings data, so
the dashboard stays consistent across all filter combinations.

## Main Features

- Global district filter with multi-select search
- Active listings only toggle
- KPI overview with compact sparklines
- Accommodation type donut chart with clickable legend
- Price histogram with contiguous range selection
- Host type bar chart filter
- Top 10 hosts table with full-row host selection
- Host-selection lock state that preserves existing filters while disabling
  other global/chart filters
- Unified spatial map with switchable layers for price, accommodation type,
  host type, listing count, reviews in the last 12 months, and activity rate
- Dynamic hover label colors for readability

## How to Run

From the `airbnb-dashboard` folder:

```bash
pip install -r requirements.txt
python app.py
```

Then open:

```text
http://127.0.0.1:8050
```

### Run with Docker

Make sure Docker Desktop is running, then build the image from the project
folder:

```bash
docker build -t airbnb-dashboard .
```

Start the container:

```bash
docker run --rm -p 8050:8050 airbnb-dashboard
```

Then open:

```text
http://localhost:8050
```

The terminal will stay attached to the running app. Press `Ctrl + C` to stop
the container.

If `Ctrl + C` does not stop it, open another terminal and list the running
containers:

```bash
docker ps
```

Copy the `CONTAINER ID` for the `airbnb-dashboard` container, then stop it:

```bash
docker stop CONTAINER_ID
```

### Optional: use a virtual environment

If you prefer to keep the project's dependencies isolated from your global
Python install (recommended), create and activate a virtual environment
**before** running the install command:

```bash
# from inside airbnb-dashboard/
python -m venv venv
source venv/bin/activate         # macOS / Linux
# .\venv\Scripts\activate          # Windows PowerShell

pip install -r requirements.txt
python app.py
```

When you are done:

```bash
deactivate
```

The `venv/` folder is ignored by `.gitignore`, so it will not be pushed to
the repository.

## Requirements

The app is built with:

- Dash
- Dash Bootstrap Components
- Plotly
- pandas
- gunicorn, for deployment with the included `Procfile`

Install everything with:

```bash
pip install -r requirements.txt
```

## Project Structure

```text
airbnb_dashboard/
├── app.py
├── requirements.txt
├── Procfile
├── README.md
├── assets/
│   ├── style.css
│   └── segmented.js
└── data/
    └── listings_Madrid_clean.csv
```

`app.py` contains the Dash layout, chart builders, filtering helpers, and
callbacks. `assets/style.css` defines the dashboard styling, and
`assets/segmented.js` keeps the map layer segmented-control pill aligned after
window resizes.
