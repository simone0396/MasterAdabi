import json
import tempfile
import geojson
import pandas as pd
import folium
import os
import altair as alt
import geopandas as gpd
import requests
import streamlit as st 
from streamlit_folium import st_folium 
import geopandas as gdp
import folium.features
import streamlit as st 
import seaborn as sns
import matplotlib as plt
import matplotlib.pyplot as plt 
import pandas as pd
import folium
import altair as alt


st.set_page_config(page_title="MasterAdabi", layout="wide")
st.title('Dashboard Operai Agricoli Nella Provincia del Cuneese')
st.caption('Mappa di Cuneo interattiva')

st.sidebar.title('Master ADABI')
st.sidebar.write(
    "Questa pagina è un elaborato frutto di un progetto di tirocinio. ")
st.sidebar.write(
    "La prima pagina contiene delle statistiche ISTAT, mentre la seconda è una dashboard interattiva.")
st.sidebar.write(
"È possibile interagire con la mappa di Cuneo: cliccando su un comune o selezionandolo nella barra di ricerca, verranno visualizzate le statistiche di riferimento.")

    

# ==========================
# Funzione 

main1, main2 = st.columns([3,1])  # La colonna 1 è più larga per ospitare i due grafici

def mostra_info_comune(st_map, df, df_aziende):
    comune_list = [''] + list(df['comune_pdf'].unique())
    comune_list.sort()

    map_comune = ''
    if st_map.get('last_active_drawing'):
        map_comune = st_map['last_active_drawing']['properties']['name']

    if not map_comune:
        map_comune = ''

    selected_comune = map_comune if map_comune in comune_list else ''

    with main2:
        selected_comune = st.selectbox('Seleziona un Comune', comune_list, index=comune_list.index(selected_comune) if selected_comune in comune_list else 0)

    nome_comune = selected_comune

    if nome_comune:
        if nome_comune in df['comune_pdf'].values:
            numero_teste = df[df['comune_pdf'] == nome_comune]['conta'].values[0]
            st.subheader(f'Statistiche per il comune di {nome_comune}:')
            st.metric(label="Numero di lavoratori:", value=numero_teste)

            st.subheader(f'Grafici per il comune di {nome_comune}:')
            df_comune = df[df['comune_pdf'] == nome_comune]

            chart_hist = alt.Chart(df_comune).mark_bar().encode(
                y=alt.Y('count()', title='Frequenza'),
                x=alt.X('classe_eta', title='Gruppi Di Età', bin=False),
                color='genere'
            )

            dominio_provenienza = ["Euro-est", "Italia", "India", "Africa", "Sub-shara", "Americhe"]
            range_colori = ["#1f77b4", "#3c9c2d", "#d1ce24", "#d62728", "#db8318", "#0e8a81"]

            provenienza_counts = df_comune['provenienza'].value_counts().reset_index()
            provenienza_counts.columns = ['provenienza', 'values']

            base = alt.Chart(provenienza_counts).encode(
                theta=alt.Theta("values:Q", stack=True),
                radius=alt.Radius("values:Q", scale=alt.Scale(type="sqrt", zero=True, rangeMin=50)),
                color=alt.Color("provenienza:N", scale=alt.Scale(domain=dominio_provenienza, range=range_colori),
                                legend=alt.Legend(title="Provenienza"))
            )

            c1 = base.mark_arc(innerRadius=20, stroke="#fff")
            c2 = base.mark_text(radiusOffset=10).encode(text="values:Q")
            chart_pie = c1 + c2

            # Aggiungi logica per aggiornare la cittadinanza se la provenienza è "Italia"
            df_comune['cittadinanza'] = df_comune.apply(
                lambda row: 'Italia' if row['provenienza'] == 'Italia' and row['cittadinanza'] != 'Italia' else row['cittadinanza'],
                axis=1
            )

            chart_hist_eta = alt.Chart(df_comune).mark_bar().encode(
                y=alt.Y('count()', title='Frequenza'),
                x=alt.X('eta', title='Età', bin=False),
                color=alt.Color('genere', scale=alt.Scale(scheme='category10'))
            )

            cittadinanza_counts = df_comune['cittadinanza'].value_counts().reset_index()
            cittadinanza_counts.columns = ['cittadinanza', 'values']
            
            # Crea il grafico delle cittadinanze
            chart_cittadinanza = alt.Chart(cittadinanza_counts).mark_bar().encode(
                x=alt.X('cittadinanza:N', title='Cittadinanza', sort='-y'),
                y=alt.Y('values:Q', title='Numero di residenti'),
                color=alt.Color('cittadinanza:N', scale=alt.Scale(scheme='category20'))
            ).properties(title='Distribuzione delle Cittadinanze')

            col1, col2 = st.columns(2)
            col1.altair_chart(chart_hist, theme="streamlit", use_container_width=True)
            col2.altair_chart(chart_pie, theme="streamlit", use_container_width=True)
            st.altair_chart(chart_hist_eta, theme="streamlit", use_container_width=True)
            st.altair_chart(chart_cittadinanza, theme="streamlit", use_container_width=True)

        aziende_comune = df_aziende[df_aziende['Comune_Azienda'] == nome_comune]

        if not aziende_comune.empty:
            numero_aziende = len(aziende_comune)
            st.subheader(f'Aziende nel comune di {nome_comune} ({numero_aziende} aziende trovate):')
            aziende_comune['Nome_Azienda'] = aziende_comune['Nome_Azienda'].str.title()

            colonne_da_escludere = ['conta_aziende']
            colonne_da_escludere = [col for col in colonne_da_escludere if col in aziende_comune.columns]

            aziende_comune_visual = aziende_comune.drop(columns=colonne_da_escludere)
            st.dataframe(aziende_comune_visual, use_container_width=True)
        else:
            st.write("Nessuna azienda trovata per questo comune.")
    else:
        if map_comune:
            st.subheader(f'Le informazioni per il comune di {map_comune} non sono presenti nel Database')



