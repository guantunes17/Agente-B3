"""Gerenciamento seguro de credenciais via keyring com fallback para .env."""
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

_SERVICO = "AgenteB3"

_CHAVES = {
    "b3_usuario": "B3_USUARIO",
    "b3_senha": "B3_SENHA",
    "b3_certificado": "B3_CERTIFICADO_PFX",
    "anbima_client_id": "ANBIMA_CLIENT_ID",
    "anbima_client_secret": "ANBIMA_CLIENT_SECRET",
    "up2data_client_id": "UP2DATA_CLIENT_ID",
    "up2data_client_secret": "UP2DATA_CLIENT_SECRET",
    "up2data_cert_path": "UP2DATA_CERT_PATH",
    "up2data_cert_password": "UP2DATA_CERT_PASSWORD",
    "up2data_client_path": "UP2DATA_CLIENT_PATH",
}

try:
    import keyring
    _KEYRING_DISPONIVEL = True
except ImportError:
    _KEYRING_DISPONIVEL = False
    logger.warning("keyring não instalado — credenciais salvas apenas em .env")


def salvar_credencial(chave: str, valor: str) -> bool:
    """Salva credencial no keyring ou no .env como fallback."""
    if not valor:
        return False
    if _KEYRING_DISPONIVEL:
        try:
            keyring.set_password(_SERVICO, chave, valor)
            return True
        except Exception as e:
            logger.warning(f"keyring falhou ao salvar '{chave}': {e}")
    return _salvar_env(chave, valor)


def obter_credencial(chave: str) -> str | None:
    """Obtém credencial do keyring ou do .env como fallback."""
    if _KEYRING_DISPONIVEL:
        try:
            valor = keyring.get_password(_SERVICO, chave)
            if valor is not None:
                return valor
        except Exception as e:
            logger.warning(f"keyring falhou ao ler '{chave}': {e}")
    return _ler_env(chave)


def obter_todas_credenciais() -> dict[str, str]:
    """Retorna todas as credenciais conhecidas (valores vazios se ausentes)."""
    return {chave: (obter_credencial(chave) or "") for chave in _CHAVES}


def salvar_todas_credenciais(dados: dict[str, str]) -> None:
    """Salva um dicionário de credenciais."""
    for chave, valor in dados.items():
        if chave in _CHAVES and valor:
            salvar_credencial(chave, valor)


def tem_credenciais_b3() -> bool:
    """Verifica se as credenciais mínimas da B3 estão configuradas."""
    usuario = obter_credencial("b3_usuario")
    senha = obter_credencial("b3_senha")
    return bool(usuario and senha)


def tem_credenciais_anbima() -> bool:
    """Verifica se as credenciais da ANBIMA estão configuradas."""
    client_id = obter_credencial("anbima_client_id")
    return bool(client_id)


def tem_credenciais_up2data_cloud() -> bool:
    """Verifica se as credenciais UP2DATA Cloud estão configuradas."""
    return bool(obter_credencial("up2data_client_id"))


def tem_credenciais_up2data_client() -> bool:
    """Verifica se o diretório do UP2DATA Client está configurado e existe."""
    from pathlib import Path
    path = obter_credencial("up2data_client_path")
    return bool(path) and Path(path).exists()


def status_credenciais() -> dict[str, bool]:
    """Retorna o status de cada fonte de dados."""
    return {
        "b3": tem_credenciais_b3(),
        "anbima": tem_credenciais_anbima(),
        "up2data_cloud": tem_credenciais_up2data_cloud(),
        "up2data_client": tem_credenciais_up2data_client(),
    }


# ── Fallback .env ─────────────────────────────────────────────────────────────

def _caminho_env() -> Path:
    raiz = Path(__file__).resolve().parent.parent
    return raiz / ".env"


def _ler_env(chave: str) -> str | None:
    env_var = _CHAVES.get(chave, chave.upper())
    caminho = _caminho_env()
    if not caminho.exists():
        return None
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if linha.startswith(f"{env_var}="):
            return linha.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def _salvar_env(chave: str, valor: str) -> bool:
    env_var = _CHAVES.get(chave, chave.upper())
    caminho = _caminho_env()
    linhas = []
    if caminho.exists():
        linhas = caminho.read_text(encoding="utf-8").splitlines()

    nova_linha = f'{env_var}="{valor}"'
    for i, linha in enumerate(linhas):
        if linha.startswith(f"{env_var}="):
            linhas[i] = nova_linha
            break
    else:
        linhas.append(nova_linha)

    caminho.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    return True
