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

st.set_page_config(page_title="Dashboard Migranti", layout="wide", initial_sidebar_state="collapsed")


st.markdown(
    """
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    <style>
        .title-container {
            background-color:rgb(194, 4, 33);
            padding: 1px;
            color: white;
            font-size: 20px;
            font-weight: bold;
            text-align: center;
            border-radius: 9px;
        }
        .big-number {
            font-size: 30px !important;
            font-weight: bold;
        }
        .image-container {
            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;
            margin-bottom: 20px;
        }
        .image-container img {
            max-width: 40%; /* Riduci la dimensione dell'immagine */
            height: auto;
            border-radius: 10px;
        }
        .grid-container {
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;  /* 1° colonna più larga per i due grafici */
            grid-template-rows: auto auto; 
            gap: 10px;
            align-items: center;
            padding: 10px;
            border-radius: 10px;
        }
        .grid-item {
            padding: 10px;
            color: white;
            border-radius: 5px;
            text-align: center;
        }
        .main-container {
            display: flex;
            justify-content: center; /* Centra tutto il contenuto orizzontalmente */
            align-items: center;
            flex-direction: column;
            margin-right: 70px:
            width: 100%;
        }
        .custom-container {
            display: flex;
            flex-direction: column;
            align-items: center; /* Centra il testo orizzontalmente */
            justify-content: center; /* Centra verticalmente */
            text-align: center;
            margin-top: 15px; /* Abbassa il titolo di circa 2 cm */
        }
        .icon-text {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            font-size: 22px; /* Aumenta la dimensione del testo */
            font-weight: bold;
        }
        .material-icons {
            font-size: 50px !important; /* Icona Google Material 2x più grande */
            color: black;
        }
    </style>
""", unsafe_allow_html=True)


st.sidebar.title('Master ADABI')
st.sidebar.write(
    "Questa pagina è un elaborato frutto di un progetto di tirocinio. "
    "La prima pagina contiene delle statistiche ISTAT, mentre la seconda è una dashboard interattiva.")
st.sidebar.write(
"È possibile interagire con la mappa di Cuneo: cliccando su un comune, verranno visualizzate le statistiche di riferimento.")

left_co, cent_co,last_co = st.columns([1, 3 ,1])

st.markdown('<div class=" main-container">', unsafe_allow_html=True)

st.markdown('<div class="image-container">', unsafe_allow_html=True)
with cent_co:
    st.title(":green[IMM]IGR:red[ITALY]")
    st.image("/Users/simone/Desktop/tirocinio/GitHub/img/albanesi_sbarco-in-Puglia.jpg", caption="L'arrivo del mercantile Vlora con 20mila albanesi a bordo. 8 Agosto 1991 (Fotogramma).")
st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div class='title-container'>L'immigrazione straniera in numeri</div>", unsafe_allow_html=True)

col_map1, col_map2 = st.columns([1.5, 1.5])  # Due colonne: numeri e mappa

