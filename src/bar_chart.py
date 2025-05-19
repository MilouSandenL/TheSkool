
import pandas as pd
import plotly.express as px
import taipy.gui.builder as tgb
from taipy.gui import Gui

# --- 1. Läs in CSV ---
df = pd.read_csv("data/studerande_ren.csv")

# --- 2. Gör datan lång ---
df_long = df.melt(id_vars=["År"], var_name="Utbildningsområde", value_name="Antal")

# --- 3. Städa kolumner ---
df_long["Antal"] = (
    df_long["Antal"]
    .astype(str)
    .str.replace(r"\s+", "", regex=True)
    .str.replace(",", ".")
    .replace("..", None)
)
df_long["Antal"] = pd.to_numeric(df_long["Antal"], errors="coerce")
df_long["År"] = df_long["År"].astype(int)

# --- 4. Dropdown och startgraf ---
available_years = [str(y) for y in sorted(df_long["År"].unique())]
selected_year = available_years[0]

def create_horizontal_bar_chart(year_str):
    year = int(year_str)
    filtered = df_long[df_long["År"] == year]
    fig = px.bar(
        filtered,
        x="Antal",
        y="Utbildningsområde",
        orientation="h",
        title=f"Antal studerande per utbildningsområde för år {year}",
        labels={"Antal": "Antal studerande", "Utbildningsområde": "Utbildningsområde"}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    return fig

def update_chart(state):
    state.line_chart = create_horizontal_bar_chart(state.selected_year)
    state.chart_title = f"Antal studerande per utbildningsområde för år {state.selected_year}"

line_chart = create_horizontal_bar_chart(selected_year)
chart_title = f"Antal studerande per utbildningsområde för år {selected_year}"

# --- 5. Bar chart-sida ---
with tgb.Page() as page:
    tgb.navbar({"/": "Karta", "Studerande": "Studerande"})
    with tgb.part(class_name="container card stack-large", style={"margin-bottom": "20px"}):
        with tgb.part(class_name="card"):
            tgb.text("# Studerande per utbildningsområde över tid", mode="md")

        with tgb.layout(columns="2 1"):
            with tgb.part(class_name="card"):
                tgb.text("## {chart_title}", mode="md")
                tgb.chart(figure="{line_chart}")

            with tgb.part(class_name="card"):
                tgb.text("## Välj år", mode="md")
                tgb.selector(value="{selected_year}", lov=available_years, dropdown=True)
                tgb.button("Uppdatera graf", on_action=update_chart, class_name="plain")

        with tgb.part(class_name="card"):
            tgb.text("## Rådata", mode="md")
            tgb.table("{df_long}", rows_per_page=24)

# Gör sidan tillgänglig för main.py
if __name__ == "__main__":
    Gui(page).run(dark_mode=False, use_reloader=True)
    
