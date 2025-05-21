from pathlib import Path
import pandas as pd
import plotly.express as px

data_dir = Path(__file__).parent / "data"
datafiler = sorted(data_dir.glob("resultat-ansokningsomgang-*.xlsx"))

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

        if "Utbildningsområde" not in df.columns:
            df["Utbildningsområde"] = "Okänt"

        if "Utbildningsnamn" in df.columns and "Beslut" in df.columns:
            dfs.append(df)
        else:
            print(f"⚠️ Saknar nödvändiga kolumner i {fil.name}, hoppade över.")

    except Exception as e:
        print(f"❌ Fel i {fil.name}: {e}")

if not dfs:
    raise ValueError("Ingen data kunde läsas in.")

data = pd.concat(dfs, ignore_index=True)

total = (
    data.groupby(["År", "Utbildningsområde"])["Utbildningsnamn"]
    .count()
    .reset_index(name="Totalt")
)
beviljad = (
    data[data["Beslut"] == "Beviljad"]
    .groupby(["År", "Utbildningsområde"])["Utbildningsnamn"]
    .count()
    .reset_index(name="Beviljad")
)

merged = total.merge(beviljad, on=["År", "Utbildningsområde"], how="left")
merged["Ej beviljad"] = merged["Totalt"] - merged["Beviljad"].fillna(0)
merged = merged.fillna(0)

merged = merged.melt(
    id_vars=["År", "Utbildningsområde"],
    value_vars=["Beviljad", "Ej beviljad"],
    var_name="Kategori",
    value_name="Antal",
)

merged["Antal"] = merged["Antal"].astype(int)

available_years = sorted(merged["År"].unique().tolist())
selected_year = available_years[-1]
selected_approved_year = available_years[-1]


def create_stacked_bar_chart(year):
    df_filtered = merged[merged["År"] == year].copy()

    totalt_counts = df_filtered.groupby("Utbildningsområde")["Antal"].sum()

    sorted_områden = totalt_counts.sort_values(ascending=True).index.tolist()

    df_filtered["Utbildningsområde"] = pd.Categorical(
        df_filtered["Utbildningsområde"], categories=sorted_områden, ordered=True
    )

    df_filtered = df_filtered.sort_values("Utbildningsområde", ascending=True)

    fig = px.bar(
        df_filtered,
        y="Utbildningsområde",
        x="Antal",
        color="Kategori",
        barmode="stack",
        orientation="h",
        title=f"Antal beviljade och ej beviljade utbildningar per område ({year})",
        labels={"Antal": "Antal utbildningar"},
        color_discrete_map={"Beviljad": "#66BB6A", "Ej beviljad": "#EF5350"},
    )

    fig.update_layout(
        title_text=None,
        showlegend=False,
        yaxis_title=None,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#E0E0E0"),
        yaxis=dict(showgrid=False),
    )

    for trace in fig.data:
        kategori = trace.name
        trace.hovertemplate = "<b>%{y}</b><br>" f"{kategori}: %{{x}}st<extra></extra>"

    return fig


fig = create_stacked_bar_chart(selected_approved_year)


def update_chart(state):
    year = int(state.selected_approved_year)
    state.stacked_fig = create_stacked_bar_chart(year)
