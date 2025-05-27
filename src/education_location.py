from pathlib import Path
import pandas as pd
import json
from difflib import get_close_matches
import numpy as np
import plotly.graph_objects as go

# --- LADDA DATA EN GÅNG ---
data_dir = Path(__file__).parent / "data"
datafiler = sorted(data_dir.glob("resultat-ansokningsomgang-*.xlsx"))

def prepare_data():
    dfs = []
    for fil in datafiler:
        try:
            år = int(fil.stem[-4:])
            skip = 5 if år >= 2023 else 0
            df = pd.read_excel(fil, sheet_name="Tabell 3", skiprows=skip)
            df["År"] = år

            if len(df.columns) < 10:
                print(f"⚠️ För få kolumner i {fil.name}, hoppade över.")
                continue

            if "Län" not in df.columns:
                df["Län"] = "Okänt"

            if "Utbildningsnamn" in df.columns and "Beslut" in df.columns:
                dfs.append(df)
            else:
                print(f"⚠️ Saknar nödvändiga kolumner i {fil.name}, hoppade över.")

        except Exception as e:
            print(f"❌ Fel i {fil.name}: {e}")

    if not dfs:
        raise ValueError("Ingen data kunde läsas in.")

    return pd.concat(dfs, ignore_index=True)

# Ladda all data EN gång
_full_data = prepare_data()
available_years = sorted(_full_data["År"].unique().tolist())
selected_year = available_years[-1]

# Ladda geojson och regionkoder EN gång
with open("assets/swedish_regions.geojson", "r", encoding="utf-8") as file:
    GEOJSON_DATA = json.load(file)

PROPERTIES = [f["properties"] for f in GEOJSON_DATA["features"]]
REGION_CODES = {p["name"]: p["ref:se:länskod"] for p in PROPERTIES}

# --- RITA KARTA ---
def run_map(year):
    year = int(year)
    # print(f"📍 Kör run_map för år: {year}")
    data = _full_data.copy()
    df = data[data["År"] == year].copy()
    # print(f"🔎 Antal rader efter filter: {len(df)}")

    decisions = df["Beslut"].value_counts()
    approved, total = decisions.get("Beviljad", 0), decisions.sum()
    approval_rate = np.divide(approved * 100, total) if total > 0 else 0

    df_regions = (
        df[df["Län"] != "Flera kommuner"]
        .groupby("Län")["Beslut"]
        .apply(lambda x: (x == "Beviljad").sum())
        .reset_index(name="Beviljade")
    )

    region_codes_map = []
    valid_names = []
    for region in df_regions["Län"]:
        matches = get_close_matches(region, REGION_CODES.keys(), n=1)
        if matches:
            region_codes_map.append(REGION_CODES[matches[0]])
            valid_names.append(region)

    df_regions = df_regions[df_regions["Län"].isin(valid_names)].copy()

    if df_regions.empty or not region_codes_map:
        return go.Figure().update_layout(
            title_text=f"Ingen data tillgänglig för år {year}",
            mapbox=dict(style="white-bg", zoom=3.3, center=dict(lat=63, lon=9.89)),
            width=700,
            height=550,
            margin=dict(r=0, t=50, l=0, b=0)
        )

    df_regions["log_beviljade"] = np.log(df_regions["Beviljade"] + 1)

    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=GEOJSON_DATA,
            locations=region_codes_map,
            z=df_regions["Beviljade"],
            featureidkey="properties.ref:se:länskod",
            customdata=df_regions["Beviljade"],
            marker_opacity=0.9,
            marker_line_width=0.4,
            text=valid_names,
            hovertemplate="<b>%{text}</b><br>Beviljade utbildningar: %{customdata}<extra></extra>",
            showscale=True,
            colorscale = [
            [0.0, "#E53935"],
            [0.5, "#FFF59D"],
            [1.0, "#2E7D32"]
            ],
            colorbar=dict(x=1, xanchor="left", y=0.5, yanchor="middle")
        )
    )

    fig.update_layout(
        mapbox=dict(style="white-bg", zoom=3.3, center=dict(lat=63, lon=9.89)),
        width=470,
        height=500,
        margin=dict(r=0, t=50, l=0, b=0),
        title=dict(
                text=f"""
    <b>Beviljade YH-utbildningar {year}</b><br>
    <br>Totalt godkändes <b>{approved}</b> av <b>{total}</b><br>ansökningar
    <br>
    <br>Beviljandegrad: <b>{approval_rate:.0f}%</b>
    """,
            x=0.06,
            y=0.75,
            font=dict(size=13),
        ),
    )

    return fig
