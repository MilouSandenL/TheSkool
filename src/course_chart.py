import pandas as pd
import plotly.express as px
import taipy.gui.builder as tgb
from taipy.gui import Gui

# === Läs in data ===
ansokningar_files = [
    "data/kursdata/ansokningar-2021.xlsx",
    "data/kursdata/ansokningar-2023.xlsx",
    "data/kursdata/ansokningar-2024.xlsx"
]
beviljade_files = [
    "data/kursdata/Beviljade-kurser-2020-vår.xlsx",
    "data/kursdata/Beviljade-kurser-2021.xlsx",
    "data/kursdata/Beviljade-kurser-2022.xlsx",
    "data/kursdata/Beviljade-kurser-2023.xlsx",
    "data/kursdata/Beviljade-kurser-2024.xlsx"
]

ansokningar_df = pd.concat([pd.read_excel(f) for f in ansokningar_files], ignore_index=True)
beviljade_df = pd.concat([pd.read_excel(f) for f in beviljade_files], ignore_index=True)

# === Förbered ansökningar ===
ansokta_kolumner = {
    "Sökt antal  platser 2021": "2021",
    "Sökt antal platser 2022": "2022",
    "Sökt antal platser 2023": "2023",
    "Sökt antal platser 2024": "2024",
    "Sökt antal platser 2024 (start och avslut 2024)": "2024_extra",
    "Sökt antal platser 2025": "2025"
}

ansokningar_df = ansokningar_df[["Utbildningsnamn"] + list(ansokta_kolumner.keys())].copy()
ansokningar_df.rename(columns=ansokta_kolumner, inplace=True)
ansokningar_df["2024"] = ansokningar_df["2024"].fillna(0) + ansokningar_df["2024_extra"].fillna(0)
ansokningar_df.drop(columns=["2024_extra"], inplace=True)

ansokningar_df = ansokningar_df.groupby("Utbildningsnamn").sum(numeric_only=True).reset_index()
ansokta_long = ansokningar_df.melt(id_vars="Utbildningsnamn", var_name="År", value_name="Platser")
ansokta_long["Typ"] = "Ansökta"

# === Förbered beviljade ===
beviljade_kolumner = {
    "Antal beviljade platser 2020": "2020",
    "Antal beviljade platser 2021": "2021",
    "Antal beviljade platser 2022": "2022",
    "Antal beviljade platser 2023": "2023",
    "Antal beviljade platser 2024": "2024",
    "Antal beviljade platser start 2024": "2024_start",
    "Antal beviljade platser start och slut 2024": "2024_start_slut",
    "Antal beviljade platser start 2025": "2025"
}

valda_kolumner = ["Utbildningsnamn"] + [col for col in beviljade_kolumner if col in beviljade_df.columns]
beviljade_df = beviljade_df[valda_kolumner].copy()
beviljade_df.rename(columns=beviljade_kolumner, inplace=True)

# Summera 2024-varianter
beviljade_df["2024"] = (
    beviljade_df.get("2024", 0).fillna(0) +
    beviljade_df.get("2024_start", 0).fillna(0) +
    beviljade_df.get("2024_start_slut", 0).fillna(0)
)

# Ta med bara årskolumner vi är säkra på
kolumner = ["Utbildningsnamn", "2020", "2021", "2022", "2023", "2024", "2025"]
for col in kolumner[1:]:
    if col not in beviljade_df.columns:
        beviljade_df[col] = 0

beviljade_df = beviljade_df[kolumner]
beviljade_df = beviljade_df.groupby("Utbildningsnamn").sum(numeric_only=True).reset_index()

beviljade_long = beviljade_df.melt(id_vars="Utbildningsnamn", var_name="År", value_name="Platser")
beviljade_long["Typ"] = "Beviljade"

# === Kombinera och fyll i saknade år ===
combined_df = pd.concat([ansokta_long, beviljade_long], ignore_index=True)
combined_df["Platser"] = combined_df["Platser"].fillna(0)

# Se till att alla kurser har alla år och typer
ALL_YEARS = ["2020", "2021", "2022", "2023", "2024", "2025"]
ALL_TYPES = ["Ansökta", "Beviljade"]
ALL_KURSER = combined_df["Utbildningsnamn"].unique()

full_index = pd.MultiIndex.from_product([ALL_KURSER, ALL_YEARS, ALL_TYPES], names=["Utbildningsnamn", "År", "Typ"])
combined_df = combined_df.set_index(["Utbildningsnamn", "År", "Typ"]).reindex(full_index, fill_value=0).reset_index()

# === GUI ===
# Filtrera bort kurser som har 0 totalt över alla år och typer
kurstotaler = combined_df.groupby("Utbildningsnamn")["Platser"].sum()
kurser_med_data = kurstotaler[kurstotaler > 0].index.tolist()

# Filtrera datan också så att vi inte visar "tomma" kurser
combined_df = combined_df[combined_df["Utbildningsnamn"].isin(kurser_med_data)]

available_courses = sorted(kurser_med_data)

selected_course = available_courses[0]

def create_bar_chart(course_name):
    df = combined_df[combined_df["Utbildningsnamn"] == course_name]
    fig = px.bar(
        df,
        x="År",
        y="Platser",
        color="Typ",
        barmode="group",
        title=f"Ansökta vs Beviljade platser för kurs: {course_name}",
        labels={"Platser": "Antal platser"},
        category_orders={"År": ALL_YEARS}
    )
    return fig

def update_chart(state):
    state.bar_chart = create_bar_chart(state.selected_course)

bar_chart = create_bar_chart(selected_course)

with tgb.Page() as page:
    with tgb.part(class_name="container card"):
        tgb.text("# Ansökta vs Beviljade platser per kurs", mode="md")
        with tgb.layout(columns="2 1"):
            with tgb.part(class_name="card"):
                tgb.chart(figure="{bar_chart}")
            with tgb.part(class_name="card"):
                tgb.selector(value="{selected_course}", lov=available_courses, dropdown=True)
                tgb.button("UPPDATERA", on_action=update_chart)

if __name__ == "__main__":
    Gui(page).run(dark_mode=False, use_reloader=True)
