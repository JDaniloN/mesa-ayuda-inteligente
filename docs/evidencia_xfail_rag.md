# Evidencia de los tres `xfail` del RAG

Fecha de contraste: 2026-08-25. Objetivo: dejar explícita la inconsistencia
entre «fallan en CI», «pasan al reprobar a mano» y lo que dice la documentación.

## Dónde están

Archivo: `tests/rag/test_consultas_compuestas.py`

| Test | Líneas (aprox.) | Qué exige |
| --- | --- | --- |
| `test_fail_cierre_y_reapertura` | `@pytest.mark.xfail` + cuerpo | citas `POL-TIC-05` §7 **y** §6.1 |
| `test_pass_problema_vs_critico` | `@pytest.mark.xfail` + cuerpo | citas `POL-TIC-05` §6.3 **y** §5.1 |
| `test_multiquery_cierre_cubre_ambas_subconsultas` | `@pytest.mark.xfail` + cuerpo | coverage de ambas subconsultas y hits `direct` con §7 **y** §6.1 |

Hechos en la política (índice real):

- §7 *Cierre*: cierre automático a los 2 días hábiles sin respuesta.
- §6.1 *Reapertura*: reabrir dentro de 5 días hábiles.
- §6.3 *Reapertura*: tres o más reaperturas → problema.
- §5.1: tratamiento de incidente crítico.

Los tres tests usan `EmbeddingsFalsos` (doble léxico hash) e ingestan un
índice temporal; **no** usan el Chroma de `data/salida/rag/` ni OpenAI.

## Entorno A — pytest / CI (embeddings fake)

```text
.\.venv\Scripts\python.exe -m pytest tests/rag/test_consultas_compuestas.py::test_fail_cierre_y_reapertura tests/rag/test_consultas_compuestas.py::test_pass_problema_vs_critico tests/rag/test_consultas_compuestas.py::test_multiquery_cierre_cubre_ambas_subconsultas -v --runxfail --tb=line
```

Resultado reproducible (2026-08-25): **3 failed**.

Sin `--runxfail` salen como **XFAIL** (falla esperada). Si hubieran pasado de
verdad en CI, pytest reportaría **XPASS** (`strict=False`). Aquí **no** hay
XPASS: siguen fallando bajo `EmbeddingsFalsos`.

## Entorno B — índice real (OpenAI + Chroma local)

Misma pregunta y mismos asserts sobre `ServicioPoliticas` / `Retriever` con
`EmbeddingsHttp` y el índice ya ingerido:

| Caso | Resultado real (2026-08-25) | Detalle |
| --- | --- | --- |
| cierre §7 + §6.1 | **FAIL parcial** | recupera §7; **no** entra §6.1 al top de citas/hits |
| crítico §6.3 + §5.1 | **PASS** | ambas secciones en citas |
| multi-query cierre §7 + §6.1 | **FAIL parcial** | `coverage` de ambas subconsultas en `True`, pero hits `direct` traen §7 y **no** §6.1 |

Conclusión: la frase «el índice real ya validado cubre los tres rankings» era
**imprecisa**. Solo el caso *problema vs crítico* se sostiene hoy con el
índice real. Cierre/reapertura sigue incompleto porque §7 y §6.1 no son
hermanos de expansión (`seccion_padre` distinto) y el ranking vectorial no
sube §6.1 en esa pregunta compuesta.

## Qué explica la sensación de «ya pasaron»

- Una respuesta **cualitativa** del generador puede sonar completa (menciona
  plazos de cierre y reapertura) aunque las **citas** no incluyan §6.1.
- El caso *crítico* sí pasa con índice real; es fácil generalizar a «los tres».
- Pytest con `xfail` **no** marca verde esos tres tests: marca XFAIL. Verde
  de la suite = el resto passed + estos xfailed, no que las tres asserts
  hayan dejado de fallar.

## Estado honesto

- **CI:** conservar los tres `xfail`; el fake no reproduce el ranking.
- **Índice real:** residual de calibración en cierre/reapertura (§6.1 ausente
  del top). No afirmar cobertura total hasta que un comando reproducible
  muestre §7 y §6.1 juntos (y, si se desea, quitar el `xfail` solo entonces).
- **No** quitar los `xfail` solo porque «a mano se veía bien»: haría fallar CI
  sin evidencia de XPASS o de assert alineado al índice real.
