# Evidencia: calibración RAG (ex-`xfail`)

Fecha: 2026-08-25. Los tres rankings que estaban en `xfail` pasan en CI fake
y con el índice real.

## Dónde estaban

`tests/rag/test_consultas_compuestas.py`:

| Test | Asserts |
| --- | --- |
| `test_fail_cierre_y_reapertura` | `POL-TIC-05` §7 y §6.1 |
| `test_pass_problema_vs_critico` | `POL-TIC-05` §6.3 y §5.1 |
| `test_multiquery_cierre_cubre_ambas_subconsultas` | coverage + hits `direct` §7 y §6.1 |

## Qué fallaba (antes)

1. **Preámbulo en subconsulta 2:** al partir por «y», la segunda rama heredaba
   «Si un ticket se reabre…» / «Tras solucionarse…» y contaminaba el ranking
   (p. ej. crítico perdía §5.1; reapertura perdía frente a Objeto/Indicadores).
2. **Diversificación tras merge:** casi todos los tops quedaban etiquetados con
   todas las subconsultas; no se anclaba un hit propio por subconsulta.
3. **Léxico:** «cerrarlo»↔«cierre» y «reabrirlo»↔«reapertura» no cruzaban por
   prefijo; §8 *Indicadores* («tasa de reapertura») robaba el puesto a §6.1.
4. **Expansión:** §7 (*Cierre*) y §6.1 (*Reapertura*) no son hermanos
   (`seccion_padre` distinto).

## Qué se calibró (`src/rag/retriever.py`)

- Subconsulta 2 sin preámbulo condicional.
- Ancla por lista propia de cada subconsulta (con preferencia de título).
- Familias léxicas + boost de familia **solo en título**.
- Boost de plazo (`tiempo`/`días`/`hábiles`).
- Expansión complementaria Cierre ↔ Reapertura en el mismo documento.

## Evidencia reproducible

```text
.\.venv\Scripts\python.exe -m pytest tests/rag/test_consultas_compuestas.py::test_fail_cierre_y_reapertura tests/rag/test_consultas_compuestas.py::test_pass_problema_vs_critico tests/rag/test_consultas_compuestas.py::test_multiquery_cierre_cubre_ambas_subconsultas -q
```

Resultado: **3 passed**.

Índice real (OpenAI + Chroma local), mismos asserts: §7+§6.1, §6.3+§5.1 y
multi-query `direct` §7+§6.1 en **True**. Respuesta demo de cierre: 2 días
hábiles de cierre automático y 5 días hábiles para reabrir.
