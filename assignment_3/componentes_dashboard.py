"""
Componentes del dashboard: gráfico de barras, mapa y tabla (Parte 3, pasos 4 y 5).

Este archivo no carga el CSV ni aplica filtros: eso lo hace app.py.
Cada función recibe el DataFrame ya filtrado, con las columnas originales
de datos/dataset.csv, y muestra un elemento en la página.

Uso desde app.py:
    from componentes_dashboard import mostrar_grafico_barras, mostrar_mapa, mostrar_tabla

    mostrar_grafico_barras(df_filtrado)
    mostrar_mapa(df_filtrado)
    mostrar_tabla(df_filtrado)
"""

import json
import unicodedata
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Carpeta de datos, ubicada respecto de este archivo (funciona en cualquier computadora)
CARPETA_DATOS = Path(__file__).parent / "datos"

# Nombres fáciles de entender para cada columna del dataset
ETIQUETAS = {
    "ubigeo": "Ubigeo",
    "departamento": "Departamento",
    "capital": "Capital",
    "lluvia_total_mm": "Lluvia total (mm)",
    "dias_lluvia_fuerte": "Días de lluvia fuerte (≥ 20 mm)",
    "declaratorias": "Declaratorias",
    "prorrogas": "Prórrogas",
}

# Escala de azules para la lluvia: claro = poca lluvia, oscuro = mucha lluvia
ESCALA_LLUVIA = ["#cde2fb", "#86b6ef", "#3987e5", "#1c5cab", "#0d366b"]

# Rango fijo de la escala de color. El máximo del dataset es 2019.9 mm (Loreto).
# Al fijarlo, un departamento conserva su color aunque cambie el filtro.
RANGO_LLUVIA = (0, 2100)


def normalizar_nombre(nombre):
    """Pasa un nombre a mayúsculas y sin tildes. Ejemplo: 'Áncash' -> 'ANCASH'."""
    sin_tildes = unicodedata.normalize("NFKD", nombre).encode("ascii", "ignore").decode("ascii")
    return sin_tildes.upper().strip()


@st.cache_data
def cargar_geojson():
    """
    Carga el mapa de departamentos y le agrega el ubigeo a cada uno.

    El GeoJSON solo trae el nombre del departamento (por ejemplo 'ANCASH'),
    así que usamos ubigeos.csv para saber qué código le corresponde.
    Los cambios se hacen en memoria: los archivos originales no se modifican.

    Devuelve el GeoJSON y la lista de departamentos que no encontraron ubigeo.
    """
    with open(CARPETA_DATOS / "departamentos.geojson", encoding="utf-8") as archivo:
        geojson = json.load(archivo)

    # dtype=str para conservar los ceros iniciales ('01' y no 1)
    ubigeos = pd.read_csv(CARPETA_DATOS / "ubigeos.csv", dtype={"ubigeo": str})

    # Diccionario {nombre normalizado: ubigeo}, por ejemplo {'ANCASH': '02'}
    ubigeo_por_nombre = {}
    for _, fila in ubigeos.iterrows():
        ubigeo_por_nombre[normalizar_nombre(fila["departamento"])] = fila["ubigeo"]

    # Agregar el ubigeo a cada departamento del mapa
    sin_ubigeo = []
    for departamento in geojson["features"]:
        nombre = departamento["properties"]["departamento"]
        ubigeo = ubigeo_por_nombre.get(normalizar_nombre(nombre))
        if ubigeo is None:
            sin_ubigeo.append(nombre)
        departamento["properties"]["ubigeo"] = ubigeo

    return geojson, sin_ubigeo


