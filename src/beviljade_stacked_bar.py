import pandas as pd
import plotly.graph_objects as go

# Läs in data
df = pd.read_excel("data/resultat-ansokningsomgang-2024.xlsx", sheet_name="Tabell 3", skiprows=5)

# Beräkna avslag
df["Avslag"] = df["Sökta platser totalt"] - df["Beviljade platser totalt"]

# Gruppera och summera per utbildningsområde
df_grouped = df.groupby("Utbildningsområde").agg({
    "Beviljade platser totalt": "sum",
    "Avslag": "sum"
}).reset_index()

# Skapa stacked bar
fig = go.Figure()

fig.add_trace(go.Bar(
    y=df_grouped["Utbildningsområde"],
    x=df_grouped["Beviljade platser totalt"],
    name="Beviljade",
    marker_color='green',
    orientation='h'
))

fig.add_trace(go.Bar(
    y=df_grouped["Utbildningsområde"],
    x=df_grouped["Avslag"],
    name="Avslag",
    marker_color='red',
    orientation='h'
))

fig.update_layout(
    barmode='stack',
    title="Beviljade och avslagna platser per utbildningsområde",
    xaxis_title="Antal platser",
    yaxis_title="Utbildningsområde",
    yaxis=dict(autorange="reversed")
)

fig.show()
