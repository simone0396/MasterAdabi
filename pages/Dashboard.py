import json
import tempfile
import geojson
import pandas as pd
import folium
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


st.set_page_config(page_title="Dashboard Lavoratori", layout="wide")
st.title('Dashboard Operai Agricoli Nella Provincia del Cunese')
st.caption('Mappa Cuneo')

st.sidebar.title('Master ADABI')
st.sidebar.write(
    "Questa pagina è un elaborato frutto di un progetto di tirocinio. "
    "La prima pagina contiene delle statistiche ISTAT, mentre la seconda è una dashboard interattiva."
"È possibile interagire con la mappa di Cuneo: cliccando su un comune, verranno visualizzate le statistiche di riferimento.")

    

# ==========================
# Funzione principale
# ==========================
main1, main2 = st.columns([3,1])  # La colonna 1 è più larga per ospitare i due grafici

def mostra_info_comune(st_map, df):
    # Creazione della lista dei comuni
    comune_list = [''] + list(df['comune_pdf'].unique())
    comune_list.sort()

    # Controllo se esiste una selezione valida dalla mappa
    map_comune = ''
    if st_map.get('last_active_drawing'):
        map_comune = st_map['last_active_drawing']['properties']['name']

    # Se map_comune è None o una stringa vuota, non fare nulla (o usa un valore predefinito)
    if not map_comune:
        map_comune = ''

    # Se non è stato selezionato nessun comune dalla mappa, la selectbox sarà vuota
    selected_comune = map_comune if map_comune in comune_list else ''

    # Selezione del comune tramite selectbox
    with main2:
        selected_comune = st.selectbox('Seleziona un Comune', comune_list, index=comune_list.index(selected_comune) if selected_comune in comune_list else 0)

    # Determinazione del comune da visualizzare (priorità alla selezione dalla selectbox)
    nome_comune = selected_comune

    # Verifica se un comune è stato selezionato e se ci sono dati per il comune selezionato
    if nome_comune:
        if nome_comune in df['comune_pdf'].values:
            numero_teste = df[df['comune_pdf'] == nome_comune]['conta'].values[0]
            st.subheader(f'Statistiche il comune di {nome_comune}:')
            st.metric(label="Numero di lavoratori:", value=numero_teste)

            st.subheader(f'Grafici per il comune di {nome_comune}:')
            df_comune = df[df['comune_pdf'] == nome_comune]

            # Grafico a barre per gruppi di età e genere
            chart_hist = alt.Chart(df_comune).mark_bar().encode(
                y=alt.Y('count()', title='Frequenza'),
                x=alt.X('classe_eta', title='Gruppi Di Età', bin=False),
                color='genere'
            )

            # Preparazione dei dati per il grafico a torta
            provenienza_counts = df_comune['provenienza'].value_counts().reset_index()
            provenienza_counts.columns = ['provenienza', 'values']

            # Creazione del grafico a torta
            base = alt.Chart(provenienza_counts).encode(
                theta=alt.Theta("values:Q", stack=True),
                radius=alt.Radius("values:Q", scale=alt.Scale(type="sqrt", zero=True, rangeMin=50)),
                color=alt.Color("provenienza:N", legend=alt.Legend(title="Provenienza"))
            )

            c1 = base.mark_arc(innerRadius=20, stroke="#fff")
            c2 = base.mark_text(radiusOffset=10).encode(text="values:Q")

            chart_pie = c1 + c2

            # Grafico a barre per età e genere
            chart_hist_eta = alt.Chart(df_comune).mark_bar().encode(
                y=alt.Y('count()', title='Frequenza'),
                x=alt.X('eta', title='Età', bin=False),
                color=alt.Color('genere', scale=alt.Scale(scheme='category10'))
            )

            # Creazione delle colonne
            col1, col2 = st.columns(2)

            # Inserimento dei grafici nelle colonne
            col1.altair_chart(chart_hist, theme="streamlit", use_container_width=True)
            col2.altair_chart(chart_pie, theme="streamlit", use_container_width=True)
            st.altair_chart(chart_hist_eta, theme="streamlit", use_container_width=True)
        else:
            if map_comune:
                st.subheader(f'Le informazioni per il comune di {nome_comune} non sono presenti nel Database 1')
    else:
        if map_comune:
            st.subheader(f'Le informazioni per il comune di {map_comune} non sono presenti nel Database')


def main():
    # Caricamento dei dati
    df = pd.read_csv('/Users/simone/Desktop/tirocinio/GitHub/dati/migranti2.csv')
    provincia_geo = gdp.read_file('/Users/simone/Desktop/tirocinio/Dashboard/dati/limits_P_4_municipalities.geojson')

    # Creazione della mappa
    map = folium.Map(location=[44.45807035, 7.858136691151624], zoom_start=8, scrollWheelZoom=False, tiles='CartoDB positron')
    
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
        legend_name='Numero Teste Per Comune',
        highlight=True,
        threshold_scale = bins,
    ).add_to(map)
    choropleth.geojson.add_to(map)
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['name'], labels=False),
        folium.LayerControl().add_to(map)
    )
    
    folium.LayerControl().add_to(map)

    #aggiunta del css perche la mappa andava fuori il container
    st.markdown("""
        <style>
            .streamlit-expanderHeader {
                padding-bottom: 0;
            }
            .folium-map {
                height: 100% !important;
                margin-bottom: 0 !important;
                padding: 0 !important;
            }
            .stContainer {
                height: 500px;
                overflow: hidden;
            }
        </style>
    """, unsafe_allow_html=True)
    
    with main1:
        with st.container(height = 500, border = False ):
            st_map = st_folium(map, width=900, height=450)


    mostra_info_comune(st_map, df)

if __name__ == "__main__":
    main()
