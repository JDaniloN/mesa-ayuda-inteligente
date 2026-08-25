# Causas raíz del módulo heredado

El original permanece sin cambios en `materiales/legacy/legacy_module.py`. La
copia corregida está en `src/legacy/legacy_module.py` y sus regresiones en
`tests/legacy/test_legacy_module.py`.

## S1 — El informe mensual pierde tickets

**Causa raíz:** el filtro usaba comparaciones estrictas (`>` y `<`) y excluía
los tickets creados exactamente en las fechas inicial y final de un período
definido como inclusivo.

**Corrección:** comparar con `inicio <= fecha_creacion <= fin`.

**Prueba de regresión:** `test_s1_filtrar_por_periodo_incluye_ambos_extremos`
comprueba los dos extremos y descarta los días anterior y posterior.
`test_s1_informe_mensual_conserva_tickets_del_primero_y_ultimo_dia` verifica
además el síntoma completo en el flujo que reportó el área.

**Alternativa descartada:** representar el período como
`inicio <= fecha < primer_dia_siguiente` también evita errores de límites,
pero cambia el contrato público: esta función recibe una fecha final que el
área de Calidad definió como inclusiva.

## S2 — Los resúmenes siguientes quedan inflados

**Causa raíz:** el diccionario usado como argumento predeterminado se creaba
una sola vez y conservaba los conteos entre llamadas independientes.

**Corrección:** usar `None` como valor predeterminado y crear un diccionario
nuevo en cada llamada que no reciba un acumulador explícito.

**Prueba de regresión:**
`test_s2_resumir_por_area_no_comparte_datos_entre_llamadas` ejecuta dos
resúmenes consecutivos y verifica que no compartan identidad ni resultados.

**Alternativa descartada:** eliminar el parámetro `acumulador` arreglaría las
llamadas independientes, pero rompería a quien lo usa deliberadamente para
acumular. `None` evita el estado compartido y conserva esa compatibilidad,
fijada por `test_s2_resumir_por_area_conserva_un_acumulador_explicito`.

## S3 — El indicador de reaperturas queda por debajo

**Causa raíz:** el indicador comparaba literalmente el estado actual con
`"reabierto"` en vez de consultar el contador que registra el hecho histórico
de haber sido reabierto.

**Corrección:** contar los tickets cuyo valor numérico de `reaperturas` sea
mayor que cero; los valores vacíos o no numéricos no se inventan ni detienen
el informe.

**Prueba de regresión:**
`test_s3_contar_reaperturas_usa_el_hecho_y_no_el_estado_actual` incluye un
ticket ya cerrado después de reabrirse y un estado reabierto sin contador.

**Alternativas descartadas:** normalizar `estado.lower()` solo corregiría
mayúsculas, pero seguiría perdiendo tickets que se cerraron después de una
reapertura. Sumar `reaperturas` respondería cuántos eventos hubo, no cuántos
tickets fueron reabiertos. Un contador vacío tampoco se transforma en `1`
porque podría haber sido `2` o `3`; se conserva como desconocido.

## Comprobación rojo → verde

La misma suite produjo tres fallos con la copia original y pasa después de las
tres correcciones:

```powershell
python -m pytest tests/legacy/test_legacy_module.py -q
```
