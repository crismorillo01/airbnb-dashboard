# =============================================================================
#  Airbnb Madrid — Interactive Dashboard
#  Deliverable 3 · Data Visualization Project
#  Authors: Cristina Morillo Leal · Vo Thuy Trang · Ketevan Romanishvili
#
#  Requirements:
#      pip install -r requirements.txt
#
#  Data:
#      data/listings_Madrid_clean.csv
#
#  Run:
#      python app.py   →   open http://127.0.0.1:8050
# =============================================================================

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import dash
from dash import dcc, html, Input, Output, State, ctx, ALL, dash_table
import dash_bootstrap_components as dbc
from pathlib import Path

# ── 0. LOAD PRE-PROCESSED DATA ───────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
file_path_listings = BASE_DIR / "data" / "listings_Madrid_clean.csv"

df = pd.read_csv(file_path_listings)

df["has_recent_demand"] = df["has_recent_demand"].astype(bool)
df["last_review"] = pd.to_datetime(df["last_review"], errors="coerce")

ALL_DISTRICTS = sorted(df["neighbourhood_group"].unique())

# Price bins for histogram
BIN_EDGES = [0, 30, 60, 90, 120, 150, 180, 210, 250, 300, 400, 500, 790]
BIN_LABELS = [
    f"{BIN_EDGES[i]}–{BIN_EDGES[i+1]}" for i in range(len(BIN_EDGES)-1)]
PRICE_BIN_INDEX = {
    (lo, hi): i for i, (lo, hi) in enumerate(zip(BIN_EDGES[:-1], BIN_EDGES[1:]))
}

# Host type order
HOST_ORDER = ["Professional (6+)", "Small multi (2-5)", "Individual (1)"]

# ── 1. PALETTE ────────────────────────────────────────────────────────────────
RED = "#C0392B"
RED_DARK = "#7B241C"
RED_LIGHT = "#E8A49A"
RED_PALE = "#FDECEA"
GRAY = "#7F8C8D"
DGRAY = "#2C3E50"
LGRAY = "#F4F6F7"
WHITE = "#FFFFFF"
FONT = "Inter, Arial, sans-serif"
LOCKED_OPACITY = 0.3
TABLE_GRID = "#F2F3F5"
SELECTED_ROW_BG = RED_PALE

RED_SEQ = [
    [0.00, "#FDECEA"], [0.25, "#F1948A"],
    [0.50, "#E74C3C"], [0.75, "#C0392B"], [1.00, "#7B241C"],
]
HOST_COLORS = {
    "Individual (1)":    GRAY,
    "Small multi (2-5)": RED_LIGHT,
    "Professional (6+)": RED,
}
ROOM_COLORS = {
    "Entire home/apt": RED,
    "Private room":    RED_LIGHT,
    "Shared room":     GRAY,
    "Hotel room":      "#AAB7B8",
}


def muted_color(color, opacity=LOCKED_OPACITY):
    """Return the same faded treatment used for inactive chart bars."""
    r = int(color[1:3], 16)
    g = int(color[3:5], 16)
    b = int(color[5:7], 16)
    return f"rgba({r},{g},{b},{opacity})"


def _color_to_rgb(color):
    """Parse common Plotly colour strings and composite rgba over white."""
    if isinstance(color, str):
        c = color.strip()
        if c.startswith("#") and len(c) == 7:
            return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
        if c.startswith("rgb"):
            vals = c[c.find("(") + 1:c.find(")")].split(",")
            nums = [float(v.strip()) for v in vals]
            r, g, b = nums[:3]
            if len(nums) == 4:
                a = max(0, min(1, nums[3]))
                r = r * a + 255 * (1 - a)
                g = g * a + 255 * (1 - a)
                b = b * a + 255 * (1 - a)
            return (int(r), int(g), int(b))
    return (255, 255, 255)


def hover_text_color(color):
    r, g, b = _color_to_rgb(color)
    luminance = 0.299 * r + 0.587 * g + 0.114 * b
    return "#FFFFFF" if luminance < 140 else "#111111"


def hoverlabel_for_colors(colors):
    if isinstance(colors, str):
        return dict(
            bgcolor=colors,
            font=dict(family=FONT, size=12, color=hover_text_color(colors)),
        )
    return dict(
        bgcolor=colors,
        font=dict(
            family=FONT,
            size=12,
            color=[hover_text_color(c) for c in colors],
        ),
    )


def colors_from_scale(values, colorscale=RED_SEQ, vmin=None, vmax=None):
    vals = pd.Series(values, dtype="float64")
    if vals.empty:
        return []
    lo = vals.min() if vmin is None else vmin
    hi = vals.max() if vmax is None else vmax
    if pd.isna(lo):
        lo = 0
    if pd.isna(hi) or hi == lo:
        hi = lo + 1
    norm = ((vals.fillna(lo) - lo) / (hi - lo)).clip(0, 1).tolist()
    return px.colors.sample_colorscale(colorscale, norm)


# Map layer options
MAP_OPTIONS = [
    {"label": "Price",              "value": "price"},
    {"label": "Accommodation type", "value": "room_type"},
    {"label": "Host type",          "value": "host_type"},
    {"label": "Listing count",      "value": "n_listings"},
    {"label": "Reviews last 12 months", "value": "reviews_ltm"},
    {"label": "Activity rate",      "value": "pct_active"},
]

# ── 2. THEME HELPER ───────────────────────────────────────────────────────────


def apply_theme(fig, title="", height=380, is_map=False):
    fig.update_layout(
        font=dict(family=FONT, size=12, color=DGRAY),
        paper_bgcolor=WHITE,
        plot_bgcolor=LGRAY,
        title=dict(
            text=title,
            font=dict(family=FONT, size=14, color=DGRAY),
            x=0.5,
        ),
        legend=dict(
            font=dict(family=FONT, size=11, color=DGRAY),
            title=dict(font=dict(family=FONT, size=11, color=DGRAY)),
        ),
        hoverlabel=dict(
            font=dict(family=FONT, size=12),
        ),
        height=height,
        margin=dict(l=0, r=0, t=40, b=0) if is_map
        else dict(l=12, r=12, t=44, b=12),
    )
    fig.update_xaxes(
        title_font=dict(family=FONT, size=12, color=DGRAY),
        tickfont=dict(family=FONT, size=10, color=DGRAY),
    )
    fig.update_yaxes(
        title_font=dict(family=FONT, size=12, color=DGRAY),
        tickfont=dict(family=FONT, size=10, color=DGRAY),
    )
    return fig


# ── 3. DATA FILTERS ───────────────────────────────────────────────────────────
def apply_filters(districts, active_only, price_range,
                  room_types, host_types, selected_host_id=None):
    dff = df.copy()
    if districts:
        dff = dff[dff["neighbourhood_group"].isin(districts)]
    if active_only:
        dff = dff[dff["has_recent_demand"]]
    if price_range:
        mask = pd.Series(False, index=dff.index)
        for lo, hi in price_range:
            mask |= (dff["price"] >= lo) & (dff["price"] < hi)
        dff = dff[mask]
    if room_types:
        dff = dff[dff["room_type"].isin(room_types)]
    if host_types:
        dff = dff[dff["host_type"].isin(host_types)]
    if selected_host_id is not None:
        dff = dff[dff["host_id"] == selected_host_id]
    return dff


