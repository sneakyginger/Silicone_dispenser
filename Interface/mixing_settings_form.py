"""Encoder-driven form for the mixing schedule settings."""

import pygame

import saved_settings
import theme


FREQUENCY_DAILY = "daily"
FREQUENCY_WEEKLY = "weekly"
FREQUENCIES = (FREQUENCY_DAILY, FREQUENCY_WEEKLY)
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MINUTE_STEP = 5
ROW_FREQUENCY = 0
ROW_START_TIME = 1
ROW_DURATION = 2
ROW_RETURN = 3
FIELD_FREQUENCY = "frequency"
FIELD_WEEKDAY = "weekday"
FIELD_HOUR = "hour"
FIELD_MINUTE = "minute"
FIELD_DURATION = "duration"


def default_state():
    settings = saved_settings.mixing_settings()
    return {
        "location": ROW_FREQUENCY,
        "editing": False,
        "edit_field": None,
        "frequency": settings["frequency"],
        "weekday": settings["weekday"],
        "hour": settings["hour"],
        "minute": settings["minute"],
        "duration_minutes": settings["duration_minutes"],
    }


def handle_turn(state, direction, location):
    state = dict(state)
    if state["editing"]:
        _change_value(state, direction)
    else:
        state["location"] = _clamp_location(location)
    return state


def handle_click(state, location):
    state = dict(state)
    state["location"] = _clamp_location(location)

    if state["editing"]:
        _advance_edit_field(state)
        saved_settings.set_mixing_settings(_settings_from_state(state))
        return state, False

    if state["location"] == ROW_RETURN:
        return state, True

    state["editing"] = True
    state["edit_field"] = _first_edit_field(state)
    return state, False


def draw(screen, width, height, state, create_text):
    row_rects = [
        pygame.Rect(80, (height-22)/5*2-72/2, width - 160, 72),
        pygame.Rect(80, (height-22)/5*3-72/2, width - 160, 72),
        pygame.Rect(80, (height-22)/5*4-72/2, width - 160, 72),
    ]
    rows = [
        ("Frequency", _frequency_label(state), FIELD_FREQUENCY),
        ("Mixing time", _start_time_label(state), state["edit_field"]),
        ("Mix duration", _duration_label(state), FIELD_DURATION),
    ]

    for index, rect in enumerate(row_rects):
        selected = state["location"] == index
        editing = state["editing"] and selected
        border_color = theme.BLACK if selected else theme.SELECTION_BAR_TRACK
        fill_color = (235, 235, 235) if editing else theme.WHITE
        pygame.draw.rect(screen, fill_color, rect)
        pygame.draw.rect(screen, border_color, rect, 3 if selected else 1)

        label, value, _edit_field = rows[index]
        label_text, label_rect = create_text(label, (rect.left + 120, rect.centery), theme.BLACK, "small")
        screen.blit(label_text, label_rect)
        if index == ROW_DURATION:
            duration_text, duration_rect = create_text(value, (rect.right - 190, rect.centery - 14), theme.BLACK, "small")
            sequence_text, sequence_rect = create_text("(one at a time)", (rect.right - 190, rect.centery + 18), theme.BLACK, "small")
            screen.blit(duration_text, duration_rect)
            screen.blit(sequence_text, sequence_rect)
        else:
            value_text, value_rect = create_text(value, (rect.right - 190, rect.centery), theme.BLACK, "small")
            screen.blit(value_text, value_rect)


def _change_value(state, direction):
    step = -1 if direction == "left" else 1
    field = state["edit_field"]
    if field == FIELD_FREQUENCY:
        current_index = FREQUENCIES.index(state["frequency"])
        state["frequency"] = FREQUENCIES[(current_index + step) % len(FREQUENCIES)]
        if state["frequency"] == FREQUENCY_DAILY and state["edit_field"] == FIELD_WEEKDAY:
            state["edit_field"] = FIELD_HOUR
    elif field == FIELD_WEEKDAY:
        state["weekday"] = (state["weekday"] + step) % len(WEEKDAYS)
    elif field == FIELD_HOUR:
        state["hour"] = (state["hour"] + step) % 24
    elif field == FIELD_MINUTE:
        state["minute"] = (state["minute"] + (step * MINUTE_STEP)) % 60
    elif field == FIELD_DURATION:
        state["duration_minutes"] = min(10, max(1, state["duration_minutes"] + step))


def _advance_edit_field(state):
    if state["location"] == ROW_START_TIME:
        fields = _start_time_fields(state)
        field_index = fields.index(state["edit_field"])
        if field_index < len(fields) - 1:
            state["edit_field"] = fields[field_index + 1]
            return

    state["editing"] = False
    state["edit_field"] = None


def _first_edit_field(state):
    if state["location"] == ROW_FREQUENCY:
        return FIELD_FREQUENCY
    if state["location"] == ROW_START_TIME:
        return _start_time_fields(state)[0]
    return FIELD_DURATION


def _start_time_fields(state):
    if state["frequency"] == FREQUENCY_WEEKLY:
        return (FIELD_WEEKDAY, FIELD_HOUR, FIELD_MINUTE)
    return (FIELD_HOUR, FIELD_MINUTE)


def _settings_from_state(state):
    return {
        "frequency": state["frequency"],
        "weekday": state["weekday"],
        "hour": state["hour"],
        "minute": state["minute"],
        "duration_minutes": state["duration_minutes"],
    }


def _clamp_location(location):
    return min(ROW_RETURN, max(ROW_FREQUENCY, location))


def _frequency_label(state):
    return state["frequency"].capitalize()


def _start_time_label(state):
    time_text = f"{state['hour']:02d}:{state['minute']:02d}"
    if state["frequency"] == FREQUENCY_DAILY:
        return f"Every day {time_text}"
    return f"{WEEKDAYS[state['weekday']]} {time_text}"


def _duration_label(state):
    return f"{state['duration_minutes']} min per bucket"

