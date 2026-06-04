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

## Filters and How to Use Them

The dashboard is designed for cross-filtering, so most controls can be used
together and the charts update in sync with one another.

- District filter: use the searchable multi-select dropdown to limit the
  dashboard to one or more Madrid districts. Remove a district from the
  selection, or clear the field, to go back to the full city view.
- Recent activity only: turn on the switch to keep only listings that were
  active in the last 12 months. This also removes the "Activity rate" map
  layer, since that metric is no longer meaningful when every listing in view
  is active.
- Price histogram: click a price bin to start a range selection. Keep clicking
  adjacent bins to expand the range, or click one of the edge bins to shrink
  it again. Non-adjacent clicks are ignored so the selection always stays
  contiguous.
- Accommodation donut: click a slice or its matching legend item to include or
  exclude a room type. This works as a multi-select filter, so you can compare
  several accommodation types at once.
- Host type bar chart: click one or more bars to filter by host category. The
  selection behaves like the room-type filter, so bars can be toggled on and
  off.
- Top 10 hosts table: click any host row to filter the whole dashboard to that
  host. While a host is selected, the other global filters and chart controls
  are locked to preserve the current context. Use the "× Clear" button to
  return to normal filtering.

You can combine the district, activity, price, room type, and host type
filters freely. The map and KPIs always reflect the current selection, and the
host table stays visible so you can switch to another host at any time.

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
