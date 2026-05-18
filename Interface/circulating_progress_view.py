"""Circulation progress screen styled like the dispensing progress screen."""

import pygame

import theme
import top_bar


BACKGROUND_COLOR = theme.WHITE
TEXT_COLOR = theme.BLACK
TRACK_COLOR = theme.TOP_BAR_TRACK
BAR_OK_COLOR = theme.BUCKET_FULL
BAR_ACTIVE_COLOR = theme.BUCKET_NORMAL
BAR_ERROR_COLOR = theme.BUCKET_LOW

SIDE_PADDING = 48
ROW_GAP = 22
BAR_HEIGHT = 12
LABEL_WIDTH = 150
VALUE_WIDTH = 170
ICON_GAP = 8

_title_font = None
_label_font = None
_text_font = None


def _get_title_font():
    global _title_font
    if _title_font is None:
        _title_font = pygame.font.SysFont(theme.SERIF_FONTS, theme.FONT_SIZE_NORMAL)
    return _title_font


def _get_label_font():
    global _label_font
    if _label_font is None:
        _label_font = pygame.font.SysFont(theme.SERIF_FONTS, theme.TOP_BAR_LABEL_FONT_SIZE, bold=True)
    return _label_font


def _get_text_font():
    global _text_font
    if _text_font is None:
        _text_font = pygame.font.SysFont(theme.SANS_SERIF_FONTS, theme.FONT_SIZE_SMALL)
    return _text_font


def _format_time(seconds):
    total_seconds = int(round(max(0.0, seconds)))
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def _progress_color(active, elapsed, duration, error):
    if error:
        return BAR_ERROR_COLOR
    if not active:
        return TRACK_COLOR
    if elapsed >= duration:
        return BAR_OK_COLOR
    return BAR_ACTIVE_COLOR


def _draw_bucket_row(screen, row_index, y, active, elapsed, duration, error):
    width = screen.get_width()
    label_font = _get_label_font()
    text_font = _get_text_font()

    label = label_font.render(str(row_index + 1), True, TEXT_COLOR)
    label_rect = label.get_rect(midleft=(SIDE_PADDING, y))
    screen.blit(label, label_rect)

    color = _progress_color(active, elapsed, duration, error)
    icon = top_bar._get_bucket_icon(color)
    if icon is not None:
        icon_rect = icon.get_rect(midleft=(label_rect.right + ICON_GAP, y))
        screen.blit(icon, icon_rect)

    shown_elapsed = min(elapsed, duration) if active else 0.0
    value = text_font.render(f"{_format_time(shown_elapsed)} / {_format_time(duration)}", True, TEXT_COLOR)
    value_rect = value.get_rect(midleft=(SIDE_PADDING + LABEL_WIDTH, y))
    screen.blit(value, value_rect)

    bar_x = SIDE_PADDING + LABEL_WIDTH + VALUE_WIDTH
    bar_w = max(1, width - SIDE_PADDING - bar_x)
    bar_rect = pygame.Rect(bar_x, y - BAR_HEIGHT // 2, bar_w, BAR_HEIGHT)
    pygame.draw.rect(screen, TRACK_COLOR, bar_rect, border_radius=6)

    if active and duration > 0:
        fraction = min(1.0, max(0.0, elapsed / duration))
        fill_w = int(bar_w * fraction)
        if fill_w > 0:
            pygame.draw.rect(screen, color, (bar_rect.x, bar_rect.y, fill_w, BAR_HEIGHT), border_radius=6)


def draw(screen, snapshot):
    screen.fill(BACKGROUND_COLOR)
    width = screen.get_width()

    title_font = _get_title_font()
    error = snapshot.get("error", "")
    title = "CIRCULATING"
    if error:
        title = "CIRCULATION ERROR"
    elif snapshot.get("done"):
        title = "CIRCULATION COMPLETE"

    title_surface = title_font.render(title, True, TEXT_COLOR)
    title_rect = title_surface.get_rect(midtop=(width // 2, top_bar.HEIGHT + 28))
    screen.blit(title_surface, title_rect)

    active = snapshot.get("active", [False, False, False, False])
    elapsed = snapshot.get("elapsed", [0.0, 0.0, 0.0, 0.0])
    duration = snapshot.get("duration_seconds", 0.0)
    start_y = title_rect.bottom + 52
    row_height = BAR_HEIGHT + ROW_GAP
    for row_index in range(4):
        _draw_bucket_row(screen, row_index, start_y + row_index * row_height, active[row_index], elapsed[row_index], duration, error)

    if error:
        text_font = _get_text_font()
        error_surface = text_font.render(error[:80], True, BAR_ERROR_COLOR)
        error_rect = error_surface.get_rect(midtop=(width // 2, start_y + 4 * row_height + 18))
        screen.blit(error_surface, error_rect)
