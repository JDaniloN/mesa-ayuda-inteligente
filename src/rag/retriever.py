"""Recuperación híbrida, multi-query determinista y expansión de hermanos."""

from __future__ import annotations

from dataclasses import replace
import re
import unicodedata

from src.rag.modelos import Hit, PuertoEmbeddings, ResultadoRecuperacion
from src.rag.vector_store import AlmacenChroma

STOPWORDS = {
    "el",
    "la",
    "los",
    "las",
    "de",
    "del",
    "y",
    "o",
    "a",
    "en",
    "un",
    "una",
    "es",
    "son",
    "ser",
    "sea",
    "por",
    "para",
    "con",
    "se",
    "que",
    "qué",
    "cual",
    "cuál",
    "cuanto",
    "cuánto",
    "cuanta",
    "cuánta",
    "cuantos",
    "cuántos",
    "debo",
    "hace",
    "hacer",
    "hacen",
    "como",
    "cómo",
    "mi",
    "mis",
    "tu",
    "su",
    "sus",
}

MAX_POR_GRUPO = 2
MARGEN_DIVERSIDAD = 0.15
MAX_CONTEXTO = 8
BOOST_TITULO = 0.08
CONECTORES = (
    " frente a ",
    " en comparación con ",
    " mientras que ",
)
INICIO_INTERROGATIVO = re.compile(
    r"^(qué|que|cuál|cual|cuánto|cuanto|cuánta|cuanta|quién|quien|"
    r"cómo|como|dónde|donde|cuándo|cuando|en qué|en que|con cuánt|"
    r"con cuant)",
    re.IGNORECASE,
)


class Retriever:
    def __init__(self, almacen: AlmacenChroma, embeddings: PuertoEmbeddings) -> None:
        self._almacen = almacen
        self._embeddings = embeddings

    def buscar(self, pregunta: str, limite: int, vector: list[float] | None = None) -> list[Hit]:
        return self.recuperar(pregunta, limite, vector=vector).hits

    def recuperar(
        self,
        pregunta: str,
        limite: int,
        vector: list[float] | None = None,
    ) -> ResultadoRecuperacion:
        partes = descomponer_pregunta(pregunta)
        etiquetas = list(partes)
        vectores = _vectores_consulta(self._embeddings, partes, vector)
        ranked: list[list[Hit]] = []
        for etiqueta, vec in zip(etiquetas, vectores):
            ranked.append(self._rankear(partes[etiqueta], vec, etiqueta))
        fusionados = _merge_por_id(ranked)
        fusionados.sort(key=lambda item: item.score, reverse=True)
        directos = _diversificar(fusionados, limite, etiquetas=etiquetas)
        coverage = {
            etiqueta: any(etiqueta in hit.source_queries for hit in directos)
            for etiqueta in etiquetas
            if etiqueta != "original" or len(etiquetas) == 1
        }
        tope = min(limite + 4, MAX_CONTEXTO)
        hits = _expandir(directos, self._almacen.listar(), tope)
        return ResultadoRecuperacion(
            hits=hits,
            coverage=coverage,
            subconsultas=partes,
        )

    def _rankear(self, pregunta: str, vector: list[float], etiqueta: str) -> list[Hit]:
        pool = max(self._almacen.cantidad(), 1)
        hits = self._almacen.consultar(vector, pool)
        fusionados = []
        for hit in hits:
            lexical = _score_lexical(pregunta, hit.texto, hit.metadata)
            final = min(1.0, 0.4 * hit.score + 0.6 * lexical)
            fusionados.append(
                Hit(
                    texto=hit.texto,
                    score=final,
                    metadata=hit.metadata,
                    vector_score=hit.vector_score or hit.score,
                    lexical_score=lexical,
                    source_queries=(etiqueta,),
                    retrieval_type="direct",
                )
            )
        fusionados.sort(key=lambda item: item.score, reverse=True)
        return fusionados


def _vectores_consulta(embeddings, partes: dict[str, str], vector: list[float] | None) -> list[list[float]]:
    etiquetas = list(partes)
    if vector is None:
        return embeddings.embed([partes[clave] for clave in etiquetas])
    otras = [clave for clave in etiquetas if clave != "original"]
    extras = embeddings.embed([partes[clave] for clave in otras]) if otras else []
    indice = 0
    vectores = []
    for clave in etiquetas:
        if clave == "original":
            vectores.append(vector)
        else:
            vectores.append(extras[indice])
            indice += 1
    return vectores


