# import pandas as pd
# import duckdb
# import json
# from difflib import get_close_matches
# import numpy as np 
# import plotly.graph_objects as go


# def run_map():
#     df = pd.read_excel(
#         "data/resultat-ansokningsomgang-2024.xlsx", sheet_name="Tabell 3", skiprows=5
#     )

#     decisions = df["Beslut"].value_counts()
#     approved, total = decisions.get("Beviljad", 0), decisions.sum()

#     # Duckdb query för att hämta län som blivit beviljade
#     df_regions = duckdb.query(
#         """--sql
#         SELECT 
#             län, 
#             COUNT_IF(beslut ='Beviljad') AS Beviljade
#         FROM df 
#         WHERE län != 'Flera kommuner'
#         GROUP BY
#             län
#         ORDER BY 
#             beviljade 
#         DESC
#     """
#     ).df()

#     with open("assets/swedish_regions.geojson", "r", encoding="utf-8") as file:
#         json_data = json.load(file)

#     properties = [feature.get("properties") for feature in json_data.get("features")]
#     region_codes = {
#         property.get("name"): property.get("ref:se:länskod") for property in properties
#     }

#     region_codes_map = []
#     valid_region_names = []

#     for region in df_regions["Län"]:
#         matches = get_close_matches(region, region_codes.keys(), n=1)
#         if matches:
#             region_name = matches[0]
#             code = region_codes[region_name]
#             region_codes_map.append(code)
#             valid_region_names.append(region)  # Behåll bara de som matchade
#         else:
#             print(f"Ingen match hittad för: {region}")

#     # Skapa kartan
#     df_regions["log_beviljade"] = np.log(df_regions["Beviljade"] + 1)

#     fig = go.Figure(
#         go.Choroplethmapbox(
#             geojson=json_data,
#             locations=region_codes_map,
#             z=df_regions["log_beviljade"],
#             featureidkey="properties.ref:se:länskod",
#             customdata=df_regions["Beviljade"],
#             marker_opacity=0.9,
#             marker_line_width=0.4,
#             text=df_regions["Län"],
#             hovertemplate="<b>%{text}</b><br>Beviljade utbildningar: %{customdata}<extra></extra>",
#             showscale=True,
#             colorscale="deep",
#             colorbar=dict(
#                 x=1,           # flytta åt höger, testa andra värden vid behov
#                 xanchor="left",
#                 y=0.5,
#                 yanchor="middle"
#             )
#         )
#     )
#     # Uppdatera kartstyle
#     fig.update_layout(
#         mapbox=dict(style="white-bg", zoom=3.3, center=dict(lat=63, lon=9.89)),
#         width=470,
#         height=500,
#         margin=dict(r=0, t=50, l=0, b=0),
#         title=dict(
#             text=f"""
# <b>Beviljade YH-utbildningar 2024</b>
# <br>Den här kartan visar antalet<br>utbildningar som beviljats i varje län.
# <br>En djupare blå färg indikerar<br>fler godkända utbildningar
# <br>
# <br>Totalt godkändes <b>{approved}</b> av <b>{total}</b><br>ansökningar,
# <br>vilket motsvarar en<br>beviljandegrad på <b>{approved/total*100:.0f}%</b>
# <br>
# <br>Stockholm, Västra Götaland<br>och Skåne har<br>flest beviljade utbildningar
# """,
#             x=0.06,
#             y=0.75,
#             font=dict(size=13),
#         ),
#     )

#     return fig



# if __name__ == "__main__":
#     run_map()


import pandas as pd 
import duckdb
import json
from difflib import get_close_matches
import numpy as np 
import plotly.graph_objects as go

def run_map():
    df = pd.read_excel("data/resultat-ansokningsomgang-2024.xlsx", sheet_name="Tabell 3", skiprows=5)

    decisions = df["Beslut"].value_counts()
    approved, total = decisions.get("Beviljad", 0), decisions.sum()

    df_regions = duckdb.query(
        """--sql
        SELECT 
            län, 
            COUNT_IF(beslut ='Beviljad') AS Beviljade
        FROM df 
        WHERE län != 'Flera kommuner'
        GROUP BY
            län
        ORDER BY 
            beviljade DESC
        """
    ).df()

    with open("assets/swedish_regions.geojson", "r", encoding="utf-8") as file:
        json_data = json.load(file)

    properties = [feature.get("properties") for feature in json_data.get("features")]
    region_codes = {
        property.get("name"): property.get("ref:se:länskod") for property in properties
    }

    region_codes_map = []
    valid_region_names = []

    for region in df_regions["Län"]:
        matches = get_close_matches(region, region_codes.keys(), n=1)
        if matches:
            region_name = matches[0]
            code = region_codes[region_name]
            region_codes_map.append(code)
            valid_region_names.append(region)
        else:
            print(f"Ingen match hittad för: {region}")

    df_regions["log_beviljade"] = np.log(df_regions["Beviljade"] + 1)

    fig = go.Figure(
        go.Choroplethmapbox(
            geojson=json_data,
            locations=region_codes_map,
            z=df_regions["log_beviljade"],
            featureidkey="properties.ref:se:länskod",
            customdata=df_regions["Beviljade"],
            marker_opacity=0.9,
            marker_line_width=0.4,
            text=df_regions["Län"],
            hovertemplate="<b>%{text}</b><br>Beviljade utbildningar: %{customdata}<extra></extra>",
            showscale=True,
            colorscale="deep",
            colorbar=dict(
                x=1,
                xanchor="left",
                y=0.5,
                yanchor="middle"
            )
        )
    )

    fig.update_layout(
        mapbox=dict(style="white-bg", zoom=3.3, center=dict(lat=63, lon=9.89)),
        width=470,
        height=500,
        margin=dict(r=0, t=50, l=0, b=0),
        title=dict(
            text=f"""
<b>Beviljade YH-utbildningar 2024</b>
<br>Den här kartan visar antalet<br>utbildningar som beviljats i varje län.
<br>En djupare blå färg indikerar<br>fler godkända utbildningar
<br><br>Totalt godkändes <b>{approved}</b> av <b>{total}</b><br>ansökningar,
<br>vilket motsvarar en<br>beviljandegrad på <b>{approved/total*100:.0f}%</b>
<br><br>Stockholm, Västra Götaland<br>och Skåne har<br>flest beviljade utbildningar
""",
            x=0.06,
            y=0.75,
            font=dict(size=13),
        ),
    )

   
    return fig

if __name__ == "__main__":
    run_map()
