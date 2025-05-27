
import os
import pandas as pd
import taipy.gui.builder as tgb

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "data", "schablonnivaer.csv")

df_bidrag = pd.read_csv(CSV_PATH)
df_bidrag["Utan momskompensation"] = df_bidrag["Utan momskompensation"].astype(str).str.replace(" ", "").astype(int)
df_bidrag["Med momskompensation"] = df_bidrag["Med momskompensation"].astype(str).str.replace(" ", "").astype(int)

utbildningar = df_bidrag["Utbildningsområde"].tolist()
val_utbildning = utbildningar[0]

utan_moms = ""
med_moms = ""

def visa_bidrag(state):
    rad = df_bidrag[df_bidrag["Utbildningsområde"] == state.val_utbildning]
    if not rad.empty:
        state.utan_moms = f"{rad['Utan momskompensation'].values[0]:,} kr".replace(",", " ")
        state.med_moms = f"{rad['Med momskompensation'].values[0]:,} kr".replace(",", " ")
    else:
        state.utan_moms = "Ej hittad"
        state.med_moms = "Ej hittad"

with tgb.Page() as bidrag_page:
    tgb.text("# 📊 Statsbidrag och schablonnivåer per utbildning", mode="md")
    tgb.text(
        '"Statsbidraget utgår från schabloner där bidraget bestäms per studerandeplats i heltidsutbildning som omfattar 40 veckor och 200 yrkeshögskolepoäng (årsplats)." - MYH.se',
        mode="md"
    )
    tgb.text("## 🎓 Välj utbildning:", mode="md")
    tgb.selector(value="{val_utbildning}", lov=utbildningar, dropdown=True)
    tgb.button("Visa bidrag", on_action=visa_bidrag)

    with tgb.part(render="{utan_moms != ''}"):
        tgb.text("💰 Utan momskompensation: {utan_moms}")
        tgb.text("💰 Med momskompensation: {med_moms}")

    tgb.text("Schablonerna ovan gäller utbildningsomgångar med startdatum fr.o.m. 1 juli 2024.", mode="md")