def descomponer_pregunta(pregunta: str) -> dict[str, str]:
    original = (pregunta or "").strip()
    if not original:
        return {"original": original}
    partes = _partir(original)
    if len(partes) < 2:
        return {"original": original}
    return {
        "original": original,
        "subquery_1": partes[0],
        "subquery_2": partes[1],
    }


def _partir(pregunta: str) -> list[str]:
    normal = f" {_normalizar(pregunta)} "
    if "por un lado" in normal and "por otro" in normal:
        cortada = re.split(r"por un lado|por otro(?: lado)?", pregunta, flags=re.IGNORECASE)
        limpias = [parte.strip(" ,;.") for parte in cortada if parte.strip(" ,;.")]
        if len(limpias) >= 2:
            return [_con_preambulo(pregunta, limpias[0]), _con_preambulo(pregunta, limpias[1])]
    for conector in CONECTORES:
        hallado = re.search(re.escape(conector.strip()), pregunta, flags=re.IGNORECASE)
        if not hallado:
            continue
        izquierda = pregunta[: hallado.start()].strip(" ,;")
        derecha = pregunta[hallado.end() :].strip(" ,;")
        if izquierda and derecha:
            return [_con_preambulo(pregunta, izquierda), _con_preambulo(pregunta, derecha)]
    return _partir_por_y(pregunta)


def _partir_por_y(pregunta: str) -> list[str]:
    cuerpo_idx = pregunta.find("¿")
    if cuerpo_idx >= 0:
        preambulo = pregunta[:cuerpo_idx]
        cuerpo = pregunta[cuerpo_idx + 1 :]
    else:
        preambulo = ""
        cuerpo = pregunta
    cuerpo = cuerpo.rstrip("?").strip()
    patron = re.compile(r",?\s+y\s+", re.IGNORECASE)
    for match in patron.finditer(cuerpo):
        derecha = cuerpo[match.end() :].strip()
        if not INICIO_INTERROGATIVO.match(_normalizar(derecha)):
            continue
        izquierda = cuerpo[: match.start()].strip(" ,;")
        if not izquierda or not derecha:
            continue
        una = f"{preambulo}¿{izquierda}?".strip()
        dos = f"{preambulo}¿{derecha}?".strip()
        if not dos.endswith("?"):
            dos = dos + "?"
        return [una, dos]
    return []


def _con_preambulo(pregunta: str, fragmento: str) -> str:
    texto = fragmento.strip()
    if "¿" in pregunta and "¿" not in texto:
        preambulo = pregunta.split("¿", 1)[0]
        return f"{preambulo}¿{texto.rstrip('?')}?"
    if not texto.endswith("?"):
        return texto + ("?" if "¿" in texto else "")
    return texto


def _grupo(hit: Hit) -> tuple[str, str]:
    codigo = str(hit.metadata.get("codigo") or "")
    padre = str(hit.metadata.get("seccion_padre") or "")
    seccion = str(hit.metadata.get("seccion") or "")
    return (codigo, padre or seccion)


def _merge_por_id(listas: list[list[Hit]]) -> list[Hit]:
    por_id: dict[str, Hit] = {}
    for lista in listas:
        for hit in lista:
            chunk_id = str(hit.metadata.get("chunk_id") or "")
            if not chunk_id:
                continue
            previo = por_id.get(chunk_id)
            if previo is None:
                por_id[chunk_id] = hit
                continue
            consultas = tuple(dict.fromkeys([*previo.source_queries, *hit.source_queries]))
            ganador = hit if hit.score > previo.score else previo
            por_id[chunk_id] = replace(ganador, source_queries=consultas)
    return list(por_id.values())


def _diversificar(
    ranked: list[Hit],
    limite: int,
    etiquetas: list[str] | None = None,
) -> list[Hit]:
    if not ranked or limite <= 0:
        return []
    elegidos: list[Hit] = []
    ids: set[str] = set()

    def _agregar(hit: Hit) -> None:
        chunk_id = str(hit.metadata.get("chunk_id") or "")
        if not chunk_id or chunk_id in ids or len(elegidos) >= limite:
            return
        elegidos.append(hit)
        ids.add(chunk_id)

    _agregar(ranked[0])
    for etiqueta in etiquetas or []:
        if etiqueta == "original":
            continue
        mejor = next(
            (
                hit
                for hit in ranked
                if etiqueta in hit.source_queries
                and str(hit.metadata.get("chunk_id") or "") not in ids
            ),
            None,
        )
        if mejor is not None:
            _agregar(mejor)
    omitidos: list[Hit] = []
    for candidato in ranked:
        if len(elegidos) >= limite:
            break
        if str(candidato.metadata.get("chunk_id") or "") in ids:
            continue
        grupo = _grupo(candidato)
        n_grupo = sum(1 for item in elegidos if _grupo(item) == grupo)
        if n_grupo < MAX_POR_GRUPO:
            _agregar(candidato)
            continue
        alternativa = next(
            (
                item
                for item in ranked
                if str(item.metadata.get("chunk_id") or "") not in ids
                and item is not candidato
                and _grupo(item) != grupo
            ),
            None,
        )
        if alternativa is None or candidato.score >= alternativa.score + MARGEN_DIVERSIDAD:
            _agregar(candidato)
        else:
            omitidos.append(candidato)
    if len(elegidos) < limite:
        for candidato in omitidos + ranked:
            _agregar(candidato)
            if len(elegidos) >= limite:
                break
    return elegidos[:limite]


