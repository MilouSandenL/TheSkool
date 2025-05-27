import pandas as pd
import taipy.gui.builder as tgb
from taipy.gui import Gui

import education_location
import students_by_field
import approved_programs
from trends import create_trend_chart
from stadsbidrag_dashboard import utbildningar, val_utbildning, utan_moms, med_moms, visa_bidrag




# === Läs in data för KPI ===
df = pd.read_excel("data/resultat-ansokningsomgang-2024.xlsx", sheet_name="Tabell 3", skiprows=5)
df.columns = df.columns.str.strip()

# === KPI-beräkningar ===
def calc_kpis():
    total_ansökningar = df.shape[0]
    beviljade = df[df["Beslut"] == "Beviljad"]
    sökta_utbildningar = total_ansökningar
    beviljade_utbildningar = beviljade.shape[0]
    beviljandegrad = round((beviljade_utbildningar / total_ansökningar) * 100, 1) if total_ansökningar > 0 else 0
    beviljade_platser = int(beviljade["Beviljade platser totalt"].sum())
    sökta_platser = int(df["Sökta platser totalt"].sum())
    sökta_bundna = int(df[df["Studieform"] == "Bunden"].shape[0])
    sökta_distans = int(df[df["Studieform"] == "Distans"].shape[0])
    return beviljandegrad, beviljade_utbildningar, sökta_utbildningar, beviljade_platser, sökta_platser, sökta_bundna, sökta_distans

beviljandegrad, beviljade_utbildningar, sökta_utbildningar, beviljade_platser, sökta_platser, sökta_bundna, sökta_distans = calc_kpis()

def uppdatera_kpi(state):
    (
        state.beviljandegrad,
        state.beviljade_utbildningar,
        state.sökta_utbildningar,
        state.beviljade_platser,
        state.sökta_platser,
        state.sökta_bundna,
        state.sökta_distans,
    ) = calc_kpis()
    
#Trends
trend_chart = create_trend_chart()    


# --- SHARED YEAR (för karta och stapeldiagram) ---
selected_year_shared = approved_programs.selected_approved_year
available_years_shared = approved_programs.available_years

def update_shared_year(state):
    year = int(state.selected_year_shared)
    state.stacked_fig = approved_programs.create_stacked_bar_chart(year)
    state.karta_fig = education_location.run_map(year)

# --- STACKED BAR (students_by_field) ---
df_long = students_by_field.df_long
available_years = students_by_field.available_years
selected_year = students_by_field.selected_year
line_chart = students_by_field.create_horizontal_bar_chart(selected_year)
chart_title = f"🎓 Antal studerande per utbildningsområde för år {selected_year}"

def update_chart(state):
    state.line_chart = students_by_field.create_horizontal_bar_chart(state.selected_year)
    state.chart_title = f"🎓 Antal studerande per utbildningsområde för år {state.selected_year}"

# --- Första kartan och diagrammet vid start ---
karta_fig = education_location.run_map(selected_year_shared)
stacked_fig = approved_programs.create_stacked_bar_chart(selected_year_shared)

# === GUI-layout ===
with tgb.Page() as Home:
    tgb.navbar()
    with tgb.layout(columns="1fr 8fr 1fr"):
        with tgb.part():  # Vänster marginal
            pass

        with tgb.part():  # Huvudinnehåll
            tgb.text("# The Skool - YH Dashboard", mode="md")

            # --- MAP och BEVILJADE PROGRAM ---
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

            # --- STUDENTER PER UTBILDNINGSOMRÅDE ---
            with tgb.part(class_name="card"):
                tgb.text("## {chart_title}", mode="md")
                with tgb.layout(columns="3 1"):
                    with tgb.part():
                        tgb.chart(figure="{line_chart}")
                    with tgb.part():
                        tgb.text("### Välj år (2005-2024)", mode="md")
                        tgb.selector(value="{selected_year}", lov=available_years, dropdown=True, on_change=update_chart)

        with tgb.part():  # Höger marginal
            pass


# === SEPARAT SIDFÖR KPIER & TRENDER ===
with tgb.Page() as Kpier_Trender:
    tgb.navbar()
    with tgb.part(class_name="card"):
        tgb.text("## 🎓 YH-ansökningsomgång 2024", mode="md")
        tgb.text(
            "Här visas nyckelindikatorer för beviljade och sökta YH-utbildningar under ansökningsomgången 2024.  \n"
            "Statistiken ger en snabb överblick över beviljandegrad, antal utbildningar och platser samt studieformer.",
            mode="md",
        )
        tgb.text("---", mode="md")
        tgb.text("📊 **Beviljandegrad:** {beviljandegrad}%  ✅ **Beviljade utbildningar:** {beviljade_utbildningar}  📝 **Sökta utbildningar:** {sökta_utbildningar}", mode="md")
        tgb.text("🎯 **Beviljade platser:** {beviljade_platser}  📌 **Sökta platser:** {sökta_platser}  🏫 **Bundna utbildningar:** {sökta_bundna}  🌐 **Distansutbildningar:** {sökta_distans}", mode="md")
        tgb.chart(figure="{trend_chart}")

with tgb.Page() as Bidrag:
    tgb.navbar()
    with tgb.part(class_name="card"):
        tgb.text("# 📊 Statsbidrag och schablonnivåer per utbildning", mode="md")
        tgb.text(
            "Statsbidraget utgår från schabloner där bidraget bestäms per studerandeplats i heltidsutbildning som omfattar 40 veckor och 200 yrkeshögskolepoäng (årsplats). - MYH.se",
            mode="md",
        )
        tgb.text("---", mode="md")
        tgb.selector(value="{val_utbildning}", lov="{utbildningar}", label="🎓 Välj utbildning:", dropdown=True)
        tgb.button("Visa bidrag", on_action=visa_bidrag)
        with tgb.part(render="{utan_moms != ''}"):
            tgb.text("💰 Utan momskompensation: {utan_moms}")
            tgb.text("💰 Med momskompensation: {med_moms}")
        tgb.text("Schablonerna ovan gäller utbildningsomgångar med startdatum fr.o.m. 1 juli 2024.", mode="md")            

#pages             
pages = {
    "Startsida": Home,
    "KPIer_Trender": Kpier_Trender,
    "Statsbidrag": Bidrag
}

# === Start GUI ===
if __name__ == "__main__":
   Gui(pages=pages).run(dark_mode=False, use_reloader=True,
     val_utbildning=val_utbildning,
     utan_moms=utan_moms,
     med_moms=med_moms,
     on_action=visa_bidrag
)

