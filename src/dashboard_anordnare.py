import pandas as pd
import plotly.express as px
import taipy.gui.builder as tgb
from taipy.gui import Gui
from pathlib import Path

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

        if (
            "Utbildningsanordnare administrativ enhet" in df.columns
            and "Utbildningsnamn" in df.columns
            and "Beslut" in df.columns
        ):
            dfs.append(df)
        else:
            print(f"⚠️ Saknar viktiga kolumner i {fil.name}, hoppade över.")

    except Exception as e:
        print(f"❌ Fel i {fil.name}: {e}")

if not dfs:
    raise ValueError("Ingen data kunde läsas in. Kontrollera att filerna finns i ./src/data")

raw_data = pd.concat(dfs, ignore_index=True)

data = (
    raw_data[[
        "Utbildningsanordnare administrativ enhet",
        "Utbildningsnamn",
        "Utbildningsområde",
        "Beslut",
        "År",
    ]]
    .dropna()
    .sort_values("År")
)

anordnare_lov = sorted(data["Utbildningsanordnare administrativ enhet"].unique().tolist())
selected_anordnare = "Stiftelsen Stockholms Tekniska Institut"

available_years = sorted(data["År"].unique().tolist())
selected_data_year = 2024
filtered_data = data[data["År"] == selected_data_year]

def update_data_table(state):
    try:
        year = int(state.selected_data_year)
        filtered = data[data["År"] == year]
        state.filtered_data = filtered
    except Exception as e:
        print("❌ Fel vid filtrering:", e)
        state.filtered_data = pd.DataFrame()

def create_bar_chart(anordnare):
    df = data[data["Utbildningsanordnare administrativ enhet"] == anordnare]
    total = df.groupby("År")["Utbildningsnamn"].count().reset_index(name="Totalt")
    beviljad = (
        df[df["Beslut"] == "Beviljad"]
        .groupby("År")["Utbildningsnamn"]
        .count()
        .reset_index(name="Beviljad")
    )
    ej_beviljad = total.merge(beviljad, on="År", how="left")
    ej_beviljad["Ej beviljad"] = ej_beviljad["Totalt"] - ej_beviljad["Beviljad"].fillna(0)
    ej_beviljad = ej_beviljad[["År", "Ej beviljad"]]

    merged = (
        total.merge(beviljad, on="År", how="left")
        .merge(ej_beviljad, on="År", how="left")
        .fillna(0)
    )
    merged = merged.melt(
        id_vars="År",
        value_vars=["Totalt", "Beviljad", "Ej beviljad"],
        var_name="Kategori",
        value_name="Antal",
    )
    merged["Antal"] = merged["Antal"].astype(int)

    color_map = {
        "Totalt": "#B0BEC5",
        "Beviljad": "#66BB6A",
        "Ej beviljad": "#EF5350"
    }

    fig = px.bar(
        merged,
        x="År",
        y="Antal",
        color="Kategori",
        barmode="group",
        title=f"Ansökningar för {anordnare} per år",
        color_discrete_map=color_map,
    )

    for trace in fig.data:
        kategori = trace.name
        visningsnamn = {
            "Totalt": "Totalt",
            "Beviljad": "Beviljade",
            "Ej beviljad": "Ej beviljade"
        }.get(kategori, kategori)

        trace.hovertemplate = f"{visningsnamn}: %{{y}}st<br>%{{x}}<extra></extra>"

    fig.update_layout(
        xaxis_title="År",
        yaxis_title="Antal utbildningar",
        xaxis=dict(tickmode="linear", dtick=1, showgrid=False),
        yaxis=dict(showgrid=False),
        plot_bgcolor="#F5F5F5",
        paper_bgcolor="#F5F5F5",
    )
    return fig

def create_bar_chart_by_area(anordnare):
    df = data[
        (data["Utbildningsanordnare administrativ enhet"] == anordnare)
        & (data["Beslut"] == "Beviljad")
    ].dropna(subset=["Utbildningsområde", "Utbildningsnamn"])

    grouped = (
        df.groupby(["År", "Utbildningsområde"])
        .size()
        .reset_index(name="Antal")
    )

    grouped["Antal"] = grouped["Antal"].astype(int)

    fig = px.bar(
        grouped,
        x="År",
        y="Antal",
        color="Utbildningsområde",
        barmode="group",
        title=f"Beviljade utbildningar per område ({anordnare})",
    )

    for trace in fig.data:
        område = trace.name
        trace.hovertemplate = (
            f"Område: {område}<br>Antal: %{{y}}st<br>År: %{{x}}<extra></extra>"
        )

    fig.update_layout(
        xaxis=dict(
            title="År",
            tickmode="linear",
            dtick=1,
            showgrid=False
        ),
        yaxis=dict(
            title="Antal beviljade utbildningar",
            tickformat="d",
            showgrid=False
        ),
        plot_bgcolor="#F5F5F5",
        paper_bgcolor="#F5F5F5",
        legend_title_text="Utbildningsområde",
        hovermode="x unified"
    )

    return fig

chart_title = f"Ansökningar för {selected_anordnare}"
bar_chart = create_bar_chart(selected_anordnare)
area_chart = create_bar_chart_by_area(selected_anordnare)

def update_chart(state):
    state.bar_chart = create_bar_chart(state.selected_anordnare)
    state.area_chart = create_bar_chart_by_area(state.selected_anordnare)
    state.chart_title = f"Ansökningar för {state.selected_anordnare}"

with tgb.Page() as anordnare_page:
    with tgb.part(class_name="container card stack-large", style={"margin-bottom": "20px"}):
        with tgb.part(class_name="card"):
            tgb.text("# Utbildningsanordnare: Ansökningar", mode="md")

        with tgb.layout(columns="2 1"):
            with tgb.part(class_name="card"):
                tgb.text("## {chart_title}", mode="md")
                tgb.chart(figure="{bar_chart}")
                tgb.chart(figure="{area_chart}")

            with tgb.part(class_name="card"):
                tgb.text("## Välj utbildningsanordnare", mode="md")
                tgb.selector(
                    value="{selected_anordnare}", lov=anordnare_lov, dropdown=True
                )
                tgb.button("Uppdatera graf", on_action=update_chart, class_name="plain")

        with tgb.part(class_name="card"):
            tgb.text("## Rådata", mode="md")
            tgb.selector(
                value="{selected_data_year}",
                lov=available_years,
                dropdown=True,
                on_change=update_data_table,
            )
            tgb.table("{filtered_data}", rows_per_page=20)

Gui(anordnare_page).run(
    title="Dashboard - Anordnare", dark_mode=False, use_reloader=True, port=8080
)
