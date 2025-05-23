import os
import pandas as pd
from taipy.gui import Gui

BASE_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(BASE_DIR, "data", "schablonnivaer.csv")

df = pd.read_csv(CSV_PATH)
df["Utan momskompensation"] = df["Utan momskompensation"].astype(str).str.replace(" ", "").astype(int)
df["Med momskompensation"] = df["Med momskompensation"].astype(str).str.replace(" ", "").astype(int)

utbildningar = df["Utbildningsområde"].tolist()
val_utbildning = utbildningar[0]

utan_moms = ""
med_moms = ""

def visa_bidrag(state):
    rad = df[df["Utbildningsområde"] == state.val_utbildning]
    if not rad.empty:
        state.utan_moms = f"{rad['Utan momskompensation'].values[0]:,} kr".replace(",", " ")
        state.med_moms = f"{rad['Med momskompensation'].values[0]:,} kr".replace(",", " ")
    else:
        state.utan_moms = "Ej hittad"
        state.med_moms = "Ej hittad"

layout = """
# 📊 Statsbidrag och schablonnivåer per utbildning

"Statsbidraget utgår från schabloner där bidraget bestäms per studerandeplats i heltidsutbildning som omfattar 40 veckor och 200 yrkeshögskolepoäng (årsplats)." - MYH.se

## 🎓 Välj utbildning:

<|{val_utbildning}|selector|label=Utbildningsområde|lov={utbildningar}|dropdown|>

<|Visa bidrag|button|on_action=visa_bidrag|>

## 💵 Statsbidrag per elev:

<|part|render={utan_moms != ""}|
<|text|value=💰 Utan momskompensation: {utan_moms}|>
<|text|value=💰 Med momskompensation: {med_moms}|>
|>

Schablonerna ovan gäller utbildningsomgångar med startdatum fr.o.m. 1 juli 2024.
"""

Gui(page=layout).run(dark_mode=True)
