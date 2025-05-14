import pandas as pd
import plotly.express as px
import taipy.gui.builder as tgb
from taipy.gui import Gui
from constants import studerande  # Anpassa efter din filstruktur

# Läs in och forma datan
df = pd.read_html(studerande)[0]
df.columns.values[0] = "Mätpunkt"
df_long = df.melt(id_vars="Mätpunkt", var_name="År", value_name="Värde")

df_long["Värde"] = (
    df_long["Värde"]
    .astype(str)
    .str.replace(r"\s+", "", regex=True)
    .str.replace(",", ".")
    .replace("..", None)
)

df_long["Värde"] = pd.to_numeric(df_long["Värde"], errors="coerce")
df_long["År"] = df_long["År"].astype(int)

# Lista med år som strängar 
available_years = [str(y) for y in sorted(df_long["År"].unique())]
selected_year = available_years[0]
chart_title = f"Studerande för år {selected_year}"

# Funktion för att skapa stapeldiagram (filtrerar bort könsandelen och examensgrad)
def create_horizontal_bar_chart(year_str):
    year = int(year_str)
    filtered = df_long[
        (df_long["År"] == year) &
        (~df_long["Mätpunkt"].isin(["därav andel män i procent", "därav andel kvinnor i procent", "Examensgrad", "Examensgrad, kvinnor", "Examensgrad, män"]))
    ]
    
    # Skapa bar chart där "Värde" representerar antalet studerande
    fig = px.bar(
        filtered,
        x="Värde",
        y="Mätpunkt",
        orientation="h",
        title=f"Studerande för år {year}"
    )
    
    # Uppdatera axeltitlar för att bättre reflektera vad som visas
    fig.update_layout(
        xaxis_title="Antal",  # Titeln på x-axeln
        yaxis_title="Kategori",  # Titeln på y-axeln
    )

    return fig


line_chart = create_horizontal_bar_chart(selected_year)

# Callback-funktion när användaren klickar på knappen
def update_chart(state):
    state.line_chart = create_horizontal_bar_chart(state.selected_year)
    state.chart_title = f"Studerande för år {state.selected_year}"

# skapa dashboarden
with tgb.Page() as studerande_page:
    with tgb.part(class_name="container card stack-large",style = {"margin-bottom": "20px"}):
        with tgb.part(class_name="card"):
            tgb.text("# Studerande över tid", mode="md")
            

        with tgb.layout(columns="2 1"):
            with tgb.part(class_name="card"):
                tgb.text("## {chart_title}", mode="md")
                tgb.chart(figure="{line_chart}")

            with tgb.part(class_name="card"):
                tgb.text("## Filtrera på år", mode="md")
                tgb.selector(
                    value="{selected_year}",
                    lov=available_years,
                    dropdown=True
                )
                tgb.button("Uppdatera graf", on_action=update_chart, class_name="plain")

        with tgb.part(class_name="card"):
            tgb.text("## Rådata", mode="md")
            tgb.table("{df_long}",rows_per_page = 24)

# startar dashboarden
Gui(studerande_page).run(dark_mode= False,use_reloader=True)




