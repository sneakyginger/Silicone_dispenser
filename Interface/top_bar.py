"""Top bar showing per-bucket fill level and the current time."""

import os
import time

import pygame

import cartridge


HEIGHT = 64
BACKGROUND_COLOR = (10, 10, 10)
TEXT_COLOR = (230, 230, 230)
BAR_TRACK_COLOR = (58, 58, 58)
COLOR_GREEN = (0x2A, 0xB6, 0x46)
COLOR_BLUE = (0x1A, 0x60, 0xD8)
COLOR_RED = (0xFC, 0x38, 0x34)

BUCKET_MAX_ML = 500
LOW_FRACTION = 0.20

SIDE_PADDING = 24
CELL_GAP = 30
CLOCK_GAP = 28
BAR_HEIGHT = 6
ICON_HEIGHT = 22
LABEL_FONT_SIZE = 26
TEXT_FONT_SIZE = 13
TIME_FONT_SIZE = 26
LABEL_ICON_GAP = 4
ICON_BAR_GAP = 6
TEXT_BAR_GAP = 2
STACK_Y_OFFSET = -3
SANS_SERIF_FONTS = "sans,arial,liberationsans,helvetica,dejavusans"
SERIF_FONTS = "liberationserif,dejavuserif,timesnewroman,times,serif"
CLOCK_FONTS = "sfprodisplay,sfpro,helveticaneue,helvetica,arial,notosans,liberationsans,dejavusans"

SPRITES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Sprites")

_font = None
_label_font = None
_time_font = None
_bucket_template = None
_tinted_buckets = {}


def _get_font():
    global _font
    if _font is None:
        _font = pygame.font.SysFont(SANS_SERIF_FONTS, TEXT_FONT_SIZE)
    return _font


def _get_label_font():
    global _label_font
    if _label_font is None:
        _label_font = pygame.font.SysFont(SERIF_FONTS, LABEL_FONT_SIZE, bold=True)
    return _label_font


def _get_time_font():
    global _time_font
    if _time_font is None:
        _time_font = pygame.font.SysFont(SERIF_FONTS, TIME_FONT_SIZE)
    return _time_font


def _bucket_color(volume_ml):
    if volume_ml >= BUCKET_MAX_ML:
        return COLOR_GREEN
    if volume_ml < BUCKET_MAX_ML * LOW_FRACTION:
        return COLOR_RED
    return COLOR_BLUE


def _load_bucket_template():
    global _bucket_template
    if _bucket_template is not None:
        return _bucket_template
    path = os.path.join(SPRITES_DIR, "bucket_white.jpg")
    try:
        img = pygame.image.load(path).convert()
        ratio = ICON_HEIGHT / img.get_height()
        new_size = (int(img.get_width() * ratio), ICON_HEIGHT)
        img = pygame.transform.smoothscale(img, new_size)
    except (pygame.error, FileNotFoundError):
        img = None
    _bucket_template = img
    return _bucket_template


def _get_bucket_icon(color):
    if color in _tinted_buckets:
        return _tinted_buckets[color]
    template = _load_bucket_template()
    if template is None:
        return None
    tinted = template.copy()
    tinted.fill(color, special_flags=pygame.BLEND_MULT)
    tinted.set_colorkey((0, 0, 0))
    _tinted_buckets[color] = tinted
    return tinted


def _draw_bucket_cell(screen, x, y, w, h, label, volume_ml):
    try:
        volume_ml = float(volume_ml)
    except (TypeError, ValueError):
        volume_ml = 0.0
    color = _bucket_color(volume_ml)
    label_font = _get_label_font()
    font = _get_font()
    center_y = y + h // 2

    label_surface = label_font.render(label, True, TEXT_COLOR)
    label_rect = label_surface.get_rect(midleft=(x, center_y))
    screen.blit(label_surface, label_rect)

    icon = _get_bucket_icon(color)
    if icon is not None:
        icon_rect = icon.get_rect(midleft=(label_rect.right + LABEL_ICON_GAP, center_y))
        screen.blit(icon, icon_rect)
        bar_x = icon_rect.right + ICON_BAR_GAP
    else:
        bar_x = label_rect.right + ICON_BAR_GAP

    bar_w = max(0, x + w - bar_x)

    vol_text = f"{int(round(volume_ml))}/{BUCKET_MAX_ML}ml"
    vol_surface = font.render(vol_text, True, TEXT_COLOR)

    stack_height = vol_surface.get_height() + TEXT_BAR_GAP + BAR_HEIGHT
    stack_top = center_y - stack_height // 2 + STACK_Y_OFFSET

    bar_rect = pygame.Rect(bar_x, stack_top + vol_surface.get_height() + TEXT_BAR_GAP, bar_w, BAR_HEIGHT)
    pygame.draw.rect(screen, BAR_TRACK_COLOR, bar_rect, border_radius=4)
    fill_w = int(bar_w * min(1.0, max(0.0, volume_ml / BUCKET_MAX_ML)))
    if fill_w > 0:
        pygame.draw.rect(screen, color, (bar_rect.x, bar_rect.y, fill_w, BAR_HEIGHT), border_radius=4)

    vol_rect = vol_surface.get_rect(midbottom=(bar_rect.centerx, bar_rect.top - TEXT_BAR_GAP))
    screen.blit(vol_surface, vol_rect)


def draw(screen):
    width = screen.get_width()
    pygame.draw.rect(screen, BACKGROUND_COLOR, (0, 0, width, HEIGHT))

    time_font = _get_time_font()
    time_surface = time_font.render(time.strftime("%H:%M"), True, TEXT_COLOR)
    time_rect = time_surface.get_rect(midright=(width - SIDE_PADDING, HEIGHT // 2))
    screen.blit(time_surface, time_rect)

    cells_area_w = time_rect.left - CLOCK_GAP - SIDE_PADDING
    cell_w = (cells_area_w - CELL_GAP * 3) // 4
    for i in range(4):
        x = SIDE_PADDING + i * (cell_w + CELL_GAP)
        volume = cartridge.bucket_volume(i)
        _draw_bucket_cell(screen, x, 0, cell_w, HEIGHT, str(i + 1), volume)