def build_dagg(dff):
    cols = ["neighbourhood_group", "n_listings", "n_listings_pct",
            "n_active", "median_price",
            "mean_reviews_ltm", "total_reviews_ltm",
            "pct_active", "pct_active_pct", "lat", "lon",
            "max_reviews_ltm", "top_listing_id"]
    if dff.empty:
        return pd.DataFrame(columns=cols)
    agg = (
        dff.groupby("neighbourhood_group")
        .agg(
            n_listings=("id",                "count"),
            median_price=("price",             "median"),
            mean_reviews_ltm=("number_of_reviews_ltm", "mean"),
            total_reviews_ltm=("number_of_reviews_ltm", "sum"),
            pct_active=("has_recent_demand",         "mean"),
            lat=("latitude",          "mean"),
            lon=("longitude",         "mean"),
            max_reviews_ltm=("number_of_reviews_ltm", "max"),
        )
        .reset_index()
    )
    agg["pct_active_pct"] = (agg["pct_active"] * 100).round(1)

    total = agg["n_listings"].sum()
    agg["n_listings_pct"] = (
        (agg["n_listings"] / total * 100).round(1) if total else 0.0
    )

    n_active = (dff[dff["has_recent_demand"]]
                .groupby("neighbourhood_group").size())
    agg["n_active"] = (agg["neighbourhood_group"].map(n_active)
                       .fillna(0).astype(int))

    # Used in the annual reviews map hover to identify the local outlier.
    has_rev = dff.dropna(subset=["number_of_reviews_ltm"])
    if not has_rev.empty:
        top_idx = (has_rev
                   .groupby("neighbourhood_group")["number_of_reviews_ltm"]
                   .idxmax())
        top_ids = (has_rev.loc[top_idx, ["neighbourhood_group", "id"]]
                          .set_index("neighbourhood_group")["id"])
        agg["top_listing_id"] = agg["neighbourhood_group"].map(top_ids)
    else:
        agg["top_listing_id"] = pd.NA

    agg["max_reviews_ltm"] = agg["max_reviews_ltm"].fillna(0).astype(int)
    agg["mean_reviews_ltm"] = agg["mean_reviews_ltm"].fillna(0.0)
    agg["total_reviews_ltm"] = agg["total_reviews_ltm"].fillna(0).astype(int)
    agg["top_listing_id"] = agg["top_listing_id"].apply(
        lambda x: f"{int(x)}" if pd.notna(x) else "—"
    )
    return agg


# ── 4. KPI CARD + SPARKLINES ─────────────────────────────────────────────────
def kpi_card(title, value, subtitle, sparkline=None):
    body = [
        html.P(title,    className="kpi-title"),
        html.H3(value,   className="kpi-value"),
        html.P(subtitle, className="kpi-sub"),
    ]
    if sparkline is not None:
        body.append(sparkline)
    return dbc.Card(dbc.CardBody(body), className="kpi-card")


def _spark_progress(percent, color=None):
    """Single horizontal progress bar (0..100)."""
    color = color or RED
    pct = max(0, min(100, percent))
    return html.Div(
        html.Div(style={
            "width": f"{pct:.1f}%",
            "background": color,
        }, className="kpi-spark-fill"),
        className="kpi-spark-bar",
    )


def _spark_stacked(segments):
    """Horizontal stacked bar from a list of (color, percent) tuples."""
    bars = [
        html.Div(style={
            "width": f"{max(0, p):.1f}%",
            "background": c,
        }, className="kpi-spark-seg")
        for c, p in segments if p > 0
    ]
    return html.Div(bars, className="kpi-spark-stack")


def _spark_marker(value, vmax):
    """Gradient scale from light → dark with a vertical marker at value/vmax."""
    pct = 0 if not vmax else max(0, min(100, value / vmax * 100))
    return html.Div([
        html.Div(className="kpi-spark-gradient"),
        html.Div(className="kpi-spark-marker",
                 style={"left": f"{pct:.1f}%"}),
    ], className="kpi-spark-scale")


# ── 5. CHART FUNCTIONS ────────────────────────────────────────────────────────

# ── Donut: fixed visual size, reflects filters, acts as room-type filter ──────
def fig_donut(dff, selected_room_types=None, locked=False):
    """
    Drawn from the filtered dataset so percentages update while the chart size
    remains stable across filter changes.
    """
    room_order = ["Entire home/apt",
                  "Private room", "Shared room", "Hotel room"]
    counts = (dff["room_type"]
              .value_counts()
              .reindex(room_order, fill_value=0)
              .reset_index())
    counts.columns = ["room_type", "count"]

    if selected_room_types:
        pull = [0.07 if rt in selected_room_types else 0.0
                for rt in counts["room_type"]]
        opacities = [1.0 if rt in selected_room_types else 0.3
                     for rt in counts["room_type"]]
    else:
        pull = [0.0] * len(counts)
        opacities = [1.0] * len(counts)
    if locked:
        opacities = [LOCKED_OPACITY] * len(counts)

    colors = [ROOM_COLORS.get(rt, GRAY) for rt in counts["room_type"]]
    rgba_colors = [
        muted_color(color, op) for color, op in zip(colors, opacities)
    ]

    fig = go.Figure(go.Pie(
        labels=counts["room_type"],
        values=counts["count"],
        hole=0.55,
        pull=pull,
        marker=dict(colors=rgba_colors, line=dict(color=WHITE, width=2)),
        textposition="inside",
        textinfo="percent",
        textfont=dict(family=FONT, size=13, color=WHITE),
        insidetextorientation="horizontal",
        domain=dict(x=[0.0, 1.0], y=[0.0, 1.0]),
        hovertemplate="<b>%{label}</b><br>%{value:,} listings (%{percent})<extra></extra>",
        hoverlabel=hoverlabel_for_colors(rgba_colors),
    ))

    apply_theme(
        fig, "Accommodation Types", height=300)
    fig.update_layout(
        margin=dict(l=8, r=8, t=40, b=8),
        showlegend=False,
        autosize=False,
        width=300,
    )
    return fig


# ── Heatmap colour helpers ───────────────────────────────────────────────────
# Same stops as the Heatmap colorscale below. Used to compute the matching
# tooltip background colour for each cell.
_HM_SCALE = [
    (0.00, (244, 246, 247)),
    (0.01, (253, 236, 234)),
    (0.30, (232, 164, 154)),
    (0.65, (192,  57,  43)),
    (1.00, (123,  36,  28)),
]


def _interp_rgb(frac):
    if frac <= 0:
        return _HM_SCALE[0][1]
    if frac >= 1:
        return _HM_SCALE[-1][1]
    for i in range(len(_HM_SCALE) - 1):
        x0, c0 = _HM_SCALE[i]
        x1, c1 = _HM_SCALE[i + 1]
        if x0 <= frac <= x1:
            t = (frac - x0) / (x1 - x0)
            return tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
    return _HM_SCALE[-1][1]


def _contrast_text(rgb):
    r, g, b = rgb
    return "#FFFFFF" if (0.299 * r + 0.587 * g + 0.114 * b) < 140 else "#2C3E50"


# ── Last-review calendar heatmap (Week × Month, rolling year) ────────────────
# Window: 14 Sep 2024 → 14 Sep 2025 (the 12 months ending on the scrape date).
HEATMAP_END = pd.Timestamp("2025-09-14")
HEATMAP_START = pd.Timestamp("2024-09-14")
# 13 (year, month) columns covering Sep-24 → Sep-25
_HM_YM = [
    (2024, 9), (2024, 10), (2024, 11), (2024, 12),
    (2025, 1), (2025, 2), (2025, 3), (2025, 4),
    (2025, 5), (2025, 6), (2025, 7), (2025, 8), (2025, 9),
]
_HM_LABELS = [
    "Sep", "Oct", "Nov", "Dec",
    "Jan", "Feb", "Mar", "Apr",
    "May", "Jun", "Jul", "Aug", "Sep",
]
_HM_X = list(range(len(_HM_YM)))
_HM_WEEK_LABELS = ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"]
_HM_TITLE = "Weekly Review Activity"
_HM_WIDTH = 385
_HM_HEIGHT = 329
_HM_ZMAX = 2200
_HM_MARGIN = dict(l=48, r=34, t=86, b=10)
_HM_COLORBAR = dict(
    thickness=8,
    len=0.76,
    x=1.02,
    outlinewidth=0,
    tickmode="array",
    tickvals=[0, 500, 1000, 1500, 2000],
    ticktext=["0", "500", "1000", "1500", "2000"],
    tickfont=dict(family=FONT, size=9, color=GRAY),
)


