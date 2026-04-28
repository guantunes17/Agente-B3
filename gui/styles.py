"""Constantes visuais do Agente B3 — Design System (CustomTkinter)."""
import customtkinter as ctk

COLORS = {
    # Sidebar (escura)
    "sidebar_bg": "#0F1C33",
    "sidebar_item": "#8899B0",
    "sidebar_item_hover": "#B8C8DE",
    "sidebar_item_active_bg": "#1A3258",
    "sidebar_item_active_text": "#FFFFFF",
    "sidebar_border": "#1A2A45",
    "sidebar_status_text": "#5A6F8E",

    # Cores primárias (B3 azul)
    "primary_900": "#042C53",
    "primary_800": "#0C447C",
    "primary_700": "#185FA5",
    "primary_600": "#2E5FA3",
    "primary_500": "#378ADD",
    "primary_400": "#4A90D9",
    "primary_300": "#85B7EB",
    "primary_200": "#B5D4F4",
    "primary_100": "#D5E8F0",
    "primary_50": "#E6F1FB",

    # Acentos
    "accent_teal": "#5DCAA5",
    "accent_teal_dark": "#0F6E56",
    "accent_coral": "#F0997B",
    "accent_coral_dark": "#993C1D",

    # Superfícies
    "bg_main": "#F8FAFB",
    "bg_card": "#FFFFFF",
    "bg_card_hover": "#FAFCFD",
    "bg_input": "#F5F5F5",
    "bg_gradient_start": "#E6F1FB",
    "bg_gradient_end": "#F8FAFB",

    # Texto
    "text_primary": "#1A1A1A",
    "text_secondary": "#666666",
    "text_muted": "#999999",
    "text_on_primary": "#FFFFFF",

    # Status
    "success": "#27500A",
    "success_bg": "#EAF3DE",
    "success_dot": "#3B6D11",
    "warning": "#633806",
    "warning_bg": "#FAEEDA",
    "error": "#791F1F",
    "error_bg": "#FCEBEB",

    # Borders
    "border_light": "#E8EDF4",
    "border_medium": "#D0D8E4",
    "border_active": "#2E5FA3",

    # Toggle / checkbox
    "toggle_active_bg": "#D5E8F0",
    "toggle_active_border": "#2E5FA3",
    "toggle_active_text": "#0C447C",
    "toggle_inactive_bg": "#F0F0F0",
    "toggle_inactive_text": "#888888",

    # Dots de navegação da sidebar
    "dot_gerar": "#4A90D9",
    "dot_historico": "#5DCAA5",
    "dot_agenda": "#F0997B",
    "dot_config": "#8899B0",
}

FONTS = {
    "page_title": ("Arial", 20, "bold"),
    "page_subtitle": ("Arial", 13),
    "card_title": ("Arial", 14, "bold"),
    "section_title": ("Arial", 12, "bold"),
    "body": ("Arial", 13),
    "small": ("Arial", 11),
    "field_label": ("Arial", 11),
    "button": ("Arial", 14, "bold"),
    "button_sm": ("Arial", 12),
    "sidebar_title": ("Arial", 13, "bold"),
    "sidebar_sub": ("Arial", 10),
    "sidebar_item": ("Arial", 13),
    "metric_value": ("Arial", 28, "bold"),
    "metric_label": ("Arial", 11),
    "status_text": ("Arial", 12),
}

SIZES = {
    "sidebar_width": 220,
    "min_window_width": 900,
    "min_window_height": 650,
    "default_window_width": 1050,
    "default_window_height": 720,
    "card_corner_radius": 12,
    "card_padding": 20,
    "page_padding_x": 32,
    "page_padding_y": 28,
    "section_gap": 16,
    "field_gap": 12,
    "button_height": 44,
    "button_corner_radius": 10,
    "input_height": 38,
    "input_corner_radius": 8,
    "toggle_corner_radius": 8,
    "toggle_padding_x": 16,
    "toggle_padding_y": 8,
}


def configurar_tema():
    """Configura o tema global do CustomTkinter."""
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
