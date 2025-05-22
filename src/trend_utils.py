# trend_utils.py
import pandas as pd

def load_trend_data(filepath: str = "data/trender.csv") -> pd.DataFrame:
    """
    Läser in trender.csv och returnerar en lång DataFrame med kolumnerna:
    'år', 'inriktning', 'sökande'
    """
    # Läs in CSV-filen
    df = pd.read_csv(filepath)

    # Ta bort kolumner som inte behövs
    df = df.drop(columns=["ålder", "kön"])

    # Smält till långt format
    df_long = df.melt(id_vars=["år"], var_name="inriktning", value_name="sökande")

    # Konvertera år till int
    df_long["år"] = df_long["år"].astype(int)

    # Konvertera sökande till int (kan innehålla strängar)
    df_long["sökande"] = pd.to_numeric(df_long["sökande"], errors="coerce").fillna(0).astype(int)

    # Sortera för snyggare resultat
    df_long = df_long.sort_values(by=["inriktning", "år"]).reset_index(drop=True)

    return df_long

def save_trend_data(df: pd.DataFrame, output_path: str = "data/trender_lang.csv"):
    """
    Sparar den långa trenden i en ny CSV-fil.
    """
    df.to_csv(output_path, index=False)