def mostrar_grafico_barras(df_filtrado):
    """Barras horizontales: declaratorias por departamento, coloreadas según la lluvia total."""
    if df_filtrado.empty:
        st.info("No hay departamentos seleccionados.")
        return

    # Plotly dibuja la primera fila abajo, por eso ordenamos de menor a mayor:
    # así el departamento con más declaratorias queda arriba.
    # En caso de empate, queda más arriba el que tuvo más lluvia.
    datos = df_filtrado.sort_values(["declaratorias", "lluvia_total_mm"])

    # Título calculado con los datos filtrados, para que siempre sea correcto
    maximo = datos["declaratorias"].max()
    lideres = datos[datos["declaratorias"] == maximo]["departamento"].tolist()
    mas_lluvia = datos.loc[datos["lluvia_total_mm"].idxmax()]

    if len(datos) == 1:
        titulo = f"{lideres[0]}: {maximo} declaratorias y {mas_lluvia['lluvia_total_mm']:.1f} mm de lluvia"
    else:
        if len(lideres) == 1:
            texto_declaratorias = f"{lideres[0]} tiene más declaratorias ({maximo})"
        else:
            texto_declaratorias = f"{len(lideres)} departamentos empatan con más declaratorias ({maximo})"
        texto_lluvia = f"{mas_lluvia['departamento']} tuvo más lluvia ({mas_lluvia['lluvia_total_mm']:.1f} mm)"
        titulo = f"{texto_declaratorias}; {texto_lluvia}"

    fig = px.bar(
        datos,
        x="declaratorias",
        y="departamento",
        orientation="h",
        color="lluvia_total_mm",
        color_continuous_scale=ESCALA_LLUVIA,
        range_color=RANGO_LLUVIA,
        hover_data={"lluvia_total_mm": ":.1f", "dias_lluvia_fuerte": True, "prorrogas": True},
        labels=ETIQUETAS,
        title=titulo,
        height=120 + 28 * len(datos),  # más departamentos, gráfico más alto
    )
    fig.update_layout(
        xaxis_title="Número de declaratorias de emergencia por lluvias (ene–may 2025)",
        yaxis_title=None,
        yaxis_automargin=True,  # deja espacio para nombres largos como "Madre de Dios"
    )
    st.plotly_chart(fig)


def mostrar_mapa(df_filtrado):
    """Mapa del Perú: cada departamento se pinta según su lluvia total."""
    if df_filtrado.empty:
        st.info("No hay departamentos seleccionados.")
        return

    geojson, sin_ubigeo = cargar_geojson()

    # Avisar si algún departamento del GeoJSON no encontró su ubigeo
    if sin_ubigeo:
        st.warning("Departamentos del mapa sin ubigeo: " + ", ".join(sin_ubigeo))

    # Avisar si algún departamento filtrado no tiene su forma en el mapa
    ubigeos_del_mapa = [departamento["properties"]["ubigeo"] for departamento in geojson["features"]]
    no_relacionados = df_filtrado[~df_filtrado["ubigeo"].isin(ubigeos_del_mapa)]
    if not no_relacionados.empty:
        st.warning("No se pudieron ubicar en el mapa: " + ", ".join(no_relacionados["departamento"]))

    # El cruce se hace por ubigeo (texto) entre el DataFrame y el GeoJSON
    fig = px.choropleth(
        df_filtrado,
        geojson=geojson,
        locations="ubigeo",
        featureidkey="properties.ubigeo",
        color="lluvia_total_mm",
        color_continuous_scale=ESCALA_LLUVIA,
        range_color=RANGO_LLUVIA,
        hover_name="departamento",
        hover_data={"ubigeo": True, "lluvia_total_mm": ":.1f", "declaratorias": True},
        labels=ETIQUETAS,
        title="Lluvia total entre enero y mayo de 2025, medida en la capital de cada departamento",
        height=650,
    )
    # Los departamentos que no están en el filtro se dibujan solo con su borde gris
    # (sin relleno), para que siempre se vea el Perú completo
    no_seleccionados = [ubigeo for ubigeo in ubigeos_del_mapa if ubigeo not in df_filtrado["ubigeo"].tolist()]
    fig.add_trace(
        go.Choropleth(
            geojson=geojson,
            locations=no_seleccionados,
            featureidkey="properties.ubigeo",
            z=[0] * len(no_seleccionados),
            colorscale=[[0, "rgba(0,0,0,0)"], [1, "rgba(0,0,0,0)"]],  # relleno transparente
            marker_line_color="#898781",
            showscale=False,
            hoverinfo="skip",
        )
    )
    # Encuadrar el mapa en el Perú y ocultar el mapa mundial de fondo
    fig.update_geos(fitbounds="geojson", visible=False, bgcolor="rgba(0,0,0,0)")
    fig.update_layout(margin={"l": 0, "r": 0, "t": 60, "b": 0})
    st.plotly_chart(fig)


def mostrar_tabla(df_filtrado):
    """Tabla con los departamentos filtrados, ordenada por declaratorias."""
    if df_filtrado.empty:
        st.info("No hay departamentos seleccionados.")
        return

    columnas = list(ETIQUETAS.keys())
    tabla = df_filtrado[columnas].sort_values(["declaratorias", "lluvia_total_mm"], ascending=False)
    tabla = tabla.rename(columns=ETIQUETAS)
    st.dataframe(tabla, hide_index=True)
