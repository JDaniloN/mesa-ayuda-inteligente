# Evidencia del pipeline de integración continua

Workflow: `.github/workflows/ci.yml`  
Disparadores: cada `push`, cada `pull_request` y ejecución manual.

## Camino exitoso

Ejecución local de los mismos pasos del job `calidad`, 2026-08-25:

```text
> ruff check --select E9,F63,F7,F82 src tests
All checks passed!

> python -m pytest -q
196 passed, 3 xfailed, 1 warning in 61.34s
Exit code: 0
```

Los tres `xfail` están en `tests/rag/test_consultas_compuestas.py`. Con
`EmbeddingsFalsos` siguen fallando (XFAIL, no XPASS). El contraste con el
índice real y los asserts exactos está en `docs/evidencia_xfail_rag.md`: solo
*problema vs crítico* pasa hoy con OpenAI; cierre/reapertura aún no ancla
§6.1. No llaman a OpenAI en CI y no ocultan una excepción de producción.

## Camino fallido controlado

El `workflow_dispatch` ofrece el booleano `demostrar_fallo`. Después de que
Ruff y pytest pasan, el último paso termina de forma deliberada:

```text
> python -c "raise SystemExit('Fallo controlado solicitado para demostrar CI rojo')"
Fallo controlado solicitado para demostrar CI rojo
Exit code: 1
```

Esto permite mostrar un job rojo sin introducir código inválido ni romper las
pruebas. En GitHub Actions:

1. Abrir **Actions → CI → Run workflow**.
2. Desmarcar `demostrar_fallo` para la ejecución verde.
3. Marcarlo para la ejecución roja.

## Ejecuciones remotas

- Exitosa (CI #4, `demostrar_fallo` desmarcado):
  https://github.com/JDaniloN/mesa-ayuda-inteligente/actions/runs/32885632111
- Fallida controlada (CI #5, `demostrar_fallo` marcado):
  https://github.com/JDaniloN/mesa-ayuda-inteligente/actions/runs/32885796312

Ambas se dispararon con `workflow_dispatch` sobre `main` (`835fa75`). La verde
terminó en Success; la roja en Failure por el paso deliberado de evidencia,
no por un test productivo roto.

## Por qué este diseño

- Ruff solo con `E9,F63,F7,F82`: evita fallar el pipeline por estilo heredado.
- Un runner Ubuntu: Chroma y pdfplumber son más estables ahí que en matrix.
- Tres `xfail` documentados: ver `docs/evidencia_xfail_rag.md` (fake vs real).
- Camino rojo con `demostrar_fallo`: no se rompe un test productivo para la
  evidencia.

Descartado: cobertura obligatoria, fail-fast sobre `xfail`, y fingir URLs
remotas con salidas locales.