def fig_review_heatmap(dff):
    """
    Calendar-style heatmap covering the rolling year that ends on the scrape
    date (14 Sep 2024 → 14 Sep 2025). Month on X, week-of-month on Y. Each
    cell counts listings whose LAST review falls in that week.
    """
    fig = go.Figure()
    base = dff.dropna(subset=["last_review"]).copy()
    base = base[(base["last_review"] >= HEATMAP_START) &
                (base["last_review"] <= HEATMAP_END)]

    base["yr"] = base["last_review"].dt.year
    base["mo"] = base["last_review"].dt.month
    base["week"] = (
        (((base["last_review"].dt.day - 1) // 7) + 1)
        .clip(upper=5)
        .astype(int)
    )

    weekly_counts = base.groupby(["yr", "mo", "week"]).size()
    z = [
        [int(weekly_counts.get((y, m, week), 0)) for (y, m) in _HM_YM]
        for week in range(1, 6)
    ]

    customdata = [
        [f"Week {week}, {_HM_LABELS[i]} {_HM_YM[i][0]}"
         for i in range(len(_HM_YM))]
        for week in range(1, 6)
    ]

    # Per-cell hover tooltip colours that match the cell's heatmap colour
    hov_bg, hov_fg = [], []
    for row in z:
        bg_row, fg_row = [], []
        for v in row:
            rgb = _interp_rgb(v / _HM_ZMAX)
            bg_row.append(f"rgb({rgb[0]},{rgb[1]},{rgb[2]})")
            fg_row.append(_contrast_text(rgb))
        hov_bg.append(bg_row)
        hov_fg.append(fg_row)

    fig.add_trace(go.Heatmap(
        z=z,
        zmin=0,
        zmax=_HM_ZMAX,
        x=_HM_X,
        y=_HM_WEEK_LABELS,
        customdata=customdata,
        colorscale=[
            [0.00, "#F4F6F7"],
            [0.01, "#FDECEA"],
            [0.30, "#E8A49A"],
            [0.65, "#C0392B"],
            [1.00, "#7B241C"],
        ],
        showscale=True,
        colorbar=_HM_COLORBAR,
        xgap=1, ygap=1,
        hovertemplate=(
            "<b>%{customdata}</b><br>"
            "%{z:,} reviews<extra></extra>"
        ),
        hoverlabel=dict(
            bgcolor=hov_bg,
            font=dict(family=FONT, color=hov_fg, size=12),
            bordercolor="rgba(255,255,255,0.65)",
        ),
    ))

    apply_theme(fig, _HM_TITLE, height=_HM_HEIGHT)
    fig.update_layout(
        title=dict(
            text=_HM_TITLE,
            font=dict(family=FONT, size=14, color=DGRAY),
            x=0.5,
            y=0.958,
        ),
        xaxis=dict(side="top", tickfont_size=9, tickangle=0,
                   tickmode="array", tickvals=_HM_X, ticktext=_HM_LABELS,
                   fixedrange=True, showgrid=False),
        yaxis=dict(autorange="reversed", tickfont_size=8,
                   fixedrange=True, showgrid=False),
        margin=_HM_MARGIN,
        autosize=False,
        width=_HM_WIDTH,
        plot_bgcolor=WHITE,
        annotations=[
            dict(
                text="2024",
                x=1.5, y=1.20,
                xref="x", yref="paper",
                showarrow=False,
                font=dict(family=FONT, size=10, color=GRAY),
            ),
            dict(
                text="2025",
                x=8, y=1.20,
                xref="x", yref="paper",
                showarrow=False,
                font=dict(family=FONT, size=10, color=GRAY),
            ),
        ],
        shapes=[
            dict(
                type="line",
                x0=-0.45, x1=3.45, y0=1.11, y1=1.11,
                xref="x", yref="paper",
                line=dict(color=RED_LIGHT, width=1),
            ),
            dict(
                type="line",
                x0=3.55, x1=12.45, y0=1.11, y1=1.11,
                xref="x", yref="paper",
                line=dict(color=RED_LIGHT, width=1),
            ),
        ],
    )
    return fig


# ── Price histogram (categorical bar chart with constant width) ──────────────
def fig_price_histogram(dff_base, selected_range=None, locked=False):
    dff_base = dff_base.copy()
    dff_base["bin"] = pd.cut(
        dff_base["price"], bins=BIN_EDGES, labels=BIN_LABELS, right=False
    )
    counts = dff_base["bin"].value_counts().reindex(BIN_LABELS, fill_value=0)

    selected_labels = set()
    if selected_range:
        for lo, hi in selected_range:
            for label, elo, ehi in zip(BIN_LABELS, BIN_EDGES[:-1], BIN_EDGES[1:]):
                if elo == lo and ehi == hi:
                    selected_labels.add(label)
                    break

    bar_colors = []
    for label in BIN_LABELS:
        if not selected_labels:
            color = RED
        elif label in selected_labels:
            color = RED_DARK
        else:
            color = RED_LIGHT
        bar_colors.append(muted_color(color) if locked else color)

    x_labels = [f"€{l}" for l in BIN_LABELS]

    fig = go.Figure(go.Bar(
        x=x_labels,
        y=counts.values,
        marker_color=bar_colors,
        marker_line_width=0,
        hovertemplate="<b>%{x}</b><br>Listings: %{y:,}<extra></extra>",
        hoverlabel=hoverlabel_for_colors(bar_colors),
        customdata=list(zip(BIN_EDGES[:-1], BIN_EDGES[1:])),
        width=0.85,                              # constant bar width
    ))

    apply_theme(fig, height=320)
    fig.update_layout(
        xaxis=dict(title="Price per night", tickangle=0, tickfont_size=9,
                   type="category", fixedrange=True),
        # Y autoscales with the data; plot area width is held constant by
        # automargin=False + fixed left margin so bar widths stay the same.
        yaxis=dict(title="Number of listings",
                   automargin=False, rangemode="tozero"),
        bargap=0.10,
        margin=dict(l=64, r=24, t=44, b=70),
    )
    return fig


# Constants pinned for every map view.
MAP_CENTER = {"lat": 40.4168, "lon": -3.7038}
MAP_ZOOM = 10.5
MAP_HEIGHT = 600
MAP_STYLE = "carto-positron"


def _slim_colorbar(label):
    return dict(
        title=dict(text=label, font=dict(family=FONT, size=10, color=GRAY)),
        thickness=8,
        len=0.55,
        x=0.99, y=0.5, xanchor="right", yanchor="middle",
        outlinewidth=0,
        tickfont=dict(family=FONT, size=10, color=GRAY),
        bgcolor="rgba(255,255,255,0.0)",
    )


def fig_unified_map(dff, dagg_f, layer):
    """
    Single map view with a stable canvas. Listing-level layers use individual
    points; aggregate layers use district bubbles.
    """
    if layer == "price":
        sample = dff.copy()
        sample["district_median_price"] = (
            sample.groupby("neighbourhood_group")["price"].transform("median")
        )
        fig = px.scatter_map(
            sample, lat="latitude", lon="longitude",
            color="price",
            color_continuous_scale=RED_SEQ, range_color=[0, 300],
            custom_data=["id", "neighbourhood_group", "price",
                         "district_median_price", "price_tier"],
            opacity=0.72,
        )
        fig.update_traces(
            marker_size=5,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "District: %{customdata[1]}<br>"
                "Price: €%{customdata[2]:.0f} / night<br>"
                "Price tier: %{customdata[4]}<br>"
                "Median price district: €%{customdata[3]:.0f} / night"
                "<extra></extra>"
            ),
            hoverlabel=hoverlabel_for_colors(
                colors_from_scale(sample["price"], RED_SEQ, vmin=0, vmax=300)
            ),
        )
        apply_theme(fig, "", height=MAP_HEIGHT, is_map=True)
        fig.update_layout(coloraxis_colorbar=_slim_colorbar("€"))

    elif layer == "room_type":
        sample = dff.copy()
        room_order_map = {rt: i for i, rt in enumerate(
            ["Entire home/apt", "Private room", "Shared room", "Hotel room"])}
        sample["room_order"] = sample["room_type"].map(room_order_map)
        sample = sample.sort_values("room_order")
        fig = px.scatter_map(
            sample, lat="latitude", lon="longitude",
            color="room_type",
            color_discrete_map=ROOM_COLORS,
            category_orders={"room_type": ["Entire home/apt", "Private room",
                                           "Shared room", "Hotel room"]},
            custom_data=["id", "neighbourhood_group", "room_type"],
            opacity=0.65,
        )
        fig.update_traces(
            marker_size=5,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "District: %{customdata[1]}<br>"
                "Accommodation type: %{customdata[2]}"
                "<extra></extra>"
            ),
        )
        for trace in fig.data:
            color = ROOM_COLORS.get(trace.name, GRAY)
            trace.update(hoverlabel=hoverlabel_for_colors(color))
        apply_theme(fig, "", height=MAP_HEIGHT, is_map=True)
        fig.update_layout(legend=dict(
            title=None,
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor="rgba(0,0,0,0.06)", borderwidth=1,
            x=0.01, y=0.99,
            font=dict(family=FONT, size=11, color=DGRAY),
        ))

    elif layer == "host_type":
        sample = dff.copy()
        host_order_map = {
            "Individual (1)": 0, "Small multi (2-5)": 1, "Professional (6+)": 2}
        sample["host_order"] = sample["host_type"].map(host_order_map)
        sample = sample.sort_values("host_order")
        sample["host_type_clean"] = sample["host_type"].str.replace(
            r"\s*\(.*\)$", "", regex=True
        )
        fig = px.scatter_map(
            sample, lat="latitude", lon="longitude",
            color="host_type",
            color_discrete_map=HOST_COLORS,
            category_orders={"host_type": ["Individual (1)",
                                           "Small multi (2-5)",
                                           "Professional (6+)"]},
            custom_data=["id", "neighbourhood_group", "host_id",
                         "host_type_clean",
                         "calculated_host_listings_count"],
            opacity=0.65,
        )
        fig.update_traces(
            marker_size=5,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "District: %{customdata[1]}<br>"
                "Host ID: %{customdata[2]}<br>"
                "Host type: %{customdata[3]}<br>"
                "Host listings: %{customdata[4]}"
                "<extra></extra>"
            ),
        )
        for trace in fig.data:
            color = HOST_COLORS.get(trace.name, GRAY)
            trace.update(hoverlabel=hoverlabel_for_colors(color))
        apply_theme(fig, "", height=MAP_HEIGHT, is_map=True)
        fig.update_layout(legend=dict(
            title=None,
            bgcolor="rgba(255,255,255,0.88)",
            bordercolor="rgba(0,0,0,0.06)", borderwidth=1,
            x=0.01, y=0.99,
            font=dict(family=FONT, size=11, color=DGRAY),
        ))

    else:
        dagg_f = dagg_f.copy()
        if layer == "pct_active":
            dagg_f["value"] = dagg_f["pct_active_pct"]
            clabel = "%"
            custom_cols = ["neighbourhood_group", "n_active", "pct_active_pct"]
            hovertpl = (
                "<b>%{customdata[0]}</b><br>"
                "LTM reviewed listings: %{customdata[1]:,}<br>"
                "Activity rate: %{customdata[2]:.1f}%"
                "<extra></extra>"
            )
        elif layer == "reviews_ltm":
            dagg_f["value"] = dagg_f["mean_reviews_ltm"].round(2)
            clabel = "avg"
            custom_cols = ["neighbourhood_group", "mean_reviews_ltm",
                           "total_reviews_ltm", "max_reviews_ltm",
                           "top_listing_id"]
            hovertpl = (
                "<b>%{customdata[0]}</b><br>"
                "Avg/listing: %{customdata[1]:.1f}<br>"
                "Total reviews LTM: %{customdata[2]:,}<br>"
                "Top listing reviews: %{customdata[3]:,}<br>"
                "Top listing ID: %{customdata[4]}"
                "<extra></extra>"
            )
        else:  # n_listings
            dagg_f["value"] = dagg_f["n_listings"]
            clabel = ""
            custom_cols = ["neighbourhood_group", "n_listings",
                           "n_listings_pct", "median_price"]
            hovertpl = (
                "<b>%{customdata[0]}</b><br>"
                "Total listings: %{customdata[1]:,}<br>"
                "Share of selected listings: %{customdata[2]:.1f}%<br>"
                "Median price: €%{customdata[3]:.0f} / night"
                "<extra></extra>"
            )

        fig = px.scatter_map(
            dagg_f, lat="lat", lon="lon",
            size="n_listings", color="value",
            color_continuous_scale=RED_SEQ, size_max=50,
            custom_data=custom_cols,
            opacity=0.82,
        )
        fig.update_traces(
            hovertemplate=hovertpl,
            hoverlabel=hoverlabel_for_colors(
                colors_from_scale(dagg_f["value"], RED_SEQ)
            ),
        )
        apply_theme(fig, "", height=MAP_HEIGHT, is_map=True)
        fig.update_layout(coloraxis_colorbar=_slim_colorbar(clabel))

    fig.update_layout(
        map=dict(
            style=MAP_STYLE,
            center=MAP_CENTER,
            zoom=MAP_ZOOM,
            # Keep the map focused on Madrid while still allowing some pan/zoom.
            bounds=dict(west=-4.05, east=-3.35, south=40.32, north=40.56),
        ),
        margin=dict(l=0, r=0, t=8, b=0),
        # Preserve user pan/zoom across filter and layer changes.
        uirevision="madrid-map",
    )
    return fig


