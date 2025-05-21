import pandas as pd
import plotly.express as px
import taipy.gui.builder as tgb
from taipy.gui import Gui


df = pd.read_csv("data/studerande_ren.csv")

df_long = df.melt(id_vars=["År"], var_name="Utbildningsområde", value_name="Antal")

df_long["Antal"] = (
    df_long["Antal"]
    .astype(str)
    .str.replace(r"\s+", "", regex=True)
    .str.replace(",", ".")
    .replace("..", None)
)
df_long["Antal"] = pd.to_numeric(df_long["Antal"], errors="coerce")
df_long["År"] = df_long["År"].astype(int)


available_years = [str(y) for y in sorted(df_long["År"].unique())]
selected_year = available_years[-1]


def create_horizontal_bar_chart(year_str):
    year = int(year_str)
    filtered = df_long[df_long["År"] == year].copy()

    def format_hover(row):
        antal = row["Antal"]
        if antal >= 10_000:
            return f"{row['Utbildningsområde']}, ~{antal/1000:.1f}k studerande"
        else:
            return f"{row['Utbildningsområde']}, {antal:,.0f} studerande".replace(",", " ")

    filtered["hovertext"] = filtered.apply(format_hover, axis=1)

    fig = px.bar(
        filtered,
        x="Antal",
        y="Utbildningsområde",
        orientation="h",
        color_discrete_sequence=["#66BB6A"],
        title=None,
        labels={"Antal": "Antal studerande", "Utbildningsområde": ""}
    )

    fig.update_traces(
        hovertemplate="%{customdata}<extra></extra>",
        customdata=filtered[["hovertext"]]
    )

    fig.update_layout(
        title_text=None,
        showlegend=False,
        yaxis_title=None,
        yaxis={"categoryorder": "total ascending", "showgrid": False},
        xaxis={"showgrid": True, "gridcolor": "#E0E0E0"},
        plot_bgcolor="white",
        paper_bgcolor="white"
    )

    return fig


def update_chart(state):
    state.bar_chart = create_horizontal_bar_chart(state.selected_year)
    state.chart_title = (
        f"Antal studerande per utbildningsområde för år {state.selected_year}"
    )


bar_chart = create_horizontal_bar_chart(selected_year)
chart_title = f"Antal studerande per utbildningsområde för år {selected_year}"

fig = bar_chart
