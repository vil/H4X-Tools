"""
Copyright (c) 2023-2026. Vili and contributors.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
import os
from pathlib import Path
from typing import Any

from helper import printer

BASE = "h4x-tools"
CONFIG_FILENAME = "config.json"


def get_config_dir() -> Path:
    """
    Return the H4X-Tools config directory.

    Uses the XDG base directory convention when ``XDG_CONFIG_HOME`` is set,
    otherwise falls back to ``$HOME/.config/h4x-tools``.

    :return: Config directory path.
    """
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    base_dir = (
        Path(xdg_config_home).expanduser()
        if xdg_config_home
        else Path.home() / ".config"
    )
    return base_dir / BASE


def get_config_file() -> Path:
    """
    Return the H4X-Tools JSON config file path.

    :return: Config file path.
    """
    return get_config_dir() / CONFIG_FILENAME


def init_config() -> Path | None:
    """
    Ensure the config directory and JSON config file exist.

    The directory is created with owner-only permissions where the platform
    supports it. The file starts as an empty JSON object.

    :return: Config file path, or ``None`` if initialization fails.
    """
    config_dir = get_config_dir()
    config_file = get_config_file()

    try:
        config_dir.mkdir(parents=True, exist_ok=True)
        try:
            config_dir.chmod(0o700)
        except OSError:
            pass

        if not config_file.exists():
            config_file.write_text("{}\n", encoding="utf-8")
            try:
                config_file.chmod(0o600)
            except OSError:
                pass

        return config_file
    except OSError as exc:
        printer.warning(f"Could not initialize config path {config_dir}: {exc}")
        return None


def load_config() -> dict[str, Any]:
    """
    Load the H4X-Tools config JSON.

    Invalid or unreadable config files are treated as empty config so tools can
    still run without persistent settings.

    :return: Parsed config dictionary.
    """
    config_file = init_config()
    if config_file is None:
        return {}

    try:
        data = json.loads(config_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        printer.warning(f"Config file is invalid JSON ({exc}); ignoring saved config.")
        return {}
    except OSError as exc:
        printer.warning(f"Could not read config file {config_file}: {exc}")
        return {}

    return data if isinstance(data, dict) else {}


def save_config(data: dict[str, Any]) -> bool:
    """
    Save the H4X-Tools config JSON.

    :param data: Config data to persist.
    :return: ``True`` when saved successfully, otherwise ``False``.
    """
    config_file = init_config()
    if config_file is None:
        return False

    try:
        config_file.write_text(
            json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        try:
            config_file.chmod(0o600)
        except OSError:
            pass
        return True
    except OSError as exc:
        printer.warning(f"Could not write config file {config_file}: {exc}")
        return False


def get_value(section: str, key: str, default: Any = None) -> Any:
    """
    Read a config value from a named section.

    :param section: Top-level config section.
    :param key: Key inside the section.
    :param default: Value returned when missing.
    :return: Stored value or default.
    """
    data = load_config()
    section_data = data.get(section, {})
    if not isinstance(section_data, dict):
        return default
    return section_data.get(key, default)


def set_value(section: str, key: str, value: Any) -> bool:
    """
    Store a config value in a named section.

    :param section: Top-level config section.
    :param key: Key inside the section.
    :param value: JSON-serializable value to store.
    :return: ``True`` when saved successfully, otherwise ``False``.
    """
    data = load_config()
    section_data = data.get(section)
    if not isinstance(section_data, dict):
        section_data = {}
        data[section] = section_data

    section_data[key] = value
    return save_config(data)


def delete_value(section: str, key: str) -> bool:
    """
    Delete a config value from a named section.

    Empty sections are kept to avoid surprising rewrites of unrelated config.

    :param section: Top-level config section.
    :param key: Key inside the section.
    :return: ``True`` when saved successfully or key was absent.
    """
    data = load_config()
    section_data = data.get(section)
    if not isinstance(section_data, dict) or key not in section_data:
        return True

    del section_data[key]
    return save_config(data)