# ── Host type bar (LEFT, acts as filter) ─────────────────────────────────────
def fig_host_type_bar(dff_base, selected_host_types=None, locked=False):
    """
    Drawn from dff_base (no host_type filter) so all bars are always visible.
    """
    ht = (dff_base["host_type"].value_counts()
          .reindex(HOST_ORDER, fill_value=0)
          .astype(int)
          .reset_index())
    ht.columns = ["host_type", "count"]
    pct = (ht["count"] / ht["count"].sum() * 100).round(1)

    bar_colors = []
    for h in ht["host_type"]:
        base = HOST_COLORS[h]
        if locked:
            bar_colors.append(muted_color(base))
        elif selected_host_types is None or h in selected_host_types:
            bar_colors.append(base)
        else:
            bar_colors.append(muted_color(base))

    fig = go.Figure(go.Bar(
        x=ht["host_type"],
        y=ht["count"],
        marker_color=bar_colors,
        marker_line_width=0,
        text=[f"{v:,}<br>({p}%)" for v, p in zip(ht["count"], pct)],
        textposition="outside",
        textfont=dict(family=FONT, size=11),
        cliponaxis=False,
        hovertemplate="<b>%{x}</b><br>Listings: %{y:,}<extra></extra>",
        hoverlabel=hoverlabel_for_colors(bar_colors),
        customdata=ht["host_type"].tolist(),
        width=0.75,
    ))

    apply_theme(fig, "Host Type", height=370)
    fig.update_layout(
        yaxis=dict(title="Number of listings",
                   automargin=False, rangemode="tozero"),
        xaxis=dict(title="", type="category", fixedrange=True),
        margin=dict(l=64, r=24, t=70, b=40),
    )
    if not ht.empty and ht["count"].max() > 0:
        fig.update_yaxes(range=[0, ht["count"].max() * 1.18])
    return fig


