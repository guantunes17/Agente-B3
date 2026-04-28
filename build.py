"""Empacotamento do Agente B3 em .exe via PyInstaller."""
import subprocess
import sys
from pathlib import Path


def main():
    raiz = Path(__file__).resolve().parent
    icone = raiz / "assets" / "icon.ico"
    dist_dir = raiz / "dist"

    # Gerar ícone se não existir
    if not icone.exists():
        print("Gerando ícone...")
        from build_icon import gerar_icone
        gerar_icone(icone)

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "AgenteB3",
        "--distpath", str(dist_dir),
        "--workpath", str(raiz / "build_tmp"),
        "--specpath", str(raiz),
        f"--icon={icone}",
        # Dados adicionais
        f"--add-data={raiz / 'presets'}{_sep()}presets",
        f"--add-data={raiz / 'assets'}{_sep()}assets",
        # Imports ocultos
        "--hidden-import=keyring",
        "--hidden-import=keyring.backends",
        "--hidden-import=keyring.backends.Windows",
        "--hidden-import=keyring.backends.fail",
        "--hidden-import=pandas",
        "--hidden-import=docx",
        "--hidden-import=bs4",
        "--hidden-import=colorama",
        "--hidden-import=dateutil",
        "--hidden-import=dateutil.parser",
        # Excluir módulos desnecessários para reduzir tamanho
        "--exclude-module=matplotlib",
        "--exclude-module=scipy",
        "--exclude-module=notebook",
        "--exclude-module=IPython",
        # Ponto de entrada
        str(raiz / "launcher.py"),
    ]

    print("Iniciando PyInstaller...")
    print(f"Saída: {dist_dir / 'AgenteB3.exe'}")
    resultado = subprocess.run(cmd, cwd=str(raiz))
    if resultado.returncode == 0:
        print(f"\nBuild concluído: {dist_dir / 'AgenteB3.exe'}")
    else:
        print("\nErro durante o build.")
        sys.exit(1)


def _sep() -> str:
    return ";" if sys.platform == "win32" else ":"


if __name__ == "__main__":
    main()
