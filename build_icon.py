"""Gera o ícone da aplicação (assets/icon.ico) usando Pillow."""
import sys
from pathlib import Path


def gerar_icone(caminho_saida: Path | None = None) -> Path:
    """Gera ícone 256x256 azul escuro com 'B3' branco."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("Pillow não instalado. Execute: pip install Pillow")
        sys.exit(1)

    if caminho_saida is None:
        caminho_saida = Path(__file__).resolve().parent / "assets" / "icon.ico"
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    tamanhos = [256, 128, 64, 32, 16]
    imagens = []

    for size in tamanhos:
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        raio = size // 8
        draw.rounded_rectangle(
            [(0, 0), (size - 1, size - 1)],
            radius=raio,
            fill=(31, 56, 100, 255)
        )

        texto = "B3"
        fonte_tamanho = max(8, int(size * 0.40))
        fonte = None
        for nome_fonte in ["arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]:
            try:
                fonte = ImageFont.truetype(nome_fonte, fonte_tamanho)
                break
            except (IOError, OSError):
                continue
        if fonte is None:
            fonte = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), texto, font=fonte)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (size - tw) // 2 - bbox[0]
        y = (size - th) // 2 - bbox[1]
        draw.text((x, y), texto, font=fonte, fill=(255, 255, 255, 255))

        imagens.append(img)

    imagens[0].save(
        caminho_saida,
        format="ICO",
        sizes=[(s, s) for s in tamanhos],
        append_images=imagens[1:]
    )
    print(f"Ícone gerado: {caminho_saida}")
    return caminho_saida


if __name__ == "__main__":
    gerar_icone()