# ── Top-hosts table ──────────────────────────────────────────────────────────
ROOM_TYPES_ORDER = ["Entire home/apt",
                    "Private room", "Shared room", "Hotel room"]
ROOM_SHORT = {
    "Entire home/apt": "Entire",
    "Private room":    "Private",
    "Shared room":     "Shared",
    "Hotel room":      "Hotel",
}


# Column spec used by the interactive DataTable (selectable rows)
TOP_HOSTS_COLUMNS = [
    {"name": "#",            "id": "rank"},
    {"name": "Host ID",      "id": "host_id"},
    {"name": "Listings",     "id": "n_listings"},
    {"name": "% of total",   "id": "n_pct"},
    {"name": "Entire",       "id": "entire"},
    {"name": "Private",      "id": "private"},
    {"name": "Shared",       "id": "shared"},
    {"name": "Hotel",        "id": "hotel"},
    {"name": "Top district", "id": "district"},
]


def top_hosts_style_data_conditional(selected_row_index=None):
    row_bg = SELECTED_ROW_BG if selected_row_index is not None else WHITE
    border_style = {
        "border": "none",
        "borderTop": f"1px solid {TABLE_GRID}",
        "borderBottom": f"1px solid {TABLE_GRID}",
        "borderLeft": "none",
        "borderRight": "none",
    }
    styles = [
        # Dash adds active-cell styling after row selection; pin it to the
        # same border model so only the row background changes.
        {"if": {"state": "active"},
         "backgroundColor": row_bg,
         **border_style},
        {"if": {"state": "selected"},
         "backgroundColor": row_bg,
         **border_style},
        {"if": {"row_index": 0},
         "borderTop": f"1px solid {TABLE_GRID}"},
        {"if": {"row_index": 0, "state": "active"},
         "backgroundColor": row_bg,
         **border_style},
        {"if": {"row_index": 0, "state": "selected"},
         "backgroundColor": row_bg,
         **border_style},
    ]
    if selected_row_index is not None:
        styles.append(
            {"if": {"row_index": selected_row_index},
             "backgroundColor": SELECTED_ROW_BG}
        )
    styles.append(
        {"if": {"filter_query": "{host_id} = \"\""},
         "color": "#D5D8DC", "cursor": "default"}
    )
    return styles


def top_hosts_data(dff, n=10):
    """
    Return rows for the top-hosts DataTable. Always exactly n rows;
    placeholder rows have host_id == "" so the row-selection callback can
    ignore them.

    Sort order (all descending):
        1. n_listings (total properties of the host)
        2. Hotel rooms
        3. Entire home/apt (whole-property listings)
        4. Private rooms
        5. Shared rooms
    """
    rows = []
    if not dff.empty:
        total_listings = len(dff)
        # Counts per host per room_type for the whole selection (needed both
        # for ranking ties and for the table cells).
        full_pivot = (dff.groupby(["host_id", "room_type"]).size()
                      .unstack(fill_value=0))
        for rt in ROOM_TYPES_ORDER:
            if rt not in full_pivot.columns:
                full_pivot[rt] = 0
        full_pivot["n_listings"] = full_pivot.sum(axis=1)

        # Multi-key ranking: total → hotel → entire → private → shared
        ranked = full_pivot.sort_values(
            by=["n_listings", "Hotel room", "Entire home/apt",
                "Private room", "Shared room"],
            ascending=[False, False, False, False, False],
        )
        top_ids = ranked.head(n).index
        pivot = full_pivot.loc[top_ids]

        sub = dff[dff["host_id"].isin(top_ids)]
        top_district = sub.groupby("host_id")["neighbourhood_group"].agg(
            lambda s: s.mode().iat[0] if not s.mode().empty else "—"
        )
        for rank, hid in enumerate(top_ids, 1):
            cnt = int(pivot.loc[hid, "n_listings"])
            pct = cnt / total_listings * 100
            row = {
                "rank":       f"#{rank}",
                "host_id":    int(hid),
                "n_listings": f"{cnt:,}",
                "n_pct":      f"{pct:.1f}%",
            }
            for short, full in zip(["entire", "private", "shared", "hotel"],
                                   ROOM_TYPES_ORDER):
                v = int(pivot.loc[hid, full])
                row[short] = f"{v:,}" if v else "—"
            row["district"] = top_district.get(hid, "—")
            rows.append(row)

    while len(rows) < n:
        rank = len(rows) + 1
        rows.append({
            "rank":     f"#{rank}",
            "host_id":  "",
            "n_listings": "—",
            "n_pct":    "—",
            "entire":   "—",
            "private":  "—",
            "shared":   "—",
            "hotel":    "—",
            "district": "—",
        })
    return rows


# ── 6. APP LAYOUT ─────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap",
    ],
    title="Airbnb Madrid Dashboard",
)

# Expose Flask server for production (Render / gunicorn)
server = app.server