def main():
    csv_path = os.path.join("dati", "migranti2.csv")
    azienda_path = os.path.join("dati", "dataset_aziende2.csv")
    df = pd.read_csv(csv_path)
    df_aziende = pd.read_csv(azienda_path)
    df_aziende['Comune_Azienda'] = df_aziende['Comune_Azienda'].str.capitalize()
    conta_aziende = df_aziende['Comune_Azienda'].value_counts().reset_index()
    conta_aziende.columns = ['Comune_Azienda', 'conta_aziende']
    df_aziende = df_aziende.merge(conta_aziende, on='Comune_Azienda', how='left')


    @st.cache_data
    def load_geojson(url):
        response = requests.get(url)
        return response.json()

    provincia_geo = load_geojson("https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_P_4_municipalities.geojson")


    # Creazione della mappa

    mappa_cuneo = folium.Map(location=[44.45807035, 7.858136691151624], zoom_start=8, scrollWheelZoom=False, tiles='CartoDB positron')
    
    max_val = df['conta'].max()
    bins = [0, 50, 100, 200, 350, 500, 1000]
    if max_val > bins[-1]:
        bins.append(max_val)

    choropleth = folium.Choropleth(
        geo_data=provincia_geo,
        data=df,
        columns=['comune_pdf', 'conta'],
        key_on='feature.properties.name',
        nan_fill_color="white",
        nan_fill_opacity= 0.5,
        line_opacity=0.8,
        legend_name='Lavoratori Per Comune',
        highlight=True,
        threshold_scale = bins,
        name = 'lavoratori'
    ).add_to(mappa_cuneo)
    
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['name'], labels=False))
    
    mappa_aziende = folium.Choropleth(
        geo_data=provincia_geo,
        data=df_aziende,
        columns=['Comune_Azienda', 'conta_aziende'],
        key_on='feature.properties.name',
        nan_fill_color="white",
        nan_fill_opacity= 0.5,
        line_opacity=0.8,
        legend_name='Aziende nel territorio',
        overlay=True,
        fill_color= 'Purples',
        highlight=True,
        name = 'aziende'
    ).add_to(mappa_cuneo)
    
    mappa_aziende.geojson.add_child(
        folium.features.GeoJsonTooltip(['name'], labels=False))
    
    folium.LayerControl(position='bottomleft', collapsed=False, name = 'layer').add_to(mappa_cuneo)

            
    with main1:
        with st.container(height = 550, border = False ):
            st_map = st_folium(mappa_cuneo, width=900, height=500)


    mostra_info_comune(st_map, df, df_aziende)

if __name__ == "__main__":
    main()
