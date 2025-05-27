import pandas as pd
import plotly.express as px

def create_trend_chart():
    trend_df = pd.read_csv("data/trender.csv", encoding="latin1")
    trend_df = trend_df.drop(columns=['ålder', 'kön'])
    trend_df['år'] = pd.to_numeric(trend_df['år'], errors='coerce')

    df_melt = trend_df.melt(id_vars=['år'], var_name='Inriktning', value_name='Antal')
    valda_inriktningar = ['Data/It', 'Teknik och tillverkning', 'Ekonomi, administration och försäljning']
    df_valda = df_melt[df_melt['Inriktning'].isin(valda_inriktningar)]

    fig = px.line(df_valda, x='år', y='Antal', color='Inriktning',
                  title='Trender för populära inriktningar 2015–2024',
                  labels={'år': 'År', 'Antal': 'Antal sökande'},
                  markers=True)

    fig.update_traces(marker=dict(color='black', line=dict(width=0)))

    # === Annotationer ===
    for inriktning, y_offset in zip(valda_inriktningar, [800, -1000, 800]):
        df_inriktn = df_valda[df_valda['Inriktning'] == inriktning]
        start = df_inriktn[df_inriktn['år'] == 2015]['Antal'].values[0]
        end = df_inriktn[df_inriktn['år'] == 2024]['Antal'].values[0]
        procent = ((end - start) / start) * 100
        fig.add_annotation(
            x=2024 if "Teknik" in inriktning else 2023.8,
            y=end + y_offset,
            text=f"<b>{procent:.1f}% ⬆️</b>",
            showarrow=False,
            font=dict(color="black", size=14),
            xanchor="left"
        )

    fig.update_layout(margin=dict(r=180), xaxis=dict(tickmode='linear', dtick=1))
    fig.add_annotation(
    xref="paper", yref="paper",
    x=0.04, y=1 ,
    text=(
        "Trots att <b>Ekonomi, administration<br>och försäljning</b><br> har flest sökande totalt sett,<br>"
        "är det <b>Data/IT</b> som<br>vuxit mest i procent sedan 2015."
    ),
    showarrow=False,
    font=dict(size=10, color="black"),
    align="left",
    bordercolor="black",
    borderwidth=1,
    borderpad=8,
    bgcolor="lightyellow",
)
    
    return fig

if __name__ == "__main__":
    fig = create_trend_chart()
    fig.show()

   