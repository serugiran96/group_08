# Assignment 2 (Grupo 8)

# Bitácora de uso de IA 

Herramienta usada: Claude Code.

Registramos los momentos en que la IA nos dio algo incorrecto, incompleto o que no funcionó, cómo nos dimos cuenta y cómo lo corregimos.

# Parte 1 – Scraping

## Paso 5: el recorrido mes por mes, no mostraba lo extraído

**1. ¿Qué le pedimos a la IA?**

De acuerdo a la indicación, se pidio verificar el código para repetir los pasos 2 a 4 (abrir la búsqueda, leer el total y extraer cada resultado) en los cinco meses de la temporada.

**2. ¿Qué nos respondió?**
```python
    verificacion.append({
        "mes": nombre_mes,
        "resultados_totales": total,
        "resultados_extraidos": len(articulos),
    })
    print(nombre_mes, "listo")
    time.sleep(2)   # pausa entre páginas (ver robots.txt)
```

**3. ¿Qué estaba mal y cómo nos dimos cuenta?**

El código extraía bien las normas, pero solo imprimía "enero listo", "febrero listo", etc. El detalle de cada resultado (número, fecha, título y enlace) solo se veía para enero, en el paso 4. De febrero a mayo no había forma de revisar qué se había extraído. Nos dimos cuenta al revisar los resultados del notebook: la tabla de verificación decía cuántas normas había por mes, pero no cuáles.

**4. ¿Cómo lo corregimos?**

Agregamos después del recorrido una celda de texto y una de código que muestran la tabla con las 54 normas extraídas (mes, número, fecha, título y enlace). Volvimos a ejecutar todo con Restart y Run All y los resultados salieron iguales. Se unió a main en el PR #13.

## Parte 2 – API de lluvias



## Parte 3 – Cruce y análisis


