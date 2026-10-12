"""Dashboard de lluvias y declaratorias de emergencia en el Perú.

Correr en local (desde la carpeta assignment_3/):
    streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Gráfico, mapa y tabla están en componentes_dashboard.py
from componentes_dashboard import mostrar_grafico_barras, mostrar_mapa, mostrar_tabla

# ---------------------------------------------------------------- configuracion
st.set_page_config(page_title="Lluvias y emergencias en el Perú", page_icon="🌧️", layout="wide")

# Streamlit Cloud corre la app desde la raíz del repo, no desde assignment_3/:
# por eso las rutas se arman a partir de la carpeta de este archivo.
CARPETA = Path(__file__).parent / "datos"


# ------------------------------------------------------------------ carga datos
# @st.cache_data guarda el resultado: sin esto, el archivo se lee otra vez
# cada vez que alguien mueve un filtro y la app va lentísima.
# El GeoJSON no se carga aquí: lo carga cargar_geojson() en componentes_dashboard.py.
@st.cache_data
def cargar():
    datos = pd.read_csv(CARPETA / "dataset.csv", dtype={"ubigeo": str})
    return datos


datos = cargar()

# ----------------------------------------------------------------------- filtros
st.sidebar.header("Filtros")

# Orden del CSV (por ubigeo); con sorted(), "Áncash" quedaría al final por la tilde.
departamentos = list(datos["departamento"].unique())
elegidos = st.sidebar.multiselect(
    "Departamento", departamentos, placeholder="Todos los departamentos"
)
# Si no se elige ninguno, se muestran los 25
if not elegidos:
    elegidos = departamentos

minimo = st.sidebar.slider(
    "Solo departamentos con lluvia de al menos… (mm)",
    0, int(datos["lluvia_total_mm"].max()), 0, step=50,
    help="Lluvia acumulada en la capital del 1 de enero al 31 de mayo de 2025. "
    "En 0 se ven los 25 departamentos.",
)

filtrado = datos[
    datos["departamento"].isin(elegidos) & (datos["lluvia_total_mm"] >= minimo)
]

# ------------------------------------------------------------------------ titulo
st.title("🌧️ ¿El Estado declara emergencia donde más llueve?")
st.caption("Lluvia ene-may 2025 en la capital de cada departamento · Fuente: Open-Meteo y decretos PCM (gob.pe)")

if filtrado.empty:
    st.warning("No hay departamentos que cumplan los filtros. Ajusta la selección.")
    st.stop()

# ---------------------------------------------------------------------- metricas
# Promedios (no sumas) para poder comparar la selección con el promedio de los
# 25 departamentos. El delta es gris: llover más no es "bueno" ni "malo".
lluvia_sel = filtrado["lluvia_total_mm"].mean()
dias_sel = filtrado["dias_lluvia_fuerte"].mean()
decl_sel = filtrado["declaratorias"].mean()

c1, c2, c3, c4 = st.columns(4)
c1.metric("Departamentos", f"{len(filtrado)} de {len(datos)}")
c2.metric(
    "Lluvia promedio (mm)", f"{lluvia_sel:,.0f}",
    delta=f"{lluvia_sel - datos['lluvia_total_mm'].mean():+,.0f} mm vs. Perú",
    delta_color="off",
)
c3.metric(
    "Días de lluvia fuerte (≥20 mm)", f"{dias_sel:.1f}",
    delta=f"{dias_sel - datos['dias_lluvia_fuerte'].mean():+.1f} días vs. Perú",
    delta_color="off",
    help="Promedio por capital, entre el 1 de enero y el 31 de mayo de 2025.",
)
c4.metric(
    "Declaratorias por departamento", f"{decl_sel:.1f}",
    delta=f"{decl_sel - datos['declaratorias'].mean():+.1f} vs. Perú",
    delta_color="off",
    help="Promedio de decretos de declaratoria que incluyeron a cada departamento.",
)

st.divider()

# Los tres componentes reciben `filtrado`, así responden a los filtros de la barra lateral.

# ---------------------------------------------------------------------- graficos
st.subheader("¿Dónde hubo más declaratorias?")
mostrar_grafico_barras(filtrado)

# -------------------------------------------------------------------------- mapa
# El mapa se une con los datos por ubigeo (texto, con el cero inicial: "01").
st.subheader("¿Dónde llovió más?")
mostrar_mapa(filtrado)

# ------------------------------------------------------------------------- tabla
st.subheader("Los datos por departamento")
mostrar_tabla(filtrado)
