"""
Logo do Agente B3 — Cubo de dados 3D isométrico.

O cubo representa processamento de dados multidimensional.
Nós verdes nos vértices representam pontos de dados conectados.
"""
from PIL import Image, ImageDraw
from pathlib import Path


def gerar_logo(tamanho: int = 256) -> Image.Image:
    """
    Gera a imagem do logo do Agente B3.

    Design: Cubo isométrico em fundo azul escuro (#0F1C33),
    arestas em azul (#2E5FA3 e #4A90D9), faces semi-transparentes,
    nós verdes (#5DCAA5) nos vértices.
    """
    img = Image.new("RGBA", (tamanho, tamanho), (15, 28, 51, 255))
    draw = ImageDraw.Draw(img)

    corner = tamanho // 5
    draw.rounded_rectangle(
        [0, 0, tamanho - 1, tamanho - 1],
        radius=corner,
        fill=(15, 28, 51, 255),
    )

    cx, cy = tamanho // 2, tamanho // 2
    s = tamanho * 0.32

    top = (cx, int(cy - s * 0.95))
    right_top = (int(cx + s * 0.85), int(cy - s * 0.45))
    left_top = (int(cx - s * 0.85), int(cy - s * 0.45))
    center = (cx, cy + int(s * 0.05))
    right_bottom = (int(cx + s * 0.85), int(cy + s * 0.55))
    left_bottom = (int(cx - s * 0.85), int(cy + s * 0.55))
    bottom = (cx, int(cy + s * 1.05))

    # Faces semi-transparentes (usar imagem overlay)
    overlay = Image.new("RGBA", (tamanho, tamanho), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.polygon([top, right_top, center, left_top], fill=(74, 144, 217, 40))
    overlay_draw.polygon([center, right_top, right_bottom, bottom], fill=(46, 95, 163, 40))
    overlay_draw.polygon([center, left_top, left_bottom, bottom], fill=(24, 95, 165, 25))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    edge_color_top = (46, 95, 163, 200)
    edge_color_bottom = (74, 144, 217, 130)
    edge_width = max(1, tamanho // 100)

    draw.line([top, right_top], fill=edge_color_top, width=edge_width)
    draw.line([top, left_top], fill=edge_color_top, width=edge_width)
    draw.line([right_top, center], fill=edge_color_top, width=edge_width)
    draw.line([left_top, center], fill=edge_color_top, width=edge_width)
    draw.line([top, center], fill=edge_color_top, width=edge_width)
    draw.line([center, right_bottom], fill=edge_color_bottom, width=edge_width)
    draw.line([center, left_bottom], fill=edge_color_bottom, width=edge_width)
    draw.line([center, bottom], fill=edge_color_bottom, width=edge_width)
    draw.line([right_top, right_bottom], fill=edge_color_bottom, width=edge_width)
    draw.line([left_top, left_bottom], fill=edge_color_bottom, width=edge_width)
    draw.line([right_bottom, bottom], fill=edge_color_bottom, width=edge_width)
    draw.line([left_bottom, bottom], fill=edge_color_bottom, width=edge_width)

    node_radius_big = max(2, tamanho // 40)
    node_radius_small = max(2, tamanho // 50)
    green = (93, 202, 165, 255)
    blue_dim = (74, 144, 217, 150)

    for pt in [top, right_top, left_top]:
        r = node_radius_big
        draw.ellipse([pt[0]-r, pt[1]-r, pt[0]+r, pt[1]+r], fill=green)
    r = node_radius_big + 1
    draw.ellipse([center[0]-r, center[1]-r, center[0]+r, center[1]+r], fill=green)
    for pt in [right_bottom, left_bottom, bottom]:
        r = node_radius_small
        draw.ellipse([pt[0]-r, pt[1]-r, pt[0]+r, pt[1]+r], fill=blue_dim)

    return img


def gerar_ctk_image(tamanho_display: int = 32):
    """Gera CTkImage para uso no CustomTkinter."""
    import customtkinter as ctk
    img = gerar_logo(tamanho_display * 4)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(tamanho_display, tamanho_display))


def salvar_ico(caminho: Path):
    """Salva o logo como .ico para ícone da janela e do .exe."""
    img = gerar_logo(256)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(caminho), format="ICO",
             sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])


def salvar_png(caminho: Path, tamanho: int = 512):
    """Salva o logo como .png."""
    img = gerar_logo(tamanho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(caminho), format="PNG")
