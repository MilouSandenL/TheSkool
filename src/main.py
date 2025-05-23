import choroplethmap
import bar_chart
import taipy.gui.builder as tgb
from taipy.gui import Gui

# --- Initiera figurer och data ---
karta_fig = choroplethmap.run_map()
df_long = bar_chart.df_long
available_years = bar_chart.available_years
selected_year = bar_chart.selected_year
line_chart = bar_chart.create_horizontal_bar_chart(selected_year)
chart_title = f"Antal studerande per utbildningsområde för år {selected_year}"

# --- Callback-funktion ---
def update_chart(state):
    state.line_chart = bar_chart.create_horizontal_bar_chart(state.selected_year)
    state.chart_title = f"Antal studerande per utbildningsområde för år {state.selected_year}"

# --- GUI-layout ---
with tgb.Page() as page:
    
    with tgb.part(class_name="card"):
        tgb.text("# Visualisering av YH-data", mode="md")

    with tgb.part(class_name="card"):
        tgb.text("## Karta: Beviljade utbildningar per län", mode="md")
        tgb.chart(figure="{karta_fig}")

    with tgb.part(class_name="card"):
        tgb.text("## {chart_title}", mode="md")
        tgb.chart(figure="{line_chart}")

    with tgb.part(class_name="card"):
        tgb.text("## Välj år", mode="md")
        tgb.selector(value="{selected_year}", lov=available_years, dropdown=True)
        tgb.button("Uppdatera graf", on_action=update_chart, class_name="plain")

    # with tgb.part(class_name="card"):
    #     tgb.text("## Rådata", mode="md")
    #     tgb.table("{df_long}", rows_per_page=20)

# --- Starta app ---
if __name__ == "__main__":
    Gui(page).run(dark_mode=False)
