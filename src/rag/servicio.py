"""Ingesta y consulta de políticas. La ruta HTTP solo delega aquí."""

from __future__ import annotations

from pathlib import Path

from src.configuracion import Configuracion, obtener_configuracion
from src.metricas import RegistroMetricas
from src.rag.chunker import fragmentar_documento
from src.rag.embeddings import EmbeddingsHttp
from src.rag.extractor import extraer_directorio, hash_documentos
from src.rag.generador import GeneradorHttp
from src.rag.modelos import (
    MENSAJE_ABSTENCION,
    ErrorRag,
    Fragmento,
    PuertoEmbeddings,
    PuertoGenerador,
    ResultadoConsulta,
)
from src.rag.retriever import Retriever
from src.rag.vector_store import AlmacenChroma

POLITICAS = Path(__file__).resolve().parents[2] / "materiales" / "politicas"


class ServicioPoliticas:
    def __init__(
        self,
        almacen: AlmacenChroma,
        embeddings: PuertoEmbeddings | None,
        generador: PuertoGenerador | None,
        min_score: float,
    ) -> None:
        self._almacen = almacen
        self._embeddings = embeddings
        self._generador = generador
        self._min_score = min_score

    @classmethod
    def desde_configuracion(
        cls,
        configuracion: Configuracion | None = None,
        *,
        embeddings: PuertoEmbeddings | None = None,
        generador: PuertoGenerador | None = None,
        almacen: AlmacenChroma | None = None,
        metricas: RegistroMetricas | None = None,
    ) -> ServicioPoliticas:
        config = configuracion or obtener_configuracion()
        store = almacen or AlmacenChroma(Path(config.rag_indice_dir))
        if embeddings is None:
            clave = config.ia_api_key.get_secret_value().strip()
            url = config.ia_api_base_url.strip()
            if clave and url:
                embeddings = EmbeddingsHttp(
                    url,
                    clave,
                    config.ia_embedding_model,
                    timeout_s=config.ia_timeout,
                    metricas=metricas,
                )
        if generador is None:
            clave = config.ia_api_key.get_secret_value().strip()
            url = config.ia_api_base_url.strip()
            if clave and url:
                generador = GeneradorHttp(
                    url,
                    clave,
                    config.ia_model,
                    timeout_s=config.ia_timeout,
                    metricas=metricas,
                )
        return cls(store, embeddings, generador, config.rag_min_score)

    def close(self) -> None:
        if self._embeddings is not None:
            self._embeddings.close()
        if self._generador is not None:
            self._generador.close()

    def ingestar(self, directorio: Path | None = None) -> dict:
        embeddings = self._exigir_embeddings()
        origen = directorio or POLITICAS
        documentos = extraer_directorio(origen)
        fragmentos: list[Fragmento] = []
        for documento in documentos:
            fragmentos.extend(fragmentar_documento(documento))
        vectores = embeddings.embed([item.texto for item in fragmentos])
        self._almacen.ingestar(
            fragmentos,
            vectores,
            modelo=embeddings.modelo,
            documents_hash=hash_documentos([item.ruta for item in documentos]),
        )
        return {
            "documentos": len(documentos),
            "fragmentos": len(fragmentos),
            "modelo": embeddings.modelo,
        }

    def consultar_politica(self, pregunta: str, limite: int = 4) -> ResultadoConsulta:
        embeddings = self._exigir_embeddings()
        if not self._almacen.existe():
            raise ErrorRag(
                "sin_indice",
                "No hay índice RAG. Ejecute python -m src.rag.",
            )
        probe = embeddings.embed([pregunta])[0]
        self._almacen.verificar_compatibilidad(embeddings.modelo, len(probe))
        recuperado = Retriever(self._almacen, embeddings).recuperar(
            pregunta, limite, vector=probe
        )
        hits = recuperado.hits
        directos = [hit for hit in hits if hit.retrieval_type == "direct"]
        if not directos or directos[0].score < self._min_score:
            return ResultadoConsulta(
                respuesta=MENSAJE_ABSTENCION,
                citas=[],
                abstuvo=True,
                hits=hits,
                coverage=recuperado.coverage,
            )
        if self._generador is None:
            raise ErrorRag(
                "configuracion",
                "Falta el generador de IA. Configure IA_API_KEY.",
            )
        contextos = [hit.texto for hit in hits]
        respuesta = self._generador.generar(
            pregunta, contextos, cobertura=recuperado.coverage
        )
        return ResultadoConsulta(
            respuesta=respuesta,
            citas=[_cita(hit) for hit in hits],
            abstuvo=False,
            hits=hits,
            coverage=recuperado.coverage,
        )

    def _exigir_embeddings(self) -> PuertoEmbeddings:
        if self._embeddings is None:
            raise ErrorRag(
                "configuracion",
                "Falta IA_API_KEY o IA_API_BASE_URL para embeddings. No se fabrican vectores.",
            )
        return self._embeddings


def _cita(hit) -> dict:
    meta = hit.metadata
    pagina_inicio = int(meta.get("pagina_inicio") or 1)
    pagina_fin = int(meta.get("pagina_fin") or pagina_inicio)
    return {
        "documento": meta.get("codigo") or "",
        "seccion": meta.get("seccion") or "",
        "titulo": meta.get("titulo_seccion") or "",
        "pagina": pagina_inicio,
        "pagina_inicio": pagina_inicio,
        "pagina_fin": pagina_fin,
        "fragmento_id": meta.get("chunk_id") or "",
    }
