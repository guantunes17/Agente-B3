"""Gera o ícone da aplicação (assets/icon.ico) usando o logo cubo 3D do Agente B3."""
import sys
from pathlib import Path


def gerar_icone(caminho_saida: Path | None = None) -> Path:
    """Gera ícone usando o logo cubo 3D isométrico."""
    if caminho_saida is None:
        caminho_saida = Path(__file__).resolve().parent / "assets" / "icon.ico"
    try:
        from gui.logo import salvar_ico
        salvar_ico(caminho_saida)
        print(f"Ícone gerado: {caminho_saida}")
        return caminho_saida
    except ImportError:
        print("Pillow não instalado. Execute: pip install Pillow")
        sys.exit(1)


if __name__ == "__main__":
    gerar_icone()