app.layout = html.Div([

    dcc.Store(id="price-range-store",     data=None),
    dcc.Store(id="room-type-store",       data=None),
    dcc.Store(id="host-type-store",       data=None),
    dcc.Store(id="host-selection-store",  data=None),

    # ── HEADER ────────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.H1("Airbnb Market in Madrid", className="header-title"),
            html.P(
                "How is the Airbnb market structured across Madrid in terms of "
                "price, location, host participation, and listing activity?",
                className="header-sub",
            ),
        ]),
        html.Img(
            src="https://upload.wikimedia.org/wikipedia/commons/6/69/"
                "Airbnb_Logo_B%C3%A9lo.svg",
            height="30px", style={"opacity": "0.9"},
        ),
    ], className="dashboard-header"),

    # ── FILTER BAR ────────────────────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Label("Filter by District", className="filter-label"),
            dcc.Dropdown(
                id="district-filter",
                options=[{"label": d, "value": d} for d in ALL_DISTRICTS],
                value=[], multi=True,
                placeholder="All districts — select to filter...",
                style={"fontSize": "13px"},
            ),
        ], id="district-filter-wrap",
            className="filter-control-wrap",
            style={"flex": "1", "marginRight": "24px"}),
        html.Div([
            html.Label("Recent activity only", className="filter-label"),
            dbc.Switch(id="active-toggle", value=False, className="mt-1"),
        ], id="active-toggle-wrap",
            className="filter-control-wrap",
            style={"display": "flex", "flexDirection": "column"}),
    ], className="filter-bar"),

    # ── VIEW 1: MARKET OVERVIEW ───────────────────────────────────────────────
    html.Div([
        html.H2("Overview", className="section-title"),
        html.Div([
            html.Div(id="kpi-row", className="kpi-row"),
            html.Div(
                dcc.Graph(id="review-heatmap",
                          config={"displayModeBar": False,
                                  "responsive": False},
                          style={
                              "width": "385px",
                              "minWidth": "385px",
                              "maxWidth": "385px",
                              "height": "329px",
                              "minHeight": "329px",
                              "maxHeight": "329px",
                          }),
                className="heatmap-wrapper",
            ),
            html.Div([
                dcc.Graph(
                    id="donut-chart",
                    className="filterable-graph",
                    config={"displayModeBar": False},
                ),
                html.Div([
                    html.Button(
                        [
                            html.Span(
                                className="legend-swatch",
                                style={"backgroundColor": ROOM_COLORS[rt]},
                            ),
                            html.Span(rt, className="legend-label"),
                        ],
                        id={"type": "room-legend", "value": rt},
                        n_clicks=0,
                        className="custom-legend-item",
                    )
                    for rt in ["Entire home/apt", "Private room",
                               "Shared room", "Hotel room"]
                ], id="room-legend-wrap", className="custom-legend"),
            ], className="donut-wrapper"),
        ], className="overview-content"),
    ], className="section-overview"),

    # ── VIEW 2: PRICE STRUCTURE ───────────────────────────────────────────────
    html.Div([
        html.H2("Price Structure", className="section-title"),
        dcc.Graph(
            id="price-histogram",
            className="filterable-graph",
            config={"displayModeBar": False},
        ),
    ], className="dashboard-section"),

    # ── VIEW 3: HOST CONCENTRATION ────────────────────────────────────────────
    html.Div([
        html.H2("Host Participation & Market Concentration",
                className="section-title"),
        dbc.Row([
            # LEFT: host type bar (filter)
            dbc.Col(
                dcc.Graph(
                    id="host-type-bar",
                    className="filterable-graph",
                    config={"displayModeBar": False},
                ),
                md=5,
            ),
            dbc.Col([
                html.Div([
                    html.H3("Top 10 hosts in current selection",
                            className="subsection-title"),
                    html.Div([
                        html.Span(id="host-filter-indicator",
                                  className="host-filter-pill"),
                        html.Button(
                            "× Clear",
                            id="clear-host-btn",
                            n_clicks=0,
                            className="clear-host-btn",
                            style={"display": "none"},
                        ),
                    ], className="host-filter-actions"),
                ], className="top-hosts-header"),
                html.Div(
                    dash_table.DataTable(
                        id="top-hosts-datatable",
                        columns=TOP_HOSTS_COLUMNS,
                        data=top_hosts_data(df, n=10),
                        row_selectable="single",
                        selected_rows=[],
                        cell_selectable=True,
                        sort_action="none",
                        page_action="none",
                        style_as_list_view=True,
                        style_table={
                            "borderRadius": "10px",
                            "overflow": "hidden",
                            "border": "1px solid #ECF0F1",
                            "boxShadow": "0 1px 4px rgba(44, 62, 80, 0.08)",
                        },
                        style_header={
                            "backgroundColor": "#C0392B",
                            "color": "#FFFFFF",
                            "fontFamily": "Inter, sans-serif",
                            "fontSize": "10.5px",
                            "fontWeight": "700",
                            "textTransform": "uppercase",
                            "letterSpacing": "0.6px",
                            "padding": "10px 12px",
                            "border": "none",
                            "borderBottom": "1px solid #7B241C",
                            "textAlign": "left",
                        },
                        style_cell={
                            "fontFamily": "Inter, sans-serif",
                            "fontSize": "12.5px",
                            "color": "#2C3E50",
                            "padding": "8px 12px",
                            "border": "none",
                            "borderBottom": "1px solid #F2F3F5",
                            "backgroundColor": "#FFFFFF",
                            "textAlign": "left",
                            "verticalAlign": "middle",
                        },
                        style_data={
                            "border": "none",
                            "borderTop": f"1px solid {TABLE_GRID}",
                            "borderBottom": f"1px solid {TABLE_GRID}",
                            "borderLeft": "none",
                            "borderRight": "none",
                        },
                        style_cell_conditional=[
                            {"if": {"column_id": "rank"},
                             "width": "46px", "color": "#C0392B",
                             "fontWeight": "700"},
                            {"if": {"column_id": "host_id"},
                             "width": "116px",
                             "fontFamily": "SF Mono, Menlo, Consolas, monospace",
                             "fontSize": "11.5px"},
                            {"if": {"column_id": "n_listings"},
                             "width": "86px", "textAlign": "right",
                             "color": "#C0392B", "fontWeight": "700"},
                            {"if": {"column_id": "n_pct"},
                             "width": "96px", "textAlign": "right",
                             "color": "#7F8C8D"},
                            {"if": {"column_id": "entire"},
                             "width": "76px", "textAlign": "right"},
                            {"if": {"column_id": "private"},
                             "width": "76px", "textAlign": "right"},
                            {"if": {"column_id": "shared"},
                             "width": "76px", "textAlign": "right"},
                            {"if": {"column_id": "hotel"},
                             "width": "76px", "textAlign": "right"},
                            {"if": {"column_id": "district"},
                             "width": "190px"},
                        ],
                        style_data_conditional=top_hosts_style_data_conditional(),
                        css=[
                            {"selector": ".dash-spreadsheet tr",
                             "rule": "cursor: pointer;"},
                        ],
                    ),
                    className="top-hosts-table-wrapper",
                ),
            ], md=7),
        ], className="g-3"),
    ], className="dashboard-section"),

    # ── VIEW 4: UNIFIED MAP ───────────────────────────────────────────────────
    html.Div([
        html.H2("Spatial Distribution", className="section-title"),
        html.Div(
            html.Div([
                html.Span(className="map-seg-pill"),
                dbc.RadioItems(
                    id="map-layer",
                    options=MAP_OPTIONS,
                    value="price",
                    className="map-segmented-radio",
                    inputClassName="btn-check",
                    labelClassName="map-seg-btn",
                    labelCheckedClassName="active",
                ),
            ], className="map-segmented", id="map-segmented"),
            className="map-segmented-wrap",
        ),
        dcc.Store(id="_map-seg-pos"),
        dcc.Graph(
            id="unified-map",
            className="unified-map",
            config={
                "displayModeBar": False,
                "displaylogo": False,
                "scrollZoom": True,
            },
        ),
    ], className="dashboard-section"),

    # ── FOOTER ────────────────────────────────────────────────────────────────
    html.Div([
        html.P(
            "Data: Inside Airbnb (insideairbnb.com) · Madrid ~September 2025 · "
            "n = 18,555 listings after cleaning",
            className="footer-text",
        ),
        html.P(
            "Cristina Morillo Leal · Vo Thuy Trang · Ketevan Romanishvili · Jun 2026",
            className="footer-text",
        ),
    ], className="dashboard-footer"),

], className="dashboard-wrapper")


# ── 7. CALLBACKS ──────────────────────────────────────────────────────────────

# ── A: Price histogram click → store (contiguous multi-select) ───────────────
# The selection must always be a contiguous run of price bins:
#   · empty selection         → click any bar to start
#   · click an adjacent bar   → extends the run
#   · click an edge bar       → removes that bar (shrinks the run)
#   · click a non-edge bar    → ignored (would split the range)
#   · click a non-adjacent    → ignored
@app.callback(
    Output("price-range-store", "data"),
    Output("price-histogram",   "clickData"),
    Input("price-histogram",    "clickData"),
    Input("district-filter",    "value"),
    Input("active-toggle",      "value"),
    State("price-range-store",  "data"),
    State("host-selection-store", "data"),
    prevent_initial_call=True,
)
def update_price_store(click_data, _districts, _active_only, current_range,
                       selected_host_id):
    triggered = ctx.triggered_id
    if selected_host_id is not None:
        click_reset = None if triggered == "price-histogram" else dash.no_update
        return dash.no_update, click_reset
    if triggered == "district-filter":
        return dash.no_update, None
    if triggered == "active-toggle":
        return dash.no_update, dash.no_update
    if click_data is None:
        return dash.no_update, dash.no_update

    lo, hi = click_data["points"][0]["customdata"]

    clicked_idx = PRICE_BIN_INDEX.get((lo, hi))
    if clicked_idx is None:
        return dash.no_update, None

    existing = current_range or []
    selected_idxs = sorted(
        i for i in (PRICE_BIN_INDEX.get(tuple(r)) for r in existing)
        if i is not None
    )

    # No selection yet → start a new range
    if not selected_idxs:
        return [[lo, hi]], None

    min_i, max_i = selected_idxs[0], selected_idxs[-1]

    # Clicked an already-selected bin
    if clicked_idx in selected_idxs:
        if clicked_idx == min_i or clicked_idx == max_i:
            # Edge → shrink the run
            new_idxs = [i for i in selected_idxs if i != clicked_idx]
            if not new_idxs:
                return None, None
            new_ranges = [[BIN_EDGES[i], BIN_EDGES[i + 1]] for i in new_idxs]
            return new_ranges, None
        # Non-edge selected bar → ignore (would split the range)
        return dash.no_update, None

    # Clicked an unselected bin → must be adjacent to the run
    if clicked_idx == min_i - 1 or clicked_idx == max_i + 1:
        new_idxs = sorted(selected_idxs + [clicked_idx])
        new_ranges = [[BIN_EDGES[i], BIN_EDGES[i + 1]] for i in new_idxs]
        return new_ranges, None

    # Non-adjacent → ignore
    return dash.no_update, None


