import pandas as pd
from pathlib import Path
import taipy.gui.builder as tgb
from taipy.gui import Gui

from src.dashboards import education_location
from src.dashboards import students_by_field
from src.dashboards import approved_programs
from src.dashboards import anordnare_analys
from src.dashboards.anordnare_analys import update_chart_anordnare
from src.dashboards.trends import create_trend_chart
from src.dashboards.stadsbidrag_dashboard import utbildningar, val_utbildning, utan_moms, med_moms, visa_bidrag
from src.dashboards.course_chart import available_courses, selected_course, bar_chart, update_chart

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"


# --- Läs in data för KPI ---
df = pd.read_excel(DATA_DIR / "resultat-ansokningsomgang-2024.xlsx", sheet_name="Tabell 3", skiprows=5)
df.columns = df.columns.str.strip()

# --- KPI-beräkningar ---
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
# länkar    
myh_program = "https://www.myh.se/yrkeshogskolan/resultat-ansokningsomgangar/resultat-for-program"   
myh_kurser = "https://www.myh.se/yrkeshogskolan/resultat-ansokningsomgangar/resultat-for-kurser"  
myh_bidrag = "https://www.myh.se/yrkeshogskolan/ansok-om-att-bedriva-utbildning/ansokan-kurser/statsbidrag-och-schablonnivaer"
myh_statliga_medel = "https://www.myh.se/statistik/yrkeshogskoleutbildningar/statistik-program/utbetalda-statliga-medel"
scb_yh = "https://www.scb.se/UF0701"
scb_marknad ="https://www.scb.se/hitta-statistik/statistik-efter-amne/utbildning-samt-forskning-inom-hogskolan/befolkningens-utbildning-och-studiedeltagande/intradet-pa-arbetsmarknaden/"



trend_chart = create_trend_chart()    


# --- SHARED YEAR (för karta och stapeldiagram) ---
selected_year_shared = approved_programs.selected_approved_year
available_years_shared = approved_programs.available_years

def update_shared_year(state):
    year = int(state.selected_year_shared)
    state.stacked_fig = approved_programs.create_stacked_bar_chart(year)
    state.karta_fig = education_location.run_map(year)

# --- students_by_field ---
df_long = students_by_field.df_long
available_years = students_by_field.available_years
selected_year = students_by_field.selected_year
line_chart = students_by_field.create_horizontal_bar_chart(selected_year)
chart_title = f"🎓 Antal studerande per utbildningsområde för år {selected_year}"

def update_students_chart(state):
    state.line_chart = students_by_field.create_horizontal_bar_chart(state.selected_year)
    state.chart_title = f"🎓 Antal studerande per utbildningsområde för år {state.selected_year}"

# --- Initial Karta och Diagram ---
karta_fig = education_location.run_map(selected_year_shared)
stacked_fig = approved_programs.create_stacked_bar_chart(selected_year_shared)

# --- anordnare_analys ---
selected_anordnare = anordnare_analys.selected_anordnare
anordnare_lov = anordnare_analys.anordnare_lov
chart_title_anordnare = anordnare_analys.chart_title_anordnare
bar_chart_anordnare = anordnare_analys.bar_chart_anordnare
bar_chart_by_area_anordnare = anordnare_analys.bar_chart_by_area_anordnare
line_chart_by_area_anordnare = anordnare_analys.line_chart_by_area_anordnare

