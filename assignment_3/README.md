# Assignment 3 – Visualización, mapas y dashboard

Pregunta de la tarea 3:
¿Pueden convertir datos crudos en algo que cualquiera entienda en 2 minutos?

## Dashboard
**Dashboard público:** https://lluvias-peru-grupo08.streamlit.app/

### ¿Qué pregunta responde?

¿El Estado declaró más emergencias por lluvias en los departamentos donde más llovió entre enero y mayo de 2025?

### Datos y fuente

Usamos `datos/dataset.csv`, que es la tabla final de la tarea 2. Tiene una fila por departamento (los 24 departamentos y el Callao).

- **Lluvia:** la sacamos de la API histórica de Open-Meteo. Sumamos la lluvia diaria del 1 de enero al 31 de mayo de 2025 en la capital de cada departamento. Un "día de lluvia fuerte" es un día con 20 mm o más.
- **Declaratorias y prórrogas:** las obtuvimos haciendo scraping de las normas legales de la PCM publicadas en gob.pe entre el 1 de enero y el 31 de mayo de 2025. Nos quedamos solo con los decretos por lluvias: 18 en total (11 declaratorias y 7 prórrogas). Para cada departamento contamos en cuántos de esos decretos aparece.
- **Mapa:** usamos `datos/departamentos.geojson` y lo unimos con los datos por el ubigeo de `datos/ubigeos.csv`. La fuente del GeoJSON está pendiente de confirmar.

### Hallazgos

1. **Que llueva más no siempre significó más declaratorias.** Madre de Dios tuvo 1751.3 mm y 30 días de lluvia fuerte (el máximo de todos), pero solo 3 declaratorias. En cambio, Cusco tuvo el mayor número de declaratorias (9) con 801.3 mm.
2. **Algunos departamentos con muy poca lluvia tuvieron varias declaratorias.** En Lima se registraron 41.1 mm y tuvo 8 declaratorias. Tacna, el departamento con menos lluvia (17.4 mm), tuvo 6.

### Limitaciones

- La lluvia se midió en un solo punto por departamento, su capital. En Lima ese punto es Huacho. Puede haber llovido mucho más en otras zonas del departamento, por ejemplo en las partes altas.
- Solo cubre de enero a mayo de 2025.
- 8 de las 11 declaratorias incluyen entre 14 y 22 departamentos a la vez, así que muchos departamentos suman casi lo mismo aunque en cada uno haya llovido muy distinto.
- Contar declaratorias no dice qué tan grave fue la emergencia ni a cuántas personas afectó.
- Son solo 25 departamentos y no tomamos en cuenta otros factores. Por eso el dashboard muestra relaciones, pero no permite afirmar que la lluvia causó las declaratorias.
