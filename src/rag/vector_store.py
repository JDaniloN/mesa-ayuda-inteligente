"""Chroma local persistente con metadata de compatibilidad."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import chromadb
from chromadb.config import Settings

from src.rag.modelos import ErrorRag, Fragmento, Hit

COLECCION = "politicas"


class AlmacenChroma:
    def __init__(self, directorio: Path) -> None:
        self.directorio = Path(directorio)
        self.directorio.mkdir(parents=True, exist_ok=True)
        self._chroma_dir = self.directorio / "chroma"
        self._sidecar = self.directorio / "indice.json"
        self._cliente = chromadb.PersistentClient(
            path=str(self._chroma_dir),
            settings=Settings(anonymized_telemetry=False),
        )

    def metadata(self) -> dict:
        if not self._sidecar.exists():
            return {}
        return json.loads(self._sidecar.read_text(encoding="utf-8"))

    def existe(self) -> bool:
        return self._sidecar.exists() and bool(self.ids())

    def ids(self) -> list[str]:
        try:
            coleccion = self._cliente.get_collection(COLECCION)
        except Exception:
            return []
        return list(coleccion.get().get("ids") or [])

    def verificar_compatibilidad(self, modelo: str, dimensiones: int) -> None:
        meta = self.metadata()
        if not meta:
            raise ErrorRag(
                "sin_indice",
                "No hay índice RAG. Ejecute python -m src.rag.",
            )
        if meta.get("embedding_model") != modelo:
            raise ErrorRag(
                "indice_incompatible",
                "El índice RAG se construyó con otro modelo de embeddings.",
            )
        if int(meta.get("embedding_dimensions") or 0) != int(dimensiones):
            raise ErrorRag(
                "indice_incompatible",
                "El índice RAG tiene otra dimensión de embeddings.",
            )

    def ingestar(
        self,
        fragmentos: list[Fragmento],
        vectores: list[list[float]],
        *,
        modelo: str,
        documents_hash: str,
    ) -> None:
        if len(fragmentos) != len(vectores):
            raise ErrorRag("configuracion", "Fragmentos y vectores no coinciden.")
        if not vectores:
            raise ErrorRag("configuracion", "La ingesta no produjo embeddings.")
        dimensiones = len(vectores[0])
        previa = self.metadata()
        mismo_indice = (
            previa.get("documents_hash") == documents_hash
            and previa.get("embedding_model") == modelo
            and int(previa.get("embedding_dimensions") or 0) == dimensiones
        )
        if self._tiene_coleccion() and not mismo_indice:
            self._cliente.delete_collection(COLECCION)
        coleccion = self._cliente.get_or_create_collection(
            name=COLECCION,
            metadata={"hnsw:space": "cosine"},
        )
        ids = [fragmento.chunk_id for fragmento in fragmentos]
        metadatos = [_meta(fragmento) for fragmento in fragmentos]
        textos = [fragmento.texto for fragmento in fragmentos]
        coleccion.upsert(
            ids=ids,
            embeddings=vectores,
            documents=textos,
            metadatas=metadatos,
        )
        self._sidecar.write_text(
            json.dumps(
                {
                    "embedding_model": modelo,
                    "embedding_dimensions": dimensiones,
                    "documents_hash": documents_hash,
                    "created_at": datetime.now(timezone.utc).isoformat(),
                    "fragmentos": len(fragmentos),
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

    def cantidad(self) -> int:
        try:
            return int(self._cliente.get_collection(COLECCION).count())
        except Exception:
            return 0

    def consultar(
        self,
        vector: list[float],
        limite: int,
    ) -> list[Hit]:
        coleccion = self._cliente.get_or_create_collection(
            name=COLECCION,
            metadata={"hnsw:space": "cosine"},
        )
        if coleccion.count() == 0:
            return []
        n = max(1, min(limite, coleccion.count()))
        bruto = coleccion.query(
            query_embeddings=[vector],
            n_results=n,
            include=["documents", "metadatas", "distances"],
        )
        hits = []
        documentos = (bruto.get("documents") or [[]])[0]
        metas = (bruto.get("metadatas") or [[]])[0]
        distancias = (bruto.get("distances") or [[]])[0]
        for texto, meta, distancia in zip(documentos, metas, distancias):
            similitud = max(0.0, min(1.0, 1.0 - float(distancia)))
            hits.append(
                Hit(
                    texto=texto or "",
                    score=similitud,
                    metadata=dict(meta or {}),
                    vector_score=similitud,
                )
            )
        return hits

    def listar(self) -> list[Hit]:
        try:
            coleccion = self._cliente.get_collection(COLECCION)
        except Exception:
            return []
        bruto = coleccion.get(include=["documents", "metadatas"])
        filas = []
        for chunk_id, texto, meta in zip(
            bruto.get("ids") or [],
            bruto.get("documents") or [],
            bruto.get("metadatas") or [],
        ):
            datos = dict(meta or {})
            datos.setdefault("chunk_id", chunk_id)
            filas.append(
                Hit(
                    texto=texto or "",
                    score=0.0,
                    metadata=datos,
                )
            )
        return filas

    def _tiene_coleccion(self) -> bool:
        try:
            self._cliente.get_collection(COLECCION)
            return True
        except Exception:
            return False


def _meta(fragmento: Fragmento) -> dict:
    return {
        "chunk_id": fragmento.chunk_id,
        "codigo": fragmento.codigo,
        "titulo_documento": fragmento.titulo_documento,
        "version": fragmento.version,
        "seccion": fragmento.seccion,
        "seccion_padre": fragmento.seccion_padre,
        "titulo_seccion": fragmento.titulo_seccion,
        "pagina_inicio": fragmento.pagina_inicio,
        "pagina_fin": fragmento.pagina_fin,
    }