# --- GUI-layout ---
with tgb.Page(name="Startsida") as Home:
    with tgb.layout(columns="1fr 8fr 1fr"):
        with tgb.part():
            pass

        with tgb.part():
            tgb.text("# The Skool - YH Dashboard", mode="md")
            tgb.navbar()

            with tgb.part(class_name="card"):
                tgb.text("## 🎓 Nyckeltal för YH-ansökningsomgång 2024", mode="md")
                tgb.text(
                    "Här visas nyckelindikatorer för beviljade och sökta YH-utbildningar under ansökningsomgången 2024.  \n"
                    "Statistiken ger en snabb överblick över beviljandegrad, antal utbildningar och platser samt studieformer.",
                    mode="md",
                )
                tgb.text("📊 **Beviljandegrad:** {beviljandegrad}%    ✅ **Beviljade utbildningar:** {beviljade_utbildningar}    📝 **Sökta utbildningar:** {sökta_utbildningar}", mode="md")
                tgb.text("🎯 **Beviljade platser:** {beviljade_platser}    📌 **Sökta platser:** {sökta_platser}  🏫 **Bundna utbildningar:** {sökta_bundna}    🌐 **Distansutbildningar:** {sökta_distans}", mode="md")

            # --- STATSBIDRAG ---
            with tgb.part(class_name="card"):
                tgb.text("## 📊 Statsbidrag och schablonnivåer per utbildningsområde", mode="md")
                tgb.text(
                    "Statsbidraget utgår från schabloner där bidraget bestäms per studerandeplats i heltidsutbildning som omfattar 40 veckor och 200 yrkeshögskolepoäng (årsplats). - MYH.se",
                    mode="md",
                )
                tgb.selector(value="{val_utbildning}", lov="{utbildningar}", label="🎓 Välj utbildningområde:", dropdown=True)
                tgb.button("Visa bidrag", on_action=visa_bidrag,)

                with tgb.part(render="{utan_moms != ''}"):
                    tgb.text("💰 Utan momskompensation: {utan_moms}")
                    tgb.text("💰 Med momskompensation: {med_moms}")

                tgb.text("Schablonerna ovan gäller utbildningsomgångar med startdatum fr.o.m. 1 juli 2024.", mode="md")
        
            with tgb.part(style="margin-top: 160px;"):
                tgb.text("## 📈 Trender för populära inriktningar 2015–2024", mode="md")
                tgb.chart(figure="{trend_chart}")

        with tgb.part(): pass

# --- Program, Studenter & Kurser ---
with tgb.Page(name="Utbildningsstatistik") as Utbildningsstatistik:
    with tgb.layout(columns="1fr 8fr 1fr"):
        with tgb.part(): pass

        with tgb.part():
            tgb.text("# The Skool - YH Dashboard", mode="md")
            tgb.navbar()
            
            # --- KARTA & BEVILJADE PROGRAM ---
            with tgb.part(class_name="card"):
                with tgb.layout(columns="3 1"):
                    with tgb.part():
                        
                        tgb.text("## 🗺️ Beviljade utbildningar per län för år {selected_year_shared}", mode="md")
                        tgb.chart(figure="{karta_fig}")
                        tgb.text("---", mode="md")
                        tgb.text("## 📈 Beviljade och avslagna program per utbildningsområde för år {selected_year_shared}", mode="md")
                        tgb.chart(figure="{stacked_fig}")
                        
                    with tgb.part():
                        tgb.text("### Välj år (2020-2024)", mode="md")
                        tgb.selector(value="{selected_year_shared}", lov=available_years_shared, dropdown=True, on_change=update_shared_year)
                        tgb.text("**Här ser vi en geografisk fördelning av de beviljade YH-utbildningarna i Sverige under 2020-2024.  \n"
         "Kartan hjälper oss förstå vilka län som fått störst satsningar och vilka som halkar efter.**  \n\n"
         "**Färgschemat visar prestanda där rött indikerar låga värden och grönt indikerar höga värden.**",
         mode="md")


            # --- STUDENTER PER UTBILDNINGSOMRÅDE ---
            with tgb.part(class_name="card"):
                tgb.text("---", mode="md")
                tgb.text("## {chart_title}", mode="md")
                with tgb.layout(columns="3 1"):
                    with tgb.part():
                        tgb.chart(figure="{line_chart}")
                    with tgb.part():
                        tgb.text("### Välj år (2005-2024)", mode="md")
                        tgb.selector(value="{selected_year}", lov=available_years, dropdown=True, on_change=update_students_chart)
                        tgb.text("**Diagrammet visar antalet studerande inom varje utbildningsområde under åren 2005-2024.\
                                 Denna information ger insikt i utbildningsintresse och efterfrågan inom olika sektorer.\
                                 Genom att analysera dessa siffror kan vi identifiera vilka områden som växer och vilka som kanske behöver mer resurser eller marknadsföring.\
                                 Det hjälper även utbildningsanordnare att planera kapacitet och utveckla relevanta utbildningar för framtidens arbetsmarknad.**",mode="md")

            # --- KURSER ---
            with tgb.part(class_name="card"):
                tgb.text("---", mode="md")
                tgb.text("## 📈 Beviljade och avslagna kurser per utbildningsområde (2020-2025)", mode="md")
                with tgb.layout(columns="3 1"):
                    with tgb.part():
                        tgb.chart(figure="{bar_chart}")
                    with tgb.part():
                        tgb.text("### 🔎 Välj kurs", mode="md")
                        tgb.selector(value="{selected_course}", lov=available_courses, dropdown=True, on_change=update_chart)
                        tgb.text("**Diagrammet visar utvecklingen över tid och ger en tydlig bild av efterfrågan och tilldelning för varje utbildning.\
                        Det hjälper till att identifiera trender inom olika utbildningsområden samt hur resurser fördelas över åren.\
                        Endast de 50 mest populära kurserna baserat på totalt antal platser visas i listan för att ge en överskådlig och relevant vy.\
                        Genom att analysera dessa data kan utbildningsanordnare och beslutsfattare fatta mer informerade beslut kring kapacitet och framtida satsningar.**", mode="md") 

        with tgb.part(): pass

