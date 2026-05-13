"""Cartridge state and hardness calculations for the dispenser interface.

This module owns the cartridge configuration stored in ``cartridge_config.json``.
That file records the hardness of the two cartridge pairs and the remaining
volume in each bucket. The pygame interface imports this module to read/update
bucket volumes, find the selectable hardness range, and calculate how a
4-component dispense should be split between the low-hardness and high-hardness
cartridge pairs.

The UI should stay focused on menus and drawing. Keeping these helpers here
makes the saved cartridge state and silicone hardness math easier to test and
change without touching the interface loop.
"""

import json
import os


CARTRIDGE_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cartridge_config.json")

DEFAULT_CARTRIDGE_CONFIG = {
    "pair_ab": {"hardness": 5, "volume_a": 100, "volume_b": 100},
    "pair_cd": {"hardness": 50, "volume_c": 100, "volume_d": 100},
}

# Pair key -> volume keys for the two buckets that belong to that pair.
PAIR_VOLUME_KEYS = (
    ("pair_ab", ("volume_a", "volume_b")),
    ("pair_cd", ("volume_c", "volume_d")),
)

# Bucket index 0..3 -> (pair key, volume key in that pair). The UI labels
# these four positions as A, B, C, D.
BUCKET_KEYS = [
    (pair_key, volume_key)
    for pair_key, volume_keys in PAIR_VOLUME_KEYS
    for volume_key in volume_keys
]

# Calibration curve for the silicone additive mix:
# (target shore hardness, fraction of high-hardness pair in the mix).
# Source: "Shore waarde van mengsel Siliconen Additie Kleurloos" chart.
HARDNESS_CURVE = [
    (5.0, 0.00),
    (5.5, 0.10),
    (14.0, 0.20),
    (18.5, 0.30),
    (23.5, 0.40),
    (27.5, 0.50),
    (32.0, 0.60),
    (36.5, 0.70),
    (41.0, 0.80),
    (45.5, 0.90),
    (50.0, 1.00),
]


def default_cartridge_config():
    """Return a fresh copy of the default cartridge configuration."""
    return {key: dict(value) for key, value in DEFAULT_CARTRIDGE_CONFIG.items()}


def bucket_keys(idx):
    """Return the config pair/volume keys for bucket index 0=A, 1=B, 2=C, 3=D."""
    if idx < 0 or idx >= len(BUCKET_KEYS):
        raise IndexError("Bucket index must be 0, 1, 2, or 3.")
    return BUCKET_KEYS[idx]


def load_cartridge_config(path=CARTRIDGE_CONFIG_PATH):
    """Load cartridge state from JSON and return a complete configuration dict."""
    try:
        with open(path) as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_cartridge_config()

    migrated = migrate_cartridge_config(config)
    if migrated:
        save_cartridge_config(config, path)
    return config


def save_cartridge_config(config, path=CARTRIDGE_CONFIG_PATH):
    """Write the current cartridge state back to the JSON config file."""
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def migrate_cartridge_config(config):
    """Update older cartridge JSON shapes so the current code can use them.

    This is here because older saved configs may have stored one shared
    ``volume`` for a pair instead of separate bucket volumes such as
    ``volume_a`` and ``volume_b``. Without this compatibility step, an existing
    dispenser could crash after a software update because its old JSON file is
    missing the newer keys.
    """
    migrated = False
    for pair_key, volume_keys in PAIR_VOLUME_KEYS:
        # Compatibility migration: keep existing machines working if their
        # cartridge_config.json was created before per-bucket volumes existed.
        if pair_key not in config:
            config[pair_key] = dict(DEFAULT_CARTRIDGE_CONFIG[pair_key])
            migrated = True

        pair = config[pair_key]
        if "volume" in pair:
            split_volume = pair.pop("volume") / 2
            for volume_key in volume_keys:
                if volume_key not in pair:
                    pair[volume_key] = split_volume
            migrated = True

        for volume_key in volume_keys:
            if volume_key not in pair:
                pair[volume_key] = DEFAULT_CARTRIDGE_CONFIG[pair_key][volume_key]
                migrated = True

        if "hardness" not in pair:
            pair["hardness"] = DEFAULT_CARTRIDGE_CONFIG[pair_key]["hardness"]
            migrated = True

    return migrated


def bucket_volume(idx):
    """Return the remaining volume in ml for bucket index 0=A, 1=B, 2=C, 3=D."""
    pair_key, volume_key = bucket_keys(idx)
    return cartridge_config[pair_key][volume_key]


def set_bucket_volume(idx, value):
    """Set the remaining volume in ml for bucket index 0=A, 1=B, 2=C, 3=D."""
    pair_key, volume_key = bucket_keys(idx)
    cartridge_config[pair_key][volume_key] = value


def decrement_bucket_volumes(measured_grams, density):
    """Subtract dispensed measured grams from bucket volumes using liquid density."""
    for i in range(4):
        used_ml = (measured_grams[i] or 0) / density
        set_bucket_volume(i, max(0.0, round(bucket_volume(i) - used_ml, 2)))
    save_cartridge_config(cartridge_config)


def pair_hardnesses():
    """Return the configured hardness values for pair AB and pair CD."""
    return cartridge_config["pair_ab"]["hardness"], cartridge_config["pair_cd"]["hardness"]


def hardness_limits():
    """Return the selectable min and max hardness from the cartridge JSON state."""
    pair_ab_hardness, pair_cd_hardness = pair_hardnesses()
    return int(min(pair_ab_hardness, pair_cd_hardness)), int(max(pair_ab_hardness, pair_cd_hardness))


def hardness_to_ratio(target_shore):
    """Convert target shore hardness to fraction of high-hardness pair in the mix."""
    if target_shore <= HARDNESS_CURVE[0][0]:
        return HARDNESS_CURVE[0][1]
    if target_shore >= HARDNESS_CURVE[-1][0]:
        return HARDNESS_CURVE[-1][1]

    for (x0, r0), (x1, r1) in zip(HARDNESS_CURVE, HARDNESS_CURVE[1:]):
        if x0 <= target_shore <= x1:
            return r0 + (r1 - r0) * (target_shore - x0) / (x1 - x0)

    return 1.0


def component_amounts_for_hardness(total_weight, target_shore):
    """Return four component gram amounts for a total weight and target hardness."""
    ratio_high = hardness_to_ratio(target_shore)
    pair_ab_hardness, pair_cd_hardness = pair_hardnesses()
    weight_high = total_weight * ratio_high
    weight_low = total_weight - weight_high

    if pair_ab_hardness <= pair_cd_hardness:
        return [weight_low / 2, weight_low / 2, weight_high / 2, weight_high / 2]
    return [weight_high / 2, weight_high / 2, weight_low / 2, weight_low / 2]


cartridge_config = load_cartridge_config()