# ── B: Donut OR custom legend click → room-type store ───────────────────────
# Multi-select toggle: clicking a slice OR a legend label adds / removes it
# from the selection. We also reset the donut's clickData so consecutive
# clicks on the SAME slice fire the callback again.
@app.callback(
    Output("room-type-store", "data"),
    Output("donut-chart",     "clickData"),
    Input("donut-chart",      "clickData"),
    Input({"type": "room-legend", "value": ALL}, "n_clicks"),
    Input("district-filter",  "value"),
    Input("active-toggle",    "value"),
    State("room-type-store",  "data"),
    State("host-selection-store", "data"),
    prevent_initial_call=True,
)
def update_room_type_store(click_data, _legend_clicks, _districts,
                           _active_only, current_selection, selected_host_id):
    triggered = ctx.triggered_id
    if selected_host_id is not None:
        click_reset = None if triggered == "donut-chart" else dash.no_update
        return dash.no_update, click_reset
    if triggered == "district-filter":
        return dash.no_update, None
    if triggered == "active-toggle":
        return dash.no_update, dash.no_update
    # Legend item clicked
    if isinstance(triggered, dict) and triggered.get("type") == "room-legend":
        label = triggered["value"]
        if current_selection and label in current_selection:
            new_sel = [r for r in current_selection if r != label]
            return (new_sel if new_sel else None), dash.no_update
        existing = current_selection or []
        return existing + [label], dash.no_update
    # Donut slice clicked
    if triggered == "donut-chart":
        if click_data is None:
            return dash.no_update, dash.no_update
        label = click_data["points"][0]["label"]
        if current_selection and label in current_selection:
            new_sel = [r for r in current_selection if r != label]
            return (new_sel if new_sel else None), None
        existing = current_selection or []
        return existing + [label], None
    return dash.no_update, dash.no_update


# ── C: Host type bar click → host-type store (multi-select toggle) ───────────
# NOTE: price-range-store is intentionally NOT an input here. The two filters
# coexist; clicking a price bar must NOT wipe the host-type selection.
@app.callback(
    Output("host-type-store", "data"),
    Output("host-type-bar",   "clickData"),
    Input("host-type-bar",    "clickData"),
    Input("district-filter",  "value"),
    Input("active-toggle",    "value"),
    State("host-type-store",  "data"),
    State("host-selection-store", "data"),
    prevent_initial_call=True,
)
def update_host_type_store(click_data, _districts, _active_only,
                           current_selection, selected_host_id):
    triggered = ctx.triggered_id
    if selected_host_id is not None:
        click_reset = None if triggered == "host-type-bar" else dash.no_update
        return dash.no_update, click_reset
    if triggered == "district-filter":
        return dash.no_update, None
    if triggered == "active-toggle":
        return dash.no_update, dash.no_update
    if click_data is None:
        return dash.no_update, dash.no_update
    label = click_data["points"][0]["customdata"]
    existing = current_selection or []
    if label in existing:
        new_sel = [h for h in existing if h != label]
        return (new_sel if new_sel else None), None
    return existing + [label], None


# ── D: Hide "Activity rate" tab when global Active toggle is ON ──────────────
# When active_only is ON, every listing in the dataset is by definition
# active, so the metric is meaningless — we drop the tab entirely. If the
# user happened to be on that tab, fall back to "Price" so the map keeps
# working.
@app.callback(
    Output("map-layer", "options"),
    Output("map-layer", "value"),
    Input("active-toggle", "value"),
    State("map-layer", "value"),
)
def filter_map_options(active_only, current_value):
    if active_only:
        opts = [o for o in MAP_OPTIONS if o["value"] != "pct_active"]
        new_val = "price" if current_value == "pct_active" else dash.no_update
        return opts, new_val
    return MAP_OPTIONS, dash.no_update


# ── E: All filters → all charts ───────────────────────────────────────────────
@app.callback(
    Output("kpi-row",                  "children"),
    Output("donut-chart",              "figure"),
    Output("review-heatmap",           "figure"),
    Output("price-histogram",          "figure"),
    Output("unified-map",              "figure"),
    Output("host-type-bar",            "figure"),
    Output("top-hosts-datatable",      "data"),
    Output("top-hosts-datatable",      "selected_rows"),
    Output("top-hosts-datatable",      "style_data_conditional"),
    Input("district-filter",     "value"),
    Input("active-toggle",       "value"),
    Input("map-layer",           "value"),
    Input("price-range-store",   "data"),
    Input("room-type-store",     "data"),
    Input("host-type-store",     "data"),
    Input("host-selection-store", "data"),
)
def update_all(districts, active_only, map_layer,
               price_range, room_types, host_types,
               selected_host_id):
    filters_locked = selected_host_id is not None

    # Cross-filter pattern: each chart uses "everything EXCEPT its own
    # dimension". The selected_host_id filter applies to ALL charts
    # except the top-hosts table itself (otherwise selecting a host
    # would collapse the table to a single row).

    # Base for price histogram: everything EXCEPT price_range
    dff_no_price = apply_filters(districts, active_only,
                                 price_range=None,
                                 room_types=room_types,
                                 host_types=host_types,
                                 selected_host_id=selected_host_id)

    # Base for donut: everything EXCEPT room_types
    dff_no_room = apply_filters(districts, active_only,
                                price_range,
                                room_types=None,
                                host_types=host_types,
                                selected_host_id=selected_host_id)

    # Base for host-type bar: everything EXCEPT host_types
    dff_no_host = apply_filters(districts, active_only,
                                price_range, room_types,
                                host_types=None,
                                selected_host_id=selected_host_id)

    # Top-hosts table: everything EXCEPT the selected_host_id itself,
    # so the user can still see (and pick) other hosts after selecting one.
    dff_no_host_sel = apply_filters(districts, active_only,
                                    price_range, room_types, host_types,
                                    selected_host_id=None)

    # Fully filtered df for KPIs, charts and map
    dff = apply_filters(districts, active_only,
                        price_range, room_types, host_types,
                        selected_host_id=selected_host_id)

    # Map uses the same fully-filtered df as KPIs
    dagg_f = build_dagg(dff)

    # KPIs
    n = len(dff)
    med = dff["price"].median() if n > 0 else 0
    pct = dff["has_recent_demand"].mean() * 100 if n > 0 else 0
    ent = (dff["room_type"] == "Entire home/apt").mean() * 100 if n > 0 else 0

    # Sparkline data
    total_full = len(df)
    fill_pct = (n / total_full * 100) if total_full else 0
    if n > 0:
        room_share = (dff["room_type"].value_counts(normalize=True) * 100)
    else:
        room_share = pd.Series(dtype=float)
    e = float(room_share.get("Entire home/apt", 0))
    pr = float(room_share.get("Private room",    0))
    sh = float(room_share.get("Shared room",     0))
    ho = float(room_share.get("Hotel room",      0))

    kpis = html.Div([
        kpi_card("Total Listings",  f"{n:,}",       "in current selection",
                 sparkline=_spark_progress(fill_pct)),
        kpi_card("Median Price",    f"€{med:.0f}",  "per night",
                 sparkline=_spark_marker(med, vmax=300)),
        kpi_card("Activity Rate", f"{pct:.1f}%",  "reviewed in last 12 months",
                 sparkline=_spark_progress(pct)),
        kpi_card("Entire Homes",    f"{ent:.1f}%",  "in current selection",
                 sparkline=_spark_stacked([
                     (RED,           e),
                     (RED_LIGHT,     pr),
                     (GRAY,          sh),
                     ("#AAB7B8",     ho),
                 ])),
    ], className="kpi-grid")

    # Top-hosts table data (unaffected by selected_host_id filter so the
    # user can still see and pick other hosts). Sync selected_rows so the
    # currently-selected host stays highlighted across filter changes.
    table_data = top_hosts_data(dff_no_host_sel, n=10)
    if selected_host_id is not None:
        new_selected_rows = [
            i for i, row in enumerate(table_data)
            if row.get("host_id") == selected_host_id
        ][:1]
    else:
        new_selected_rows = []
    selected_row_index = new_selected_rows[0] if new_selected_rows else None

    return (
        kpis,
        fig_donut(dff_no_room, room_types, locked=filters_locked),
        fig_review_heatmap(dff),
        fig_price_histogram(
            dff_no_price,
            selected_range=price_range,
            locked=filters_locked,
        ),
        fig_unified_map(dff, dagg_f, map_layer),
        fig_host_type_bar(
            dff_no_host,
            selected_host_types=host_types,
            locked=filters_locked,
        ),
        table_data,
        new_selected_rows,
        top_hosts_style_data_conditional(selected_row_index),
    )