# --- ANORDNARANALYS ---
with tgb.Page(name="Utbildningsanordnare") as Anordnaranalys:
    with tgb.layout(columns="1fr 8fr 1fr"):
        with tgb.part(): pass

        with tgb.part():
            tgb.text("# The Skool - YH Dashboard", mode="md")
            tgb.navbar()
            with tgb.part(class_name="card"):
                
                with tgb.layout(columns="3 1"):
                    with tgb.part():
                        tgb.text("## 📊 Beviljade och ej beviljade utbildningar per år", mode="md")
                        tgb.chart(figure="{bar_chart_anordnare}")
                        tgb.text("---", mode="md")

                        tgb.text("## 📚 Beviljade utbildningar per utbildningsområde", mode="md")
                        tgb.chart(figure="{bar_chart_by_area_anordnare}")
                        tgb.text("---", mode="md")

                        tgb.text("## 📈 Ansökta utbildningar per område över tid", mode="md")
                        tgb.chart(figure="{line_chart_by_area_anordnare}")

                    with tgb.part():
                        tgb.text("### 🔎 Välj utbildningsanordnare", mode="md")
                        tgb.selector(
                            value="{selected_anordnare}",
                            lov="{anordnare_lov}",
                            dropdown=True,
                            on_change=anordnare_analys.update_chart_anordnare
                        )
                        tgb.text("**Denna visualisering visar hur antalet beviljade och ej beviljade utbildningar har utvecklats över tid för varje utbildningsanordnare.\
                                 Genom att följa trenderna kan vi se vilka anordnare som får mest stöd och vilka som har större utmaningar att få sina utbildningar godkända.\
                                Informationen ger värdefulla insikter för att förstå styrkor och svagheter i utbildningsutbudet och stödja framtida beslut.**",mode="md")

        with tgb.part(): pass
        
with tgb.Page() as länkar:
    with tgb.layout(columns="1fr 8fr 1fr"):
        with tgb.part(): pass
        
        with tgb.part():
                tgb.text("# The Skool - YH Dashboard", mode="md")
                tgb.navbar()
                
                with tgb.part(class_name="card"):
                    
                    with tgb.layout(columns="3 1"):
                       
                        with tgb.part():
                            tgb.text("## 📚 Länkar och resurser", mode="md")
                            tgb.text("Här är några användbara länkar för att utforska mer om YH-utbildningar och statistik:", mode="md")
                            
                            tgb.text(f"- [Resultat ansökningsomgång program]({myh_program})", mode="md")
                            tgb.text(f"- [Resultat ansökningsomgång kurser]({myh_kurser})", mode="md")
                            tgb.text(f"- [Statsbidrag och schablonsnivåer]({myh_bidrag})", mode="md")
                            tgb.text(f"- [Utbetalda statliga medel]({myh_statliga_medel})", mode="md")
                            tgb.text(f"- [Yrkeshögskolan - SCB]({scb_yh})", mode="md")
                            tgb.text(f"- [Inträdet på arbetsmarknaden - SCB]({scb_marknad})", mode="md")
                            
                        
        with tgb.part(): pass
    # --- Initiera initial state ---
selected_course = available_courses[0]

    # --- Pages ---            
pages = {
        "Startsida": Home,
        "Utbildningsstatistik": Utbildningsstatistik,
        "Utbildningsanordnare": Anordnaranalys,
        "Resurser": länkar
    }

# --- Start GUI ---
if __name__ == "__main__":
    Gui(pages=pages).run(
        dark_mode=False,
        use_reloader=True,
        val_utbildning=val_utbildning,
        utan_moms=utan_moms,
        med_moms=med_moms,
        available_courses=available_courses,
        selected_course=selected_course,
        selected_anordnare=selected_anordnare,
        anordnare_lov=anordnare_lov,
        chart_title_anordnare=chart_title_anordnare,
        bar_chart_anordnare=bar_chart_anordnare,
        bar_chart_by_area_anordnare=bar_chart_by_area_anordnare,
        line_chart_by_area_anordnare=line_chart_by_area_anordnare,
        update_chart_anordnare=update_chart_anordnare,
        bar_chart=None,
        on_action=visa_bidrag,
        port=8080
    )
