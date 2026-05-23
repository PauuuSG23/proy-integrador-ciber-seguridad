import os
import sys
from getpass import getpass
from pathlib import Path


def _validate_api_key(api_key: str) -> str:
    if not api_key:
        raise RuntimeError(
            "Falta OPENAI_API_KEY. Define una API key real antes de ejecutar el script."
        )

    lowered = api_key.lower()
    looks_like_placeholder = (
        (api_key.startswith("{{") and api_key.endswith("}}"))
        or "openai_api_key" in lowered
        or "your_api_key" in lowered
        or "tu_api_key" in lowered
    )
    if looks_like_placeholder:
        raise RuntimeError(
            "OPENAI_API_KEY contiene un placeholder. Reemplázalo por una clave real."
        )

    if "*" in api_key:
        raise RuntimeError(
            "OPENAI_API_KEY parece estar redactada o incompleta. Usa la clave completa."
        )

    return api_key

def _read_key_from_dotenv() -> str:
    dotenv_path = Path(".env")
    if not dotenv_path.is_file():
        return ""

    try:
        for raw_line in dotenv_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            if name.strip() != "OPENAI_API_KEY":
                continue

            candidate = value.strip()
            if (
                (candidate.startswith('"') and candidate.endswith('"'))
                or (candidate.startswith("'") and candidate.endswith("'"))
            ) and len(candidate) >= 2:
                candidate = candidate[1:-1].strip()

            return candidate
    except OSError:
        return ""

    return ""


def prompt_for_openai_api_key() -> str:
    print("OPENAI_API_KEY no válida. Ingresa una clave real para esta ejecución.")
    typed_key = getpass("OPENAI_API_KEY: ").strip()
    valid_key = _validate_api_key(typed_key)
    os.environ["OPENAI_API_KEY"] = valid_key
    return valid_key


def get_openai_api_key() -> str:
    env_key = (os.getenv("OPENAI_API_KEY") or "").strip()
    env_error = None
    try:
        return _validate_api_key(env_key)
    except RuntimeError as env_error:
        pass

    dotenv_key = _read_key_from_dotenv().strip()
    if dotenv_key:
        valid_from_dotenv = _validate_api_key(dotenv_key)
        os.environ["OPENAI_API_KEY"] = valid_from_dotenv
        return valid_from_dotenv

    if not sys.stdin.isatty():
        if env_error is not None:
            raise env_error
        raise RuntimeError(
            "Falta OPENAI_API_KEY. Define una API key real antes de ejecutar el script."
        )

    return prompt_for_openai_api_key()


def authentication_error_message() -> str:
    return (
        "Autenticación fallida con OpenAI (401). "
        "Verifica que OPENAI_API_KEY sea válida y esté activa."
    )
