"""Guardas básicas contra secretos en el código desarrollado."""

from pathlib import Path
import re
import subprocess

RAIZ = Path(__file__).resolve().parents[2]
PATRONES_SECRETOS = (
    re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)


def test_env_esta_ignorado():
    ignorados = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".env" in {linea.strip() for linea in ignorados}


def test_env_no_esta_rastreado_por_git():
    resultado = subprocess.run(
        ["git", "ls-files", "--error-unmatch", ".env"],
        cwd=RAIZ,
        capture_output=True,
        text=True,
        check=False,
    )

    assert resultado.returncode != 0


def test_codigo_documentacion_y_pruebas_no_contienen_secretos_conocidos():
    archivos = [RAIZ / "README.md", RAIZ / ".env.example"]
    for carpeta in ("src", "tests", "docs"):
        archivos.extend(
            ruta
            for ruta in (RAIZ / carpeta).rglob("*")
            if ruta.is_file() and ruta.suffix in {".py", ".md", ".json", ".yaml", ".yml"}
        )
    archivos.extend(
        ruta
        for ruta in (RAIZ / "web" / "src").rglob("*")
        if ruta.is_file() and ruta.suffix in {".ts", ".html", ".json"}
    )

    hallazgos = [
        str(ruta.relative_to(RAIZ))
        for ruta in archivos
        if any(
            patron.search(ruta.read_text(encoding="utf-8"))
            for patron in PATRONES_SECRETOS
        )
    ]

    assert hallazgos == []


def test_frontend_no_persiste_token_ni_lo_inyecta_desde_proxy():
    fuentes = [
        ruta
        for ruta in (RAIZ / "web" / "src").rglob("*.ts")
        if not ruta.name.endswith(".spec.ts")
    ]
    codigo = "\n".join(ruta.read_text(encoding="utf-8") for ruta in fuentes)
    proxy = (RAIZ / "web" / "proxy.conf.json").read_text(encoding="utf-8")
    plantilla = (
        RAIZ
        / "web"
        / "src"
        / "app"
        / "solicitudes"
        / "listado-solicitudes.component.html"
    ).read_text(encoding="utf-8")

    assert "localStorage" not in codigo
    assert "sessionStorage" not in codigo
    assert "Authorization" not in proxy
    assert "API_TOKEN" not in proxy
    assert 'name="api-token' not in plantilla
