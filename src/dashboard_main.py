import education_location
import students_by_field
import approved_programs

import taipy.gui.builder as tgb
from taipy.gui import Gui

# --- SHARED YEAR ---
selected_year_shared = approved_programs.selected_approved_year
available_years_shared = approved_programs.available_years

def update_shared_year(state):
    year = int(state.selected_year_shared)
    state.stacked_fig = approved_programs.create_stacked_bar_chart(year)
    state.karta_fig = education_location.run_map(year)

# --- MAP (education_locations) ---
selected_map_year = education_location.selected_year
available_map_years = education_location.available_years
karta_fig = education_location.run_map(selected_map_year)

def update_map(state):
    state.karta_fig = education_location.run_map(state.selected_map_year)


# --- STACKED BAR (approved_programs) ---
stacked_fig = approved_programs.fig
selected_approved_year = approved_programs.selected_year
available_approved_years = approved_programs.available_years

def update_stacked_chart(state):
    approved_programs.update_chart(state)

# --- STACKED BAR (students_by_field) ---
df_long = students_by_field.df_long
available_years = students_by_field.available_years
selected_year = students_by_field.selected_year
line_chart = students_by_field.create_horizontal_bar_chart(selected_year)
chart_title = f"🎓 Antal studerande per utbildningsområde för år {selected_year}"

def update_chart(state):
    state.line_chart = students_by_field.create_horizontal_bar_chart(state.selected_year)
    state.chart_title = f"🎓 Antal studerande per utbildningsområde för år {state.selected_year}"

# --- GUI-layout ---
with tgb.Page() as page:
    with tgb.layout(columns="1fr 8fr 1fr"):
        with tgb.part():  # Vänster marginal
            pass  # Lämna tom för marginal

        with tgb.part():  # Huvudinnehåll
            tgb.text("# The Skool - YH Dashboard", mode="md")

            # --- MAP och APPROVED PROGRAMS ---
            with tgb.part(class_name="card"):
                with tgb.layout(columns="3 1"):
                    with tgb.part():
                        tgb.text("## 🗺️ Beviljade utbildningar per län för år {selected_year_shared}", mode="md")
                        tgb.chart(figure="{karta_fig}")

                        tgb.text("## 📈 Beviljade och avslagna program per utbildningsområde för år {selected_year_shared}", mode="md")
                        tgb.chart(figure="{stacked_fig}")

                    with tgb.part():
                        tgb.text("### Välj år (2020-2024)", mode="md")
                        tgb.selector(value="{selected_year_shared}", lov=available_years_shared, dropdown=True, on_change=update_shared_year)

            # --- STACKED BAR (students_by_field) ---
            with tgb.part(class_name="card"):
                tgb.text("## {chart_title}", mode="md")
                with tgb.layout(columns="3 1"):
                    with tgb.part():
                        tgb.chart(figure="{line_chart}")
                    with tgb.part():
                        tgb.text("### Välj år (2005-2024)", mode="md")
                        tgb.selector(value="{selected_year}", lov=available_years, dropdown=True, on_change=update_chart)

        with tgb.part():  # Höger marginal
            pass  # Lämna tom för marginal

# --- Start GUI ---
if __name__ == "__main__":
    Gui(page=page).run(use_reloader=True, dark_mode=False, port=8080)