# Etapa 5 — Fase 1: plan documental (revisión)

**Propósito.** Definir, ítem por ítem, el paso a paso para resolverlo y cómo
controlar fallos para el **criterio 4** y los criterios propios de Middle II
(IA vs automatización, métricas previas, suite, ML clásico, comparación,
revisión de código, estándar, visión de negocio). **Todavía no se implementa
la suite ni el cuaderno.**

**Flujo acordado (igual que etapa 4)**

1. **Fase 1 (este documento):** plan y control de errores.
2. **Tu revisión:** marcas qué aceptar, ajustar o sacar del alcance.
3. **Fase 2 (después):** retroalimentación → entregables y commits en el
   orden correcto.

**Marco del enunciado (versión 3 días)**

| Obligatorio | Opcional / flexible |
|---|---|
| Documento de decisión (R-01…R-03) | Integrar el ML clásico a la API |
| Métricas previas + gold ≥ 50 en Git **antes** de la suite | Video 5 min (va con la entrega final) |
| Suite de evaluación en CI que falle bajo umbral | Autoevaluación PC-GTH-68 (fuera del repo) |
| Cuaderno ML con línea base y matriz | |
| Comparación LLM vs clásico + recomendación | |
| Revisión de `pr_para_revision.diff` + estándar | |

**Orden crítico en Git (no negociable)**

```
1) docs/metricas_previas.md + data/referencia/conjunto_referencia.csv
2) (después) tests/evaluacion/ + enganche CI
3) notebook + docs de decisión/comparación (pueden ir en paralelo tras 1)
```

Si la suite aparece en el historial **antes** que las métricas, se pierde el
punto de “definición previa”.

---

## Mapa de ítems

| # | Ítem | Entregable previsto | ¿Código / notebook en fase 2? |
|---|---|---|---|
| 1 | Documento de decisión R-01…R-03 | `docs/decision_ia_vs_automatizacion.md` | Solo doc |
| 2 | Métricas previas + gold ≥ 50 | `docs/metricas_previas.md`, `data/referencia/conjunto_referencia.csv` | CSV a mano + commit temprano |
| 3 | Suite de evaluación en CI | `tests/evaluacion/`, job o paso en `.github/workflows/ci.yml` | Sí, **después** del commit de métricas |
| 4 | ML clásico | `notebooks/linea_base_clasificacion.ipynb` | Cuaderno; no integrar a API |
| 5 | Comparación LLM vs clásico | Cierre en el doc de decisión (o `docs/comparacion_enfoques.md`) | Solo doc (+ cifras del notebook) |
| 6 | Revisión PR + estándar | `docs/revision_pr.md`, `docs/estandar_ingenieria_ia.md` | Docs; reutilizar/ampliar el estándar de etapa 3 |

Relación con etapa 3: ya existe `docs/estandar_revision_codigo_ia.md`. En
etapa 5 el estándar debe ser el **referente de equipo** (permisos, revisión
obligatoria, rechazo sin prueba) y citar hallagos del diff defectuoso; no
hace falta inventar otro documento desde cero si se **amplía** con nombre
oficial.

---

## Ítem 1 — Documento de decisión (R-01, R-02, R-03)

### Fuente

`materiales/n5/requerimientos_negocio.md` (no modificar).

### Qué debe quedar

Para **cada** requerimiento:

- Decisión: IA / automatización tradicional / combinación.
- Criterios: volumen, estabilidad, costo, latencia, tolerancia al error,
  mantenimiento.
- Costo estimado (orden de magnitud).
- Riesgo.
- **Condición de cambio** (cuándo revertirías la decisión).

Punto crítico 10: **al menos uno de los tres no se resuelve con IA**. Eso se
sustenta con números, no se esconde.

### Paso a paso

1. Leer R-01, R-02, R-03 y anotar restricciones literales.
2. Armar una matriz 3×6 (requerimiento × criterio) con valores o rangos.
3. Propuesta preliminar (para tu revisión; no es la respuesta “oficial”):

   | Id | Decisión tentativa | Por qué en una línea |
   |---|---|---|
   | R-01 | **Automatización / ML clásico o reglas** (no LLM en línea) | 3.000/día, 12 categorías estables 3 años, lote horario, error barato |
   | R-02 | **IA (RAG) + abstención** | Lenguaje natural, PDFs, error caro → citas + umbral |
   | R-03 | **Automatización tradicional** | Texto fijo, calendario 8:00, idempotencia; la IA no aporta |

