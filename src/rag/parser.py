"""Parser estructural: secciones, cláusulas, tablas semánticas y disclaimer."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.rag.extractor import DocumentoExtraido, PaginaExtraida

DISCLAIMER = re.compile(
    r"Documento sintético elaborado exclusivamente.*",
    re.IGNORECASE | re.DOTALL,
)
MARCA_PAGINA = re.compile(r"^--\s*\d+\s+of\s+\d+\s*--$", re.IGNORECASE)
CID = re.compile(r"\(cid:\d+\)")
SECCION = re.compile(r"^(\d+)\.\s+(\S.{0,80})$")
CLAUSULA = re.compile(r"^(?:[•\-]\s*)?(\d+)\.(\d+)\.\s+(.+)$")


@dataclass
class Bloque:
    seccion: str
    seccion_padre: str
    titulo_seccion: str
    pagina_inicio: int
    pagina_fin: int
    lineas: list[str] = field(default_factory=list)

    @property
    def texto(self) -> str:
        return "\n".join(linea for linea in self.lineas if linea.strip()).strip()


def parsear_documento(documento: DocumentoExtraido) -> list[Bloque]:
    bloques: list[Bloque] = []
    actual: Bloque | None = None
    titulos: dict[str, str] = {}

    for pagina in documento.paginas:
        celdas = _celdas(pagina)
        tablas_semanticas = [tabla_semantica(tabla) for tabla in pagina.tablas]
        insertadas: set[int] = set()
        texto = DISCLAIMER.sub("", pagina.texto or "")
        for cruda in texto.splitlines():
            linea = CID.sub("", cruda).replace("•", " ").strip()
            linea = re.sub(r"\s+", " ", linea)
            if not linea or MARCA_PAGINA.match(linea):
                continue
            if _es_cabecera_documento(linea, documento):
                continue
            if _es_linea_de_tabla(linea, celdas):
                if actual is not None:
                    for indice, semantica in enumerate(tablas_semanticas):
                        if indice in insertadas or not semantica:
                            continue
                        if _tabla_coincide_linea(linea, pagina.tablas[indice]):
                            actual.lineas.append(semantica)
                            actual.pagina_fin = pagina.numero
                            insertadas.add(indice)
                            break
                continue
            seccion_titulada = SECCION.match(linea)
            clausula = CLAUSULA.match(linea)
            if seccion_titulada and not clausula:
                numero, titulo = seccion_titulada.groups()
                titulos[numero] = titulo.strip()
                actual = Bloque(
                    seccion=numero,
                    seccion_padre="",
                    titulo_seccion=titulo.strip(),
                    pagina_inicio=pagina.numero,
                    pagina_fin=pagina.numero,
                )
                bloques.append(actual)
                continue
            if clausula:
                mayor, menor, resto = clausula.groups()
                seccion = f"{mayor}.{menor}"
                titulo_propio = _titulo_subseccion(resto)
                actual = Bloque(
                    seccion=seccion,
                    seccion_padre=mayor,
                    titulo_seccion=titulo_propio or titulos.get(mayor, ""),
                    pagina_inicio=pagina.numero,
                    pagina_fin=pagina.numero,
                    lineas=[resto.strip()],
                )
                bloques.append(actual)
                continue
            if actual is None:
                continue
            actual.pagina_fin = pagina.numero
            actual.lineas.append(linea)

        if actual is not None:
            for indice, semantica in enumerate(tablas_semanticas):
                if indice not in insertadas and semantica:
                    actual.lineas.append(semantica)

    return [bloque for bloque in bloques if bloque.texto]


def tabla_semantica(tabla: list[list[str]]) -> str:
    if not tabla:
        return ""
    encabezados = [celda.strip() for celda in tabla[0]]
    lineas = []
    for fila in tabla[1:]:
        celdas = [celda.strip() for celda in fila]
        if not any(celdas):
            continue
        clave = celdas[0] or "Fila"
        pares = []
        for indice, valor in enumerate(celdas[1:], start=1):
            if not valor:
                continue
            etiqueta = (
                encabezados[indice]
                if indice < len(encabezados)
                else f"columna {indice + 1}"
            )
            pares.append(f"- {etiqueta}: {valor}")
        if pares:
            prefijo = f"{encabezados[0]} " if encabezados and encabezados[0] else ""
            lineas.append(f"{prefijo}{clave}:".strip())
            lineas.extend(pares)
        else:
            lineas.append(clave)
    return "\n".join(lineas)


def _celdas(pagina: PaginaExtraida) -> set[str]:
    return {
        _normalizar_celda(celda)
        for tabla in pagina.tablas
        for fila in tabla
        for celda in fila
        if _normalizar_celda(celda)
    }


def _tabla_coincide_linea(linea: str, tabla: list[list[str]]) -> bool:
    normal = _normalizar_celda(linea)
    encabezados = [_normalizar_celda(celda) for celda in tabla[0] if celda.strip()]
    if encabezados:
        cubiertos = sum(1 for celda in encabezados if celda in normal)
        if cubiertos >= min(2, len(encabezados)):
            return True
    for fila in tabla[1:]:
        celdas = [_normalizar_celda(celda) for celda in fila if celda.strip()]
        if len(celdas) >= 2 and celdas[0] in normal and any(celda in normal for celda in celdas[1:]):
            return True
    return False


def _es_linea_de_tabla(linea: str, celdas: set[str]) -> bool:
    if not celdas:
        return False
    normal = _normalizar_celda(linea)
    if not normal:
        return False
    coincidencias = [celda for celda in celdas if len(celda) > 2 and celda in normal]
    if len(coincidencias) >= 2:
        return True
    tokens = [token for token in re.split(r"\s+", linea.strip()) if len(token) > 2]
    if len(tokens) < 2:
        return False
    cubiertos = sum(1 for token in tokens if _normalizar_celda(token) in celdas)
    return cubiertos >= max(2, int(0.6 * len(tokens)))


def _normalizar_celda(valor: str) -> str:
    return re.sub(r"\s+", " ", (valor or "").strip()).lower()


def _es_cabecera_documento(linea: str, documento: DocumentoExtraido) -> bool:
    if linea == documento.titulo:
        return True
    if documento.codigo and documento.codigo in linea and "LA FORTUNA" in linea.upper():
        return True
    return linea.upper().startswith("LA FORTUNA")


def _titulo_subseccion(resto: str) -> str:
    candidato = resto.strip()
    if len(candidato) > 60 or candidato.endswith("."):
        return ""
    if candidato[:1].islower():
        return ""
    if re.match(r"^(La|El|Los|Las|Un|Una|Todo|Toda|Si)\b", candidato):
        return ""
    return candidato
