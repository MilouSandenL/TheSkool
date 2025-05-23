


# import pandas as pd
# from taipy.gui import Gui
# import taipy.gui.builder as tgb

# # === Läs in data ===
# df = pd.read_excel("data/resultat-ansokningsomgang-2024.xlsx", sheet_name="Tabell 3", skiprows=5)
# df.columns = df.columns.str.strip()

# # === KPI-variabler ===
# def calc_kpis():
#     total_ansökningar = df.shape[0]
#     beviljade = df[df["Beslut"] == "Beviljad"]
#     sökta_utbildningar = total_ansökningar
#     beviljade_utbildningar = beviljade.shape[0]
#     beviljandegrad = round((beviljade_utbildningar / total_ansökningar) * 100, 1) if total_ansökningar > 0 else 0
#     beviljade_platser = int(beviljade["Beviljade platser totalt"].sum())
#     sökta_platser = int(df["Sökta platser totalt"].sum())
#     sökta_bundna = int(df[df["Studieform"] == "Bunden"].shape[0])
#     sökta_distans = int(df[df["Studieform"] == "Distans"].shape[0])
#     return beviljandegrad, beviljade_utbildningar, sökta_utbildningar, beviljade_platser, sökta_platser, sökta_bundna, sökta_distans

# beviljandegrad, beviljade_utbildningar, sökta_utbildningar, beviljade_platser, sökta_platser, sökta_bundna, sökta_distans = calc_kpis()

# def uppdatera_kpi(state):
#     (
#         state.beviljandegrad,
#         state.beviljade_utbildningar,
#         state.sökta_utbildningar,
#         state.beviljade_platser,
#         state.sökta_platser,
#         state.sökta_bundna,
#         state.sökta_distans,
#     ) = calc_kpis()

# # === GUI ===
# with tgb.Page(on_init=uppdatera_kpi) as page:
#     tgb.text("## 📈 KPI:er för ansökningsomgång 2024", mode="md")
#     tgb.text("📊 **Beviljandegrad:** {beviljandegrad}%  ✅ **Beviljade utbildningar:** {beviljade_utbildningar}  📝 **Sökta utbildningar:** {sökta_utbildningar}", mode="md")
#     tgb.text("🎯 **Beviljade platser:** {beviljade_platser}  📌 **Sökta platser:** {sökta_platser}  🏫 **Bundna utbildningar:** {sökta_bundna}  🌐 **Distansutbildningar:** {sökta_distans}", mode="md")

# # === Starta GUI ===
# if __name__ == "__main__":
#     Gui(page).run(use_reloader=True, dark_mode=False)

import pandas as pd
from taipy.gui import Gui
import taipy.gui.builder as tgb

# === Läs in data ===
df = pd.read_excel("data/resultat-ansokningsomgang-2024.xlsx", sheet_name="Tabell 3", skiprows=5)
df.columns = df.columns.str.strip()

# === KPI-variabler ===
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

# === GUI ===
with tgb.Page(on_init=uppdatera_kpi) as page:
    tgb.text("## 🎓 YH-ansökningsomgång 2024", mode="md")
    tgb.text(
        "Här visas nyckelindikatorer för beviljade och sökta YH-utbildningar under ansökningsomgången 2024.  \n"
        "Statistiken ger en snabb överblick över beviljandegrad, antal utbildningar och platser samt studieformer.",
        mode="md",
    )
    tgb.text("---", mode="md")

    tgb.text("📊 **Beviljandegrad:** {beviljandegrad}%  ✅ **Beviljade utbildningar:** {beviljade_utbildningar}  📝 **Sökta utbildningar:** {sökta_utbildningar}", mode="md")
    tgb.text("🎯 **Beviljade platser:** {beviljade_platser}  📌 **Sökta platser:** {sökta_platser}  🏫 **Bundna utbildningar:** {sökta_bundna}  🌐 **Distansutbildningar:** {sökta_distans}", mode="md")

# === Starta GUI ===
if __name__ == "__main__":
    Gui(page).run(use_reloader=True, dark_mode=False)
