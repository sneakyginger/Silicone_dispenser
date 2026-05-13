"""Bucket state and hardness calculations for the dispenser interface.

This module owns the cartridge configuration stored in ``saved_settings.json``.
That file can also hold other saved dispenser information later. For now it
records the four physical buckets, the component in each bucket, the bucket
hardness group, and the remaining volume. The pygame interface imports this
module to read/update bucket volumes, find the selectable hardness range, and
calculate how a 4-component dispense should be split between the small- and
big-hardness buckets.

The UI should stay focused on menus and drawing. Keeping these helpers here
makes the saved cartridge state and silicone hardness math easier to test and
change without touching the interface loop.
"""

import json
import os


SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_settings.json")
LEGACY_CARTRIDGE_CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cartridge_config.json")
CARTRIDGE_CONFIG_PATH = SETTINGS_PATH

DEFAULT_CARTRIDGE_CONFIG = {
    "buckets": {
        "bucket_1": {"component": "A", "hardness_group": "small", "hardness": 5, "volume": 100},
        "bucket_2": {"component": "B", "hardness_group": "small", "hardness": 5, "volume": 100},
        "bucket_3": {"component": "A", "hardness_group": "big", "hardness": 50, "volume": 100},
        "bucket_4": {"component": "B", "hardness_group": "big", "hardness": 50, "volume": 100},
    }
}

# Python lists use index 0..3, but the machine labels the physical reservoirs
# as bucket 1..4.
BUCKET_KEYS = ("bucket_1", "bucket_2", "bucket_3", "bucket_4")
SMALL_HARDNESS_BUCKETS = ("bucket_1", "bucket_2")
BIG_HARDNESS_BUCKETS = ("bucket_3", "bucket_4")

# Calibration curve for the silicone additive mix:
# (target shore hardness, fraction of big-hardness buckets in the mix).
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
    return {
        "buckets": {
            bucket_key: dict(bucket)
            for bucket_key, bucket in DEFAULT_CARTRIDGE_CONFIG["buckets"].items()
        }
    }


def bucket_keys(idx):
    """Return the config bucket key for index 0=bucket 1 through 3=bucket 4."""
    if idx < 0 or idx >= len(BUCKET_KEYS):
        raise IndexError("Bucket index must be 0, 1, 2, or 3.")
    return BUCKET_KEYS[idx]


def load_cartridge_config(path=CARTRIDGE_CONFIG_PATH):
    """Load cartridge state from JSON and return a complete configuration dict."""
    loaded_from_legacy_path = False
    if path == CARTRIDGE_CONFIG_PATH and not os.path.exists(path) and os.path.exists(LEGACY_CARTRIDGE_CONFIG_PATH):
        path = LEGACY_CARTRIDGE_CONFIG_PATH
        loaded_from_legacy_path = True

    try:
        with open(path) as f:
            config = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_cartridge_config()

    migrated = migrate_cartridge_config(config)
    if migrated or loaded_from_legacy_path:
        save_settings(config, CARTRIDGE_CONFIG_PATH)
    return config


def save_settings(config, path=CARTRIDGE_CONFIG_PATH):
    """Write the current cartridge state back to the saved settings JSON file."""
    with open(path, "w") as f:
        json.dump(config, f, indent=2)


