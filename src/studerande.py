import pandas as pd
import plotly.express as px
import taipy.gui.builder as tgb
from taipy.gui import Gui
from constants import studerande  # Anpassa efter din filstruktur

# === DATAINLÄSNING OCH OMBEARBETNING ===

# Läser in tabellen från HTML-källan (t.ex. Excel i HTML-format)
df = pd.read_html(studerande)[0]

# Sätter kolumnnamn på första kolumnen till "Mätpunkt"
df.columns.values[0] = "Mätpunkt"

# Omformar tabellen till långformat med kolumnerna: Mätpunkt, År, Värde
df_long = df.melt(id_vars="Mätpunkt", var_name="År", value_name="Värde")

# Rensar värden: tar bort mellanslag, ersätter kommatecken med punkt, ersätter ".." med None
df_long["Värde"] = (
    df_long["Värde"]
    .astype(str)
    .str.replace(r"\s+", "", regex=True)
    .str.replace(",", ".")
    .replace("..", None)
)

# Konverterar "Värde" till numeriskt format, ogiltiga värden blir NaN
df_long["Värde"] = pd.to_numeric(df_long["Värde"], errors="coerce")

# Konverterar år till heltal
df_long["År"] = df_long["År"].astype(int)

# === INITIALISERING AV TILLSTÅND FÖR DASHBOARD ===

# Skapar en lista av unika år som strängar för dropdown-menyn
available_years = [str(y) for y in sorted(df_long["År"].unique())]

# Förvalt valt år är det första i listan
selected_year = available_years[0]

# Titeltext till grafen
chart_title = f"Studerande för år {selected_year}"

# === FUNKTION FÖR ATT SKAPA HORISONTELL STAPELDIAGRAM ===

def create_horizontal_bar_chart(year_str):
    # Omvandlar sträng till int
    year = int(year_str)

    # Filtrerar bort irrelevanta mätpunkter (andelar och examensgrad)
    filtered = df_long[
        (df_long["År"] == year) &
        (~df_long["Mätpunkt"].isin([
            "därav andel män i procent",
            "därav andel kvinnor i procent",
            "Examensgrad",
            "Examensgrad, kvinnor",
            "Examensgrad, män"
        ]))
    ]

    # Skapar horisontellt stapeldiagram med Plotly Express
    fig = px.bar(
        filtered,
        x="Värde",          # Antal visas på x-axeln
        y="Mätpunkt",       # Kategorier (t.ex. studerande, antagna) på y-axeln
        orientation="h",    # Horisontella staplar
        title=f"Studerande för år {year}"  # Diagramtitel
    )

    # Uppdaterar axeltitlar för tydlighet
    fig.update_layout(
        xaxis_title="Antal",        # X-axel: antal personer
        yaxis_title="Kategori"      # Y-axel: typ av mätpunkt
    )

    return fig

# Förvald graf som visas vid uppstart
line_chart = create_horizontal_bar_chart(selected_year)

# === FUNKTION SOM ANROPAS VID INTERAKTION (KNAPPTRYCK) ===

def update_chart(state):
    # Uppdaterar grafen med valt år
    state.line_chart = create_horizontal_bar_chart(state.selected_year)
    state.chart_title = f"Studerande för år {state.selected_year}"

# === SKAPA DASHBOARD MED TAIPY ===

with tgb.Page() as studerande_page:
    with tgb.part(class_name="container card stack-large", style={"margin-bottom": "20px"}):
        # Titel överst
        with tgb.part(class_name="card"):
            tgb.text("# Studerande över tid", mode="md")

        # Layout med två kolumner: graf till vänster, filter till höger
        with tgb.layout(columns="2 1"):
            with tgb.part(class_name="card"):
                # Visar graf med dynamisk titel
                tgb.text("## {chart_title}", mode="md")
                tgb.chart(figure="{line_chart}")

            with tgb.part(class_name="card"):
                # Dropdown för  att välja år
                tgb.text("## Filtrera på år", mode="md")
                tgb.selector(
                    value="{selected_year}",
                    lov=available_years,
                    dropdown=True
                )
                # Uppdatera-knapp
                tgb.button("Uppdatera graf", on_action=update_chart, class_name="plain")

        # Rådata-tabell längst ned
        with tgb.part(class_name="card"):
            tgb.text("## Rådata", mode="md")
            tgb.table("{df_long}", rows_per_page=24)

# === STARTAR TAIPY GUI ===

Gui(studerande_page).run(dark_mode=False, use_reloader=True)
