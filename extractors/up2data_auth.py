"""
Autenticação no UP2DATA Cloud.

Fluxo:
1. Gerar token JWT usando Client ID + Client Secret + certificado .pfx
2. Usar token JWT para obter chaves SAS dos canais contratados
3. Cachear token (24h) e chaves SAS (90 dias) para evitar chamadas desnecessárias

Boas práticas B3:
- Token JWT: consultar apenas 1x/dia
- Chaves SAS: não mudam durante o dia
- Downloads: a cada 5 minutos ou via RSS
"""
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

CACHE_FILE = Path.home() / ".agenteb3" / "up2data_cache.json"


class UP2DataAuth:
    """Gerencia autenticação e cache de tokens/chaves SAS do UP2DATA Cloud."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        cert_path: str,
        cert_password: str | None = None,
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.cert_path = Path(cert_path) if cert_path else None
        self.cert_password = cert_password
        self._token_cache: dict | None = None
        self._sas_cache: dict | None = None
        self._load_cache()

    def obter_token_jwt(self) -> str:
        """
        Obtém token JWT válido.
        Usa cache se o token ainda estiver válido (< 24h).
        """
        if self._token_cache and self._token_valido():
            logger.debug("Usando token JWT do cache.")
            return self._token_cache["token"]

        logger.info("Gerando novo token JWT no UP2DATA...")
        # PLACEHOLDER — implementar quando credenciais estiverem disponíveis.
        # Estrutura baseada na documentação pública da B3:
        # 1. Carregar certificado .pfx via cryptography.hazmat.primitives.serialization.pkcs12
        # 2. POST para UP2DATA_TOKEN_ENDPOINT com Client ID, Client Secret e certificado
        # 3. Receber token JWT, salvar no cache com timestamp
        raise NotImplementedError(
            "Autenticação UP2DATA ainda não configurada. "
            "Configure as credenciais em Configurações → UP2DATA."
        )

    def obter_chaves_sas(self) -> dict:
        """
        Obtém chaves SAS para os canais contratados.
        Usa cache se as chaves ainda estiverem válidas (< 90 dias).
        Retorna dict: {canal: sas_url}
        """
        if self._sas_cache and self._sas_valida():
            logger.debug("Usando chaves SAS do cache.")
            return self._sas_cache["chaves"]

        logger.info("Obtendo novas chaves SAS do UP2DATA...")
        token = self.obter_token_jwt()
        # PLACEHOLDER — implementar quando credenciais estiverem disponíveis.
        # 1. GET/POST para UP2DATA_SAS_ENDPOINT com token JWT no header Authorization
        # 2. Receber chaves SAS por canal
        # 3. Salvar no cache com timestamp
        raise NotImplementedError("Obtenção de chaves SAS ainda não configurada.")

    def _token_valido(self) -> bool:
        if not self._token_cache:
            return False
        gerado_em = datetime.fromisoformat(self._token_cache.get("gerado_em", "2000-01-01"))
        return datetime.now() - gerado_em < timedelta(hours=24)

    def _sas_valida(self) -> bool:
        if not self._sas_cache:
            return False
        gerado_em = datetime.fromisoformat(self._sas_cache.get("gerado_em", "2000-01-01"))
        # Renovar 5 dias antes do vencimento de 90 dias
        return datetime.now() - gerado_em < timedelta(days=85)

    def _load_cache(self):
        if CACHE_FILE.exists():
            try:
                data = json.loads(CACHE_FILE.read_text(encoding="utf-8"))
                self._token_cache = data.get("token")
                self._sas_cache = data.get("sas")
            except Exception:
                self._token_cache = None
                self._sas_cache = None

    def _save_cache(self):
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {"token": self._token_cache, "sas": self._sas_cache}
        CACHE_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def limpar_cache(self):
        """Remove o cache local, forçando nova autenticação na próxima chamada."""
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
        self._token_cache = None
        self._sas_cache = None
        logger.info("Cache de autenticação UP2DATA limpo.")

    @staticmethod
    def disponivel() -> bool:
        """Verifica se as credenciais UP2DATA Cloud estão configuradas."""
        try:
            from gui.credentials import obter_credencial
            return bool(obter_credencial("up2data_client_id"))
        except ImportError:
            return False
