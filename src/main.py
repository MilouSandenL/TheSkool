# from taipy.gui import Gui
# import taipy.gui.builder as tgb

# from choroplethmap import run_map
# from bar_chart import (
#     page as bar_chart_page,
#     line_chart,
#     chart_title,
#     selected_year,
#     available_years,
#     df_long,
#     update_chart,
# )

# # Karta
# map_figure = run_map()

# with tgb.Page() as map_page:
#     with tgb.part(class_name="container card"):
#         tgb.text("# Karta: Beviljade YH-utbildningar", mode="md")
#         tgb.chart(figure=map_figure)

# # Sidor
# pages = {
#     "/": map_page,
#     "Studerande": bar_chart_page,
# }

# # Samla state-variabler i en dict
# data = {
#     "line_chart": line_chart,
#     "chart_title": chart_title,
#     "selected_year": selected_year,
#     "available_years": available_years,
#     "df_long": df_long,
#     "update_chart": update_chart,
# }

# # Kör GUI
# Gui(pages=pages).run(dark_mode=False, use_reloader=True, data=data)


from taipy.gui import Gui
import taipy.gui.builder as tgb

from choroplethmap import run_map
from bar_chart import (
    page as bar_chart_page,
    line_chart,
    chart_title,
    selected_year,
    available_years,
    df_long,
    update_chart,
)

# Skapa sida för kartan
map_figure = run_map()

with tgb.Page() as map_page:
    tgb.navbar()
    with tgb.part():
        tgb.text("# Karta")
        tgb.chart(figure=map_figure)

# Sidor
pages = {
    "/": map_page,
    "Studerande": bar_chart_page,
}

# Samla state-variabler i en dict
data = {
    "line_chart": line_chart,
    "chart_title": chart_title,
    "selected_year": selected_year,
    "available_years": available_years,
    "df_long": df_long,
    "update_chart": update_chart,
}

# Starta Gui med pages och data
Gui(pages=pages).run(dark_mode=False, use_reloader=True, data=data)