def migrate_cartridge_config(config):
    """Update older cartridge JSON shapes so the current code can use them.

    Older configs used ``pair_ab``/``pair_cd`` with volumes such as
    ``volume_a`` and ``volume_b``. The current shape is bucket-first:
    ``buckets.bucket_1`` through ``buckets.bucket_4``.
    """
    migrated = False
    defaults = default_cartridge_config()

    if "buckets" not in config:
        old_pair_ab = config.get("pair_ab", {})
        old_pair_cd = config.get("pair_cd", {})
        small_hardness = old_pair_ab.get("hardness", defaults["buckets"]["bucket_1"]["hardness"])
        big_hardness = old_pair_cd.get("hardness", defaults["buckets"]["bucket_3"]["hardness"])

        small_volume = old_pair_ab.get("volume")
        big_volume = old_pair_cd.get("volume")
        config["buckets"] = {
            "bucket_1": {
                "component": "A",
                "hardness_group": "small",
                "hardness": small_hardness,
                "volume": old_pair_ab.get("volume_a", small_volume / 2 if small_volume is not None else 100),
            },
            "bucket_2": {
                "component": "B",
                "hardness_group": "small",
                "hardness": small_hardness,
                "volume": old_pair_ab.get("volume_b", small_volume / 2 if small_volume is not None else 100),
            },
            "bucket_3": {
                "component": "A",
                "hardness_group": "big",
                "hardness": big_hardness,
                "volume": old_pair_cd.get("volume_c", big_volume / 2 if big_volume is not None else 100),
            },
            "bucket_4": {
                "component": "B",
                "hardness_group": "big",
                "hardness": big_hardness,
                "volume": old_pair_cd.get("volume_d", big_volume / 2 if big_volume is not None else 100),
            },
        }
        config.pop("pair_ab", None)
        config.pop("pair_cd", None)
        migrated = True

    buckets = config["buckets"]
    for bucket_key, default_bucket in defaults["buckets"].items():
        if bucket_key not in buckets:
            buckets[bucket_key] = dict(default_bucket)
            migrated = True

        bucket = buckets[bucket_key]
        for field, default_value in default_bucket.items():
            if field not in bucket:
                bucket[field] = default_value
                migrated = True

    return migrated


def bucket_volume(idx):
    """Return remaining volume in ml for index 0=bucket 1 through 3=bucket 4."""
    return cartridge_config["buckets"][bucket_keys(idx)]["volume"]


def set_bucket_volume(idx, value):
    """Set remaining volume in ml for index 0=bucket 1 through 3=bucket 4."""
    cartridge_config["buckets"][bucket_keys(idx)]["volume"] = float(value)


def decrement_bucket_volumes(measured_grams, density):
    """Subtract dispensed measured grams from bucket volumes using liquid density."""
    for i in range(4):
        used_ml = (measured_grams[i] or 0) / density
        set_bucket_volume(i, max(0.0, round(bucket_volume(i) - used_ml, 2)))
    save_settings(cartridge_config)


def hardness_group_value(group):
    """Return the configured hardness for the small or big hardness group."""
    for bucket in cartridge_config["buckets"].values():
        if bucket["hardness_group"] == group:
            return bucket["hardness"]
    raise ValueError(f"No bucket configured for hardness group {group!r}.")


def hardness_group_values():
    """Return the configured hardness values for small and big hardness groups."""
    return hardness_group_value("small"), hardness_group_value("big")


def pair_hardnesses():
    """Compatibility wrapper for older code; returns small and big hardness."""
    return hardness_group_values()


def hardness_limits():
    """Return the selectable min and max hardness from the saved JSON state."""
    small_hardness, big_hardness = hardness_group_values()
    return int(min(small_hardness, big_hardness)), int(max(small_hardness, big_hardness))


def hardness_to_ratio(target_shore):
    """Convert target shore hardness to fraction of big-hardness buckets in the mix."""
    if target_shore <= HARDNESS_CURVE[0][0]:
        return HARDNESS_CURVE[0][1]
    if target_shore >= HARDNESS_CURVE[-1][0]:
        return HARDNESS_CURVE[-1][1]

    for (x0, r0), (x1, r1) in zip(HARDNESS_CURVE, HARDNESS_CURVE[1:]):
        if x0 <= target_shore <= x1:
            return r0 + (r1 - r0) * (target_shore - x0) / (x1 - x0)

    return 1.0


def bucket_amounts_for_hardness(total_weight, target_shore):
    """Return bucket 1..4 gram amounts for a total weight and target hardness."""
    ratio_high = hardness_to_ratio(target_shore)
    weight_high = total_weight * ratio_high
    weight_low = total_weight - weight_high

    amounts = [0, 0, 0, 0]
    for bucket_key in SMALL_HARDNESS_BUCKETS:
        amounts[BUCKET_KEYS.index(bucket_key)] = weight_low / len(SMALL_HARDNESS_BUCKETS)
    for bucket_key in BIG_HARDNESS_BUCKETS:
        amounts[BUCKET_KEYS.index(bucket_key)] = weight_high / len(BIG_HARDNESS_BUCKETS)
    return amounts


def component_amounts_for_hardness(total_weight, target_shore):
    """Compatibility wrapper for older code; returns bucket 1..4 gram amounts."""
    return bucket_amounts_for_hardness(total_weight, target_shore)


cartridge_config = load_cartridge_config()
