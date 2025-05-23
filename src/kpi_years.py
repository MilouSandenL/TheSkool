import pandas as pd
from taipy.gui import Gui
import taipy.gui.builder as tgb

years = [2020, 2021, 2022, 2023, 2024]
dfs = {}
for year in years:
    if year in [2020, 2021, 2022]:
        df = pd.read_excel(f"data/resultat-ansokningsomgang-{year}.xlsx", sheet_name="Tabell 3")
    else:
        df = pd.read_excel(f"data/resultat-ansokningsomgang-{year}.xlsx", sheet_name="Tabell 3", skiprows=5)
    df.columns = df.columns.str.strip()
    dfs[year] = df

val_år = years[-1]

def calc_kpis(year):
    df = dfs[year]
    antal_sökta_omg = int(df["Sökta utbildningsomgångar"].sum())
    antal_beviljade_omg = int(df["Beviljade utbildningsomgångar"].sum())
    antal_utbildningar = df["Utbildningsnamn"].nunique()
    antal_lan = df["Län"].nunique()
    return antal_sökta_omg, antal_beviljade_omg, antal_utbildningar, antal_lan

antal_sökta_omg, antal_beviljade_omg, antal_utbildningar, antal_lan = calc_kpis(val_år)

def uppdatera_kpi(state):
    # Detta triggar omrendering även om val_år inte ändrats
    state.val_år = state.val_år
    (
        state.antal_sökta_omg,
        state.antal_beviljade_omg,
        state.antal_utbildningar,
        state.antal_lan,
    ) = calc_kpis(state.val_år)

with tgb.Page(on_init=uppdatera_kpi) as page:
    tgb.text("## KPI:er för ansökningsomgång {val_år}", mode="md")
    tgb.selector("Välj år", value="{val_år}", lov=years, dropdown=True)
    tgb.button("Visa KPI för valt år", on_action=uppdatera_kpi, class_name="plain", update=True)
    tgb.text("📝 **Antal sökta utbildningsomgångar:** {antal_sökta_omg}", mode="md")
    tgb.text("✅ **Antal beviljade utbildningsomgångar:** {antal_beviljade_omg}", mode="md")
    tgb.text("🎓 **Antal utbildningar:** {antal_utbildningar}", mode="md")
    tgb.text("🗺️ **Antal län:** {antal_lan}", mode="md")

if __name__ == "__main__":
    Gui(page).run(use_reloader=True, dark_mode=False)