4. Escribir costo: p. ej. tokens/día vs cron + SQL; hora-hombre de
   mantenimiento.
5. Escribir riesgo: reclamación formal (R-02), duplicar recordatorios (R-03),
   sesgo de categoría (R-01).
6. Condición de cambio: p. ej. “si las categorías cambian cada mes →
   reevaluar LLM para R-01”; “si aparece teletrabajo en políticas → R-02
   deja de abstenerse en esos casos”.
7. Cerrar con sección “visión de negocio”: qué no automatizarías aunque sea
   tentador.

### Control de errores (criterio 4 + Mid II)

| Fallo anticipado | Control |
|---|---|
| Los tres “con IA” por moda | Forzar que R-03 (o el que elijas) sea sin IA y documentar por qué |
| Decisión sin números | Cada fila con volumen, latencia y costo orden de magnitud |
| Confundir R-01 con el clasificador LLM actual | Separar “lo que ya hay en la demo” vs “lo óptimo a escala 3.000/día” |
| Olvidar condición de cambio | Checklist: las 3 decisiones la tienen |
| Copiar el enunciado sin criterio | Matriz de criterios completa antes de redactar prosa |

### Evidencia de revisión (fase 1)

- [ ] Tabla R-01…R-03 con decisión + condición de cambio
- [ ] Uno explícitamente **sin IA**
- [ ] Costos y riesgos no vacíos

---

## Ítem 2 — Métricas previas y conjunto de referencia (≥ 50)

### Qué debe quedar

1. `docs/metricas_previas.md` con umbrales numéricos **antes** de codear la
   suite.
2. `data/referencia/conjunto_referencia.csv` (≥ 50 filas), partiendo de
   `materiales/n5/plantilla_conjunto_referencia.csv` **sin modificar
   materiales/**.
3. Commit visible en `git log` anterior al de `tests/evaluacion/`.

### Umbrales a fijar (valores tentativos para tu revisión)

| Métrica | Tentativo | Alcance |
|---|---|---|
| Precisión objetivo por categoría | ≥ 0,75 macro / ≥ 0,70 por categoría frecuente | Clasificador (LLM y clásico) |
| Latencia p95 | ≤ 3 000 ms crear solicitud (degradado OK); ≤ 8 000 ms RAG con red | API |
| Tasa máxima de escalamiento / abstención forzada | ≤ 25 % en gold de políticas “con evidencia”; abstención 100 % en casos `SIN EVIDENCIA` | RAG / orquestación |
| Tamaño gold | ≥ 50 | Mix: clasificación, políticas con cita, abstención |

Estos números se pueden endurecer o aflojar en tu revisión; lo importante es
**commitearlos primero**.

### Paso a paso

1. Crear `data/referencia/` y copiar la plantilla a
   `conjunto_referencia.csv`.
2. Conservar GS-001…GS-004; GS-005 completar o reemplazar.
3. Etiquetar a mano hasta ≥ 50:
   - ~20 clasificación (categoría del catálogo / histórico),
   - ~20 políticas con `documento_fuente` + `seccion_fuente`,
   - ≥ 5 abstención (`SIN EVIDENCIA EN LOS DOCUMENTOS`),
   - resto: bordes (hospedaje capital vs no capital, FAQ vs cláusula, etc.).
4. Redactar `docs/metricas_previas.md`: definición de cada métrica, cómo se
   calcula, umbral, exclusión (p. ej. sin red en CI para latencia LLM real).
5. **Commit solo de métricas + CSV** con mensaje claro
   (`docs(eval): fija métricas previas y gold de 50 casos`).
6. Recién después abrir PR/commits de la suite.

### Control de errores

| Fallo anticipado | Control |
|---|---|
| Suite antes que métricas en Git | Commit separado y verificar con `git log -- metricas_previas conjunto_referencia` |
| Gold inventado por el LLM sin leer PDF | Etiquetar a mano; citar sección real o marcar abstención |
| Umbrales inalcanzables en CI sin OpenAI | Distinguir evaluación offline (fakes / clásico) vs online opcional |
| Menos de 50 filas | Contador en el doc + test que falle si `len < 50` |
| Modificar `materiales/n5/` | Prohibido; solo copia en `data/referencia/` |
| Casos solo felices | Cupo mínimo de abstención y de confusiones conocidas |

### Pregunta para tu revisión

¿Los umbrales tentativos de arriba te sirven, o prefieres otros números
antes del primer commit?

---

## Ítem 3 — Suite de evaluación automatizada (CI)

### Qué debe quedar

- `tests/evaluacion/` que lea el gold y los umbrales.
- Reporte de precisión (y lo que se pueda medir offline).
- **Fallo** si cae bajo el umbral.
- Enganche en `.github/workflows/ci.yml` (mismo pipeline o job dedicado).
- Camino de “rojo deliberado” documentado (bajar umbral en un test o input),
  sin romper la rama principal de forma permanente.

### Paso a paso

1. Confirmar que el commit de métricas ya está en la rama.
2. Cargar CSV + umbrales desde archivos versionados (no hardcode mágico
   distinto al doc).
3. Evaluadores mínimos:
   - **Clasificación clásica o degradado/falso:** precisión sobre subset
     GS de categoría (sin red).
   - **Abstención RAG:** casos `SIN EVIDENCIA` deben abstenerse con
     embeddings fake + índice de prueba o regla de etiqueta esperada.
   - **Citas:** si el gold trae documento/sección, el hit debe coincidir
     cuando el score lo permita (aceptar `xfail` documentados solo si el
     fake no alcanza).
4. Latencia p95: medir sobre TestClient en memoria (no OpenAI) o marcar
   métrica “solo smoke” en CI y medición real en doc.
5. Añadir paso CI: `python -m pytest tests/evaluacion/ -q`.
6. Documentar en `docs/metricas_previas.md` cómo reproducir un fallo bajo
   umbral (p. ej. `EVAL_UMBRAL_PRECISION=0.99` en un job manual).

### Control de errores

| Fallo anticipado | Control |
|---|---|
| Suite llama OpenAI en CI | `conftest` + fakes; red prohibida |
| Umbral distinto al doc | Un solo origen (YAML/JSON o parse del markdown) |
| Rojo permanente en main | Rojo deliberado solo por `workflow_dispatch` o test aislado |
| Evaluar 50 casos con Chroma lento | Muestreo o índice tmp; tope de tiempo en job |
| Confundir abstención con error 503 | Asserts explícitos de mensaje fijo / `citas: []` |

### Alternativas a decidir

- A) Suite solo offline (recomendado para CI verde estable).
- B) Job opcional `evaluation-live` con secretos (más fiel, más frágil).

---

## Ítem 4 — Modelo ML clásico (cuaderno)

### Qué debe quedar

`notebooks/linea_base_clasificacion.ipynb` sobre el histórico limpio (o
CSV de `materiales` + limpieza reproducible):

- Partición train/test (estratificada si se puede).
- Línea base (p. ej. TF-IDF + LogisticRegression o similar simple).
- Matriz de confusión.
- Lectura en **términos de negocio** (qué categorías se confunden y qué
  implica para la mesa).

**No** integrar el modelo a `src/api/` en la versión de 3 días.

### Paso a paso

1. Fijar fuente de datos: preferir salida limpia reproducible o script que
   limpie al vuelo desde `materiales/datos/tickets_historicos.csv`.
2. Definir etiqueta: `categoria` del histórico (alineada al catálogo).
3. Partición 80/20, `random_state` fijo.
4. Entrenar línea base; reportar precisión/macro-F1.
5. Matriz de confusión (tabla o heatmap).
6. Celda final: “lectura de negocio” (3–5 viñetas).
7. Guardar el notebook ejecutado o con salidas claras para el evaluador.

### Control de errores

| Fallo anticipado | Control |
|---|---|
| Data leakage (texto con la etiqueta) | Revisar columnas; no usar campos futuros |
| Partición no reproducible | Semilla fija documentada |
| Categorías raras con 0 soporte | Agrupar o reportar soporte mínimo |
| Presentar el clásico como API | README: “cuaderno; no integrado” |
| Entrenar sobre gold de políticas | Gold de etapa 5 ≠ features del histórico; no mezclar |

---

## Ítem 5 — Comparación LLM vs clásico + recomendación

### Qué debe quedar

Tabla explícita (en el doc de decisión o archivo hermano):

| Dimensión | LLM (demo actual) | Clásico (cuaderno) |
|---|---|---|
| Costo por 1.000 solicitudes | $ / tokens | $ compute local ≈ 0 API |
| Latencia | p50/p95 medidos o estimados | Inferencia local |
| Precisión | Sobre gold / muestra | Sobre test del notebook |
| Esfuerzo de mantenimiento | Prompts, umbral, proveedor | Reentrenar al cambiar catálogo |

Recomendación final alineada a R-01…R-03 (p. ej. clásico/lote para
clasificación masiva; LLM+RAG para políticas; cron para recordatorios).

### Paso a paso

1. Tomar supuestos de costo de etapa 4 (o definirlos aquí si etapa 4 aún no
   cerró).
2. Rellenar la tabla con cifras del notebook + métricas previas.
3. Una página de recomendación: cuándo LLM, cuándo clásico, cuándo ninguno.
4. Cruzar con el documento de decisión para que no se contradigan.

### Control de errores

| Fallo anticipado | Control |
|---|---|
| Comparar precisión LLM real con clásico sin mismo set | Declarar sets distintos o evaluar ambos sobre el mismo subset de clasificación |
| Costo sin supuestos | Tabla de supuestos encima de la comparación |
| Recomendar LLM para todo | Debe coherir con R-03 sin IA |
| Ignorar mantenimiento | Incluir “cambio de categorías” y “cambio de PDF” |

---

## Ítem 6 — Revisión de `pr_para_revision.diff` + estándar

### Fuente

`materiales/revision/pr_para_revision.diff` — artefacto **defectuoso a
propósito**. No se modifica ni se “arregla” en `materiales/`.

### Qué debe quedar

1. `docs/revision_pr.md`: hallazgos con archivo/línea (del diff), severidad,
   evidencia, corrección propuesta.
2. `docs/estandar_ingenieria_ia.md` (o ampliación del estándar de etapa 3):
   - qué se **permite** generar con IA,
   - qué se **revisa siempre**,
   - qué **nunca** se acepta sin prueba.

### Paso a paso

1. Leer el diff completo una vez sin IA; anotar olores.
2. Clasificar hallazgos típicos esperables: secretos en código, SQL
   concatenado, límites de fecha, N+1, mezcla de responsabilidades, etc.
3. Redactar revisión como si fuera feedback de PR (accionable).
4. Derivar 5–8 reglas de equipo al estándar.
5. Contrastar con `docs/declaracion_uso_ia.md` y con
   `docs/estandar_revision_codigo_ia.md` (evitar duplicar; unificar).
6. Video 5 min (al cerrar entrega, no en esta fase): qué se construyó, hasta
   qué etapa, dos decisiones, qué harías distinto.

### Control de errores

| Fallo anticipado | Control |
|---|---|
| “Arreglar” el diff en materiales | Solo documentación en `docs/` |
| Hallazgos genéricos sin línea | Cada uno cita hunk/archivo del diff |
| Estándar que nadie puede aplicar | Máximo una página; puerta de commit concreta |
| Aceptar secretos “de demo” | Regla: nunca en Git; `.env.example` sin valores reales |
| Confiar en el modelo para listar bugs | Primera pasada humana; IA solo como segundo lector |

---

## Criterio 4 y Mid II — checklist transversal

Antes de cerrar fase 2 de etapa 5:

1. Decisiones con alternativas y condición de cambio.
2. Métricas **commiteadas antes** que la suite (`git log` demostrable).
3. Suite que puede ponerse **roja** bajo umbral de forma controlada.
4. Notebook con lectura de negocio, no solo accuracy.
5. Comparación con recomendación coherente (IA no siempre gana).
6. Revisión del PR + estándar aplicable en el siguiente cambio.

---

## Recomendación preliminar (para tu revisión)

| Ítem | Propuesta para fase 2 |
|---|---|
| Decisión R-01…R-03 | **Hacer completo** — R-01 clásico/reglas, R-02 RAG, R-03 automatización |
| Métricas + gold 50 | **Primer commit** de la etapa; umbrales tentativos arriba |
| Suite | Offline en CI; rojo deliberado vía input o env |
| Notebook ML | Obligatorio; sin integrar a API |
| Comparación | Cierra el mismo doc de decisión |
| Revisión + estándar | Ampliar estándar etapa 3; revisión escrita del diff |

---

## Preguntas para tu revisión

1. ¿Confirmas R-01 sin LLM a escala, R-02 con RAG, R-03 sin IA?
2. ¿Aceptas los umbrales tentativos o los cambias antes del commit de
   métricas?
3. ¿Suite solo offline en CI, o también job live opcional?
4. ¿El estándar de etapa 5 amplía `estandar_revision_codigo_ia.md` o archivo
   nuevo `estandar_ingenieria_ia.md`?
5. ¿Algún ítem lo sacamos del alcance de esta entrega (además del video /
   PC-GTH-68)?

Cuando respondas, la fase 2 de etapa 5 arranca en el **orden Git** correcto
(métricas → suite → resto).