with col_map1:
    st.markdown('<div class="custom-container"><h3>Alcuni dati</h3></div>', unsafe_allow_html=True)
    
    st.markdown("""
        <div class="custom-container">
            <div class="icon-text" style="flex-direction: column;">
                <span class="material-icons">groups</span> 
                <span>Totale Immigrati in Italia:</span>
                <span style="font-weight: normal;">6.5 milioni</span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="custom-container">
            <div class="icon-text" style="flex-direction: column;">
                <span class="material-icons">bar_chart</span> 
                <span>Percentuale di popolazione straniera:</span>
                <span style="font-weight: normal;">10.5% </span>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="custom-container">
            <div class="icon-text" style="flex-direction: column;">
                <span class="material-icons">flag</span> 
                <span>Area di provenienza:</span>
                <span style="font-weight: normal;">46.3% Europa,  23.4% Asia <br> 22.7% Africa, 7.6% America</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ✅ 3. Dati popolazione per regione
data_regioni = {
    "Regione": ["Piemonte", "Valle d'Aosta/Vallée d'Aoste", "Liguria", "Lombardia", "Trentino-Alto Adige/Südtirol", 
                "Veneto", "Friuli-Venezia Giulia", "Emilia-Romagna",
                "Toscana", "Umbria", "Marche", "Lazio", "Abruzzo", "Molise", "Campania", 
                "Puglia", "Basilicata", "Calabria", "Sicilia", "Sardegna"],
    "Immigrati": [428905, 8568, 155646, 1203138, 102890, 501161, 120144, 560953, 
                  424066, 88579, 132011, 643312, 85828, 13231, 263680, 147269, 25410, 99907, 196919, 52041]
}

df_regioni = pd.DataFrame(data_regioni)

# ✅ 4. Calcolare la percentuale per ogni regione
totale_immigrati = df_regioni["Immigrati"].sum()
df_regioni["Percentuale"] = (df_regioni["Immigrati"] / totale_immigrati) * 100
migranti_dict = df_regioni.set_index("Regione")[["Immigrati", "Percentuale"]].to_dict(orient="index")


# ✅ 5. Scaricare il GeoJSON delle regioni italiane
geojson_url = "https://raw.githubusercontent.com/openpolis/geojson-italy/master/geojson/limits_IT_regions.geojson"
response = requests.get(geojson_url)
italy_geojson = response.json()

for feature in italy_geojson["features"]:
    regione = feature["properties"]["reg_name"]
    if regione in migranti_dict:
        feature["properties"]["Immigrati"] = f"{migranti_dict[regione]['Immigrati']:,}"  # 🔹 Numero con separatore di migliaia
        feature["properties"]["Percentuale"] = f"{migranti_dict[regione]['Percentuale']:.2f}%"  # 🔹 Percentuale formattata

# ✅ 6. Creare la mappa con Folium
m = folium.Map(location=[42, 12], zoom_start=4.5, tiles="cartodb positron", draggin = False,  scrollWheelZoom=False,)

# ✅ 7. Aggiungere la mappa coropletica con percentuale
choropleth = folium.Choropleth(
    geo_data=italy_geojson,
    name="choropleth",
    data=df_regioni,
    columns=["Regione", "Percentuale"],  # 🔹 Usiamo la percentuale per il colore
    key_on="feature.properties.reg_name",
    fill_color="YlOrRd",
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name="Distribuzione % Immigrati per Regione"
).add_to(m)

folium.GeoJson(
    italy_geojson,
    name="Regioni",
    style_function=lambda feature: {
        "fillColor": "transparent",
        "color": "black",
        "weight": 0.5,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["reg_name", "Immigrati", "Percentuale"],  # 🔹 Ora i campi sono separati!
        aliases=["Regione:", "Immigrati:", "Percentuale:"],
        localize=True,
        sticky=True,
        labels=True
    )
).add_to(m)

# ✅ 10. Mostrare la mappa in Streamlit
with col_map2:
        with st.container(height = 500, border = False ):
            st_map = st_folium(map, width=900, height=450)


st.markdown('<div class="title-container">Stranieri residenti al 1° gennaio 2024</div>', unsafe_allow_html=True)
st.markdown('<div class="grid-container">', unsafe_allow_html=True)

# Creazione del dataset
data = {
    "Paese": [
        "Romania", "Albania", "Marocco", "Cina", "Ucraina",
        "Bangladesh", "India", "Egitto", "Pakistan", "Filippine",
        "Nigeria", "Senegal", "Sri Lanka", "Tunisia", "Perù",
        "Moldova", "Polonia", "Ecuador", "Brasile", "Macedonia",
        "Bulgaria", "Ghana", "Russia", "Kosovo", "Germania",
        "Georgia", "Costa d'Avorio", "Francia", "Repubblica Dominicana",
        "Serbia", "Spagna", "Regno Unito", "Gambia", "Cuba",
        "El Salvador", "Mali", "Colombia", "Turchia", "Iran",
        "Bosnia-Erzegovina", "Algeria", "Afghanistan", "Burkina Faso",
        "Camerun", "Stati Uniti", "Croazia", "Argentina", "Venezuela",
        "Guinea", "Bolivia", "Bielorussia"
    ],
    "Popolazione": [
        1073196, 416229, 412346, 308984, 273484,
        192678, 170880, 161551, 159332, 156642,
        128487, 115047, 110532, 110395, 105265,
        102667, 73320, 59394, 51918, 49366,
        48659, 46529, 41631, 36046, 35104,
        33674, 31816, 30896, 29791, 29679,
        28932, 26202, 24779, 24756, 24349,
        23233, 23155, 21611, 19887, 19577,
        19142, 17642, 16768, 16570, 16534,
        15349, 15342, 15003, 13670, 12478,
        9505
    ]
}

df = pd.DataFrame(data)

# Ordina i dati in base alla popolazione per migliorare la leggibilità
df = df.sort_values("Popolazione", ascending=True)

# Creazione del grafico Altair
chart = alt.Chart(df).mark_bar().encode(
    x=alt.X("Popolazione:Q", title="Popolazione"),
    y=alt.Y("Paese:N", sort="-x", title="Paese di cittadinanza"),
    tooltip=[
        alt.Tooltip("Paese:N", title="Paese"),
        alt.Tooltip("Popolazione:Q", title="Popolazione", format=",")
    ]).properties(
    width=700,
    height=600,
    title="Popolazione per Paese di cittadinanza"
).configure_title(
        anchor='middle'
    )

# Streamlit UI
st.altair_chart(chart, use_container_width=True)

st.markdown('<div class="title-container">Altri Numeri</div>', unsafe_allow_html=True)
st.markdown('<div class="grid-container">', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1,1,1])  # La colonna 1 è più larga per ospitare i due grafici

# 🔹 **Grafico 1: Sbarchi (2000-2022)**
df_sbarchi = pd.DataFrame({
    "Anno": list(range(2000, 2023)),
    "Sbarchi": [26817, 20143, 23719, 14331, 13635, 22939, 22016, 20455, 36951, 9537, 4406, 62692,
                13267, 42925, 170100, 153842, 181436, 119369, 23370, 11471, 34154, 67477, 105129]
})

chart_sbarchi = alt.Chart(df_sbarchi).mark_line(point=True).encode(
    x=alt.X("Anno:O", title="Anno"),
    y=alt.Y("Sbarchi:Q", title="Numero di Sbarchi"),
    tooltip=["Anno", "Sbarchi"]
).properties(width=600, height=300, title={ "text": "Sbarchi sulle coste italiane (2000-2022)", 
    "subtitle": "Fonte: Elaborazioni su dati ISTAT "
    })

with col2:
    st.altair_chart(chart_sbarchi, use_container_width=True)

# 🔹 **Grafico 2: Popolazione straniera (2002-2019)**
df_popolazione = pd.DataFrame({
    "Anno": list(range(2002, 2020)),
    "Maschi": [665663, 738644, 939459, 1131951, 1235134, 1318952, 1528676, 1713842, 1828641, 1930140,
               2022797, 2168037, 2252743, 2270954, 2277217, 2284218, 2338162, 2414285],
    "Femmine": [675751, 744633, 954468, 1137067, 1263277, 1373070, 1622877, 1845011, 2007708, 2171195,
                2296404, 2442456, 2534423, 2564291, 2553825, 2534415, 2545289, 2581873],
    "Totale": [1341414, 1483277, 1893927, 2269018, 2498411, 2692022, 3151553, 3558853, 3836349, 4101335,
               4319201, 4610493, 4787166, 4835245, 4831042, 4818633, 4883451, 4996158]
})

df_popolazione = df_popolazione.melt("Anno", var_name="Categoria", value_name="Popolazione")

chart_popolazione = alt.Chart(df_popolazione).mark_line(point=True).encode(
    x=alt.X("Anno:O", title="Anno"),
    y=alt.Y("Popolazione:Q", title="Popolazione"),
    color="Categoria",
    tooltip=["Anno", "Categoria", "Popolazione"]
).properties(width=600, height=300,title={
    "text": "Popolazione straniera in Italia (2002-2019)", 
    "subtitle": "Fonte: Elaborazioni su dati ISTAT "
    })

with col1:
    st.altair_chart(chart_popolazione, use_container_width=True)

with col3:
    data_morti = pd.DataFrame({
        'Anno': [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
        'Morti o dispersi': [2275, 1327, 1401, 2078, 2439, 3160, 1758, 18]
    })

    chart_morti = alt.Chart(data_morti).mark_bar(color='orange').encode(
        x=alt.X('Anno:O', title="Anno"),
        y=alt.Y('Morti o dispersi:Q', title="Numero di morti o dispersi"),
        tooltip=['Anno', 'Morti o dispersi']
    ).properties(width=600, height=300,title={
    "text": "Morti o dispersi", 
    "subtitle": "Fonte: Elaborazioni su dati ISTAT "
    })


    st.altair_chart(chart_morti, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

#st.markdown("Vai alla sezione **Dashboard Lavoratori** dal menu laterale.")