# ── G0: Click anywhere on a row → set selected_rows ──────────────────────────
# Lets the entire row act as the click target instead of the tiny radio.
# Uses active_cell (any cell clicked) and writes to selected_rows.
@app.callback(
    Output("top-hosts-datatable", "selected_rows", allow_duplicate=True),
    Output("top-hosts-datatable", "active_cell"),
    Output("top-hosts-datatable", "style_data_conditional",
           allow_duplicate=True),
    Input("top-hosts-datatable", "active_cell"),
    State("top-hosts-datatable", "data"),
    State("top-hosts-datatable", "selected_rows"),
    prevent_initial_call=True,
)
def click_row_to_select(active_cell, data, current_selected):
    if not active_cell or not data:
        return dash.no_update, dash.no_update, dash.no_update
    row = active_cell.get("row")
    if row is None or row >= len(data):
        return dash.no_update, None, dash.no_update
    # Ignore placeholder rows (host_id == "") — keep current selection
    if not data[row].get("host_id"):
        new_selected = [] if current_selected else dash.no_update
        style = top_hosts_style_data_conditional() if current_selected else dash.no_update
        return new_selected, None, style
    if current_selected == [row]:
        return [], None, top_hosts_style_data_conditional()
    return [row], None, top_hosts_style_data_conditional(row)


# ── G: DataTable row selection or Clear button → host-selection-store ───────
@app.callback(
    Output("host-selection-store", "data"),
    Output("top-hosts-datatable", "selected_rows", allow_duplicate=True),
    Output("top-hosts-datatable", "active_cell", allow_duplicate=True),
    Output("top-hosts-datatable", "style_data_conditional",
           allow_duplicate=True),
    Input("top-hosts-datatable", "selected_rows"),
    Input("clear-host-btn",      "n_clicks"),
    State("top-hosts-datatable", "data"),
    State("host-selection-store", "data"),
    prevent_initial_call=True,
)
def update_host_selection(selected_rows, _n_clicks, table_data, current_host):
    triggered = ctx.triggered_id
    # Clear button → wipe selection
    if triggered == "clear-host-btn":
        new_host = None if current_host is not None else dash.no_update
        return new_host, [], None, top_hosts_style_data_conditional()
    # Row-selection change
    if not selected_rows:
        new_host = None if current_host is not None else dash.no_update
        return (
            new_host,
            dash.no_update,
            None,
            top_hosts_style_data_conditional(),
        )
    if not table_data:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    row = table_data[selected_rows[0]]
    new_host = row.get("host_id")
    # Ignore placeholder (empty) rows
    if not new_host:
        new_host = None if current_host is not None else dash.no_update
        return new_host, [], None, top_hosts_style_data_conditional()
    if new_host == current_host:
        return dash.no_update, dash.no_update, dash.no_update, dash.no_update
    return (
        new_host,
        dash.no_update,
        dash.no_update,
        top_hosts_style_data_conditional(selected_rows[0]),
    )


# ── H: Sync the host-filter indicator pill + Clear button visibility ─────────
@app.callback(
    Output("host-filter-indicator", "children"),
    Output("host-filter-indicator", "className"),
    Output("clear-host-btn",        "style"),
    Output("district-filter",       "disabled"),
    Output("active-toggle",         "disabled"),
    Output("district-filter-wrap",  "className"),
    Output("active-toggle-wrap",    "className"),
    Output("price-histogram",       "className"),
    Output("donut-chart",           "className"),
    Output("host-type-bar",         "className"),
    Output({"type": "room-legend", "value": ALL}, "disabled"),
    Output("room-legend-wrap",      "className"),
    Input("host-selection-store",   "data"),
)
def render_host_filter_indicator(host_id):
    locked = host_id is not None
    filter_class = (
        "filter-control-wrap is-locked" if locked else "filter-control-wrap"
    )
    graph_class = "filterable-graph is-locked" if locked else "filterable-graph"
    legend_class = "custom-legend is-locked" if locked else "custom-legend"
    legend_disabled = [locked] * len(ROOM_TYPES_ORDER)
    if host_id is not None:
        return (
            f"Filtered by host {host_id}",
            "host-filter-pill active",
            {"display": "inline-block"},
            True,
            True,
            filter_class,
            filter_class,
            graph_class,
            graph_class,
            graph_class,
            legend_disabled,
            legend_class,
        )
    return (
        "",
        "host-filter-pill",
        {"display": "none"},
        False,
        False,
        filter_class,
        filter_class,
        graph_class,
        graph_class,
        graph_class,
        legend_disabled,
        legend_class,
    )


# ── F: Clientside callback — slide the segmented-control pill ────────────────
# Whenever the active map layer (or the option list) changes, recompute the
# pill's horizontal position and width on the client side. Smooth sliding
# is provided by a CSS transition on .map-seg-pill.
app.clientside_callback(
    """
    function(value, options) {
        const place = () => {
            const container = document.getElementById('map-segmented');
            if (!container) return null;
            const pill = container.querySelector('.map-seg-pill');
            const active = container.querySelector('label.map-seg-btn.active');
            if (!pill || !active) return null;
            const cRect = container.getBoundingClientRect();
            const lRect = active.getBoundingClientRect();
            pill.style.transform = `translateX(${lRect.left - cRect.left}px)`;
            pill.style.width = `${lRect.width}px`;
            pill.style.opacity = '1';
            return null;
        };
        // Wait one frame so Dash has applied the .active class
        requestAnimationFrame(place);
        // Retry after fonts/layout settle in case rAF was too early
        setTimeout(place, 80);
        return null;
    }
    """,
    Output("_map-seg-pos", "data"),
    Input("map-layer", "value"),
    Input("map-layer", "options"),
)


# ── 8. RUN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, host="0.0.0.0", port=port)