def _menor(seccion: str) -> int | None:
    partes = str(seccion).split(".")
    if len(partes) != 2:
        return None
    try:
        return int(partes[1])
    except ValueError:
        return None


def _expandir(directos: list[Hit], inventario: list[Hit], tope: int) -> list[Hit]:
    resultado = list(directos)
    vistos = {str(hit.metadata.get("chunk_id") or "") for hit in resultado}
    indice = {
        (
            str(item.metadata.get("codigo") or ""),
            str(item.metadata.get("seccion") or ""),
        ): item
        for item in inventario
    }
    for hit in directos:
        padre = str(hit.metadata.get("seccion_padre") or "")
        seccion = str(hit.metadata.get("seccion") or "")
        codigo = str(hit.metadata.get("codigo") or "")
        menor = _menor(seccion)
        if not padre or menor is None:
            continue
        for delta in (-1, 1):
            vecino = indice.get((codigo, f"{padre}.{menor + delta}"))
            if vecino is None:
                continue
            chunk_id = str(vecino.metadata.get("chunk_id") or "")
            if not chunk_id or chunk_id in vistos:
                continue
            resultado.append(
                replace(
                    vecino,
                    retrieval_type="expansion",
                    source_queries=(),
                    score=0.0,
                    vector_score=0.0,
                    lexical_score=0.0,
                )
            )
            vistos.add(chunk_id)
            if len(resultado) >= tope:
                return resultado
    return resultado


def _score_lexical(pregunta: str, texto: str, metadata: dict) -> float:
    q = _tokens(pregunta)
    cuerpo = texto + " " + " ".join(
        str(valor)
        for clave, valor in metadata.items()
        if clave != "titulo_seccion"
    )
    d = _tokens(cuerpo)
    if not q:
        return 0.0
    matched = sum(1 for token in q if _cubre(token, d))
    solapamiento = matched / len(q)
    extra = 0.0
    codigo = str(metadata.get("codigo") or "")
    seccion = str(metadata.get("seccion") or "")
    if codigo and codigo.lower() in pregunta.lower():
        extra += 0.15
    if seccion and seccion in pregunta:
        extra += 0.1
    pregunta_norm = _normalizar(pregunta)
    texto_norm = _normalizar(cuerpo)
    palabras = [token for token in pregunta_norm.split() if token not in STOPWORDS]
    for indice in range(len(palabras) - 1):
        bigrama = f"{palabras[indice]} {palabras[indice + 1]}"
        if bigrama in texto_norm:
            extra += 0.25
    titulo = _normalizar(str(metadata.get("titulo_seccion") or ""))
    tokens_titulo = _tokens(titulo)
    if tokens_titulo and any(
        _cubre(token, tokens_titulo) and not _cubre(token, d) for token in q
    ):
        extra += BOOST_TITULO
    score = min(1.0, solapamiento + extra)
    if matched < 2:
        score *= 0.35
    return score


def _cubre(token: str, vocabulario: set[str]) -> bool:
    if token in vocabulario:
        return True
    raiz = token[:5] if len(token) >= 5 else token
    for candidato in vocabulario:
        if len(candidato) >= 5 and (
            candidato.startswith(raiz) or token.startswith(candidato[:5])
        ):
            return True
        if len(token) >= 5 and len(candidato) >= 5 and (
            token in candidato or candidato in token
        ):
            return True
    return False


def _normalizar(texto: str) -> str:
    return unicodedata.normalize("NFC", (texto or "").lower())


def _tokens(texto: str) -> set[str]:
    nfc = _normalizar(texto)
    return {
        token
        for token in re.findall(r"[a-záéíóúñü0-9%]+", nfc)
        if len(token) > 2 and token not in STOPWORDS
    }
