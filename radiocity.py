#!/usr/bin/env python3
import json
import logging
import os
import signal
import socket
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path
import shutil
import ssl
import uuid
import warnings
import webbrowser
import ctypes
import ctypes.util

try:
    import certifi
except ImportError:
    certifi = None

os.environ.pop("GDK_PIXBUF_MODULEDIR", None)
os.environ.pop("GDK_PIXBUF_MODULE_FILE", None)

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, Pango, PangoCairo

APP_NAME = "Clarionet"
APP_VERSION = "0.2.1"
ASSETS_DIR = Path(__file__).resolve().parent / "assets"
CONFIG_DIR = Path.home() / ".config" / "clarionet"
RADIOS_PATH = CONFIG_DIR / "radios.json"
CONFIG_PATH = CONFIG_DIR / "config.json"
MPV_SOCKET = CONFIG_DIR / "mpv.sock"
ICONS_DIR = CONFIG_DIR / "icons"
LOG_PATH = CONFIG_DIR / "clarionet.log"
MPV_LOG_PATH = CONFIG_DIR / "clarionet-mpv.log"
STATE_IDLE = "idle"
STATE_LOADING = "loading"
STATE_PLAYING = "playing"
STATE_PAUSED = "paused"
STATE_ERROR = "error"
VOLUME_STEP = 1
DIGITAL_FONT_PATH = (
    ASSETS_DIR
    / "fonts"
    / "digital-readout"
    / "TrueType"
    / "SFDigitalReadout-Medium.ttf"
)
DIGITAL_FONT_FAMILY = "SF Digital Readout"

CONFIG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    filename=str(LOG_PATH),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

warnings.filterwarnings(
    "ignore",
    message=".*StatusIcon.*deprecated.*",
    category=DeprecationWarning,
)
warnings.filterwarnings(
    "ignore",
    message=".*set_wmclass.*deprecated.*",
    category=DeprecationWarning,
)

DEFAULT_RADIOS = [
    {
        "id": str(uuid.uuid4()),
        "name": "FIP",
        "stream_url": "https://stream.radiofrance.fr/fip/fip_hifi.m3u8",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "France Inter",
        "stream_url": "https://stream.radiofrance.fr/franceinter/franceinter_hifi.m3u8",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "France Culture",
        "stream_url": "https://stream.radiofrance.fr/franceculture/franceculture_hifi.m3u8",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "SomaFM Groove Salad",
        "stream_url": "https://ice1.somafm.com/groovesalad-128-mp3",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "SomaFM Drone Zone",
        "stream_url": "https://ice1.somafm.com/dronezone-128-mp3",
    },
]


def load_json(path, default):
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def save_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, sort_keys=True)


def normalize_radios(radios):
    normalized = []
    changed = False
    seen = set()
    for radio in radios:
        name = (radio.get("name") or "").strip()
        stream_url = (radio.get("stream_url") or radio.get("url") or "").strip()
        radio_id = radio.get("id")
        homepage = (radio.get("homepage") or "").strip() or None
        favicon = (radio.get("favicon") or "").strip() or None
        if not radio_id:
            radio_id = str(uuid.uuid4())
            changed = True
        if not name or not stream_url:
            changed = True
            continue
        key = (name.lower(), stream_url)
        if key in seen:
            changed = True
            continue
        seen.add(key)
        if "stream_url" not in radio or "url" in radio:
            changed = True
        entry = {"id": radio_id, "name": name, "stream_url": stream_url}
        if homepage:
            entry["homepage"] = homepage
        if favicon:
            entry["favicon"] = favicon
        normalized.append(entry)
    return normalized, changed


def normalize_config(config, radios):
    changed = False
    last_radio_id = config.get("last_radio_id")
    last_radio = config.get("last_radio")
    if not last_radio_id and last_radio:
        for radio in radios:
            if radio["name"] == last_radio:
                last_radio_id = radio["id"]
                changed = True
                break
    if last_radio_id and not any(radio["id"] == last_radio_id for radio in radios):
        last_radio_id = None
        changed = True
    volume = config.get("volume", 50)
    presets = config.get("presets")
    if presets is None:
        presets = [None] * 6
        changed = True
    else:
        cleaned = []
        for preset_id in presets[:6]:
            if preset_id and not any(radio["id"] == preset_id for radio in radios):
                cleaned.append(None)
                changed = True
            else:
                cleaned.append(preset_id)
        if len(cleaned) < 6:
            cleaned.extend([None] * (6 - len(cleaned)))
            changed = True
        presets = cleaned
    radios_payload = [dict(radio) for radio in radios]
    if config.get("radios") != radios_payload:
        changed = True
    if "last_radio" in config:
        changed = True
    return {
        "volume": volume,
        "last_radio_id": last_radio_id,
        "presets": presets,
        "radios": radios_payload,
    }, changed


def register_font(font_path):
    if not font_path.exists():
        logger.warning("Font not found: %s", font_path)
        return False
    lib_name = ctypes.util.find_library("fontconfig")
    if not lib_name:
        logger.warning("fontconfig library not found")
        return False
    try:
        fontconfig = ctypes.CDLL(lib_name)
        fontconfig.FcConfigGetCurrent.restype = ctypes.c_void_p
        fontconfig.FcConfigAppFontAddFile.argtypes = [ctypes.c_void_p, ctypes.c_char_p]
        fontconfig.FcConfigAppFontAddFile.restype = ctypes.c_int
        config = fontconfig.FcConfigGetCurrent()
        if not config:
            logger.warning("fontconfig config not available")
            return False
        result = fontconfig.FcConfigAppFontAddFile(
            config, str(font_path).encode("utf-8")
        )
        if result == 0:
            logger.warning("Failed to register font: %s", font_path)
            return False
        return True
    except Exception as exc:
        logger.warning("Font registration error: %s", exc)
        return False


def favicon_cache_path(url):
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    if not host:
        return None
    safe_host = "".join(ch if ch.isalnum() or ch in ("-", ".") else "_" for ch in host)
    return ICONS_DIR / f"{safe_host}.ico"


def build_ssl_context():
    if certifi:
        return ssl.create_default_context(cafile=certifi.where())
    return ssl.create_default_context()


def open_url(request, timeout, max_bytes=None, allow_insecure=False):
    context = build_ssl_context()
    try:
        with urllib.request.urlopen(
            request, timeout=timeout, context=context
        ) as response:
            data = response.read(max_bytes + 1) if max_bytes else response.read()
    except ssl.SSLError:
        if not allow_insecure:
            raise
        insecure_context = ssl._create_unverified_context()
        with urllib.request.urlopen(
            request, timeout=timeout, context=insecure_context
        ) as response:
            data = response.read(max_bytes + 1) if max_bytes else response.read()
        return data, True
    return data, False


def favicon_url(url):
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname
    if not host:
        return None
    scheme = parsed.scheme if parsed.scheme in ("http", "https") else "https"
    return f"{scheme}://{host}/favicon.ico"


class MpvController:
    def __init__(self, socket_path):
        self.socket_path = socket_path
        self.process = None
        self.listener_thread = None
        self.listener_lock = threading.Lock()
        self.stop_event = threading.Event()

    def _ensure_process(self):
        if self.process and self.process.poll() is None:
            return
        if self.socket_path.exists():
            self.socket_path.unlink()
        cmd = [
            "mpv",
            "--no-terminal",
            "--idle=yes",
            f"--input-ipc-server={self.socket_path}",
            f"--log-file={MPV_LOG_PATH}",
            "--msg-level=all=warn",
        ]
        try:
            self.process = subprocess.Popen(cmd)
        except FileNotFoundError:
            raise RuntimeError("mpv n'est pas disponible sur ce systeme")

    def _send(self, command):
        self._ensure_process()
        message = json.dumps(command).encode("utf-8") + b"\n"
        last_error = None
        for _ in range(5):
            sock = socket.socket(socket.AF_UNIX)
            try:
                sock.connect(str(self.socket_path))
                sock.sendall(message)
                return
            except OSError as exc:
                last_error = exc
                time.sleep(0.1)
            finally:
                sock.close()
        if last_error:
            raise last_error

    def start_event_listener(self, callback):
        with self.listener_lock:
            if self.listener_thread and self.listener_thread.is_alive():
                return
            self.stop_event.clear()
            self.listener_thread = threading.Thread(
                target=self._listen_events, args=(callback,), daemon=True
            )
            self.listener_thread.start()

    def stop_event_listener(self):
        self.stop_event.set()

    def _listen_events(self, callback):
        while not self.stop_event.is_set():
            self._ensure_process()
            sock = None
            for _ in range(10):
                if self.stop_event.is_set():
                    return
                try:
                    sock = socket.socket(socket.AF_UNIX)
                    sock.connect(str(self.socket_path))
                    break
                except OSError:
                    if sock:
                        sock.close()
                    sock = None
                    time.sleep(0.2)
            if not sock:
                time.sleep(0.5)
                continue
            try:
                commands = [
                    {"command": ["observe_property", 1, "pause"]},
                    {"command": ["observe_property", 2, "idle-active"]},
                    {"command": ["observe_property", 3, "media-title"]},
                ]

                for command in commands:
                    sock.sendall(json.dumps(command).encode("utf-8") + b"\n")
                buffer = b""
                while not self.stop_event.is_set():
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    buffer += chunk
                    while b"\n" in buffer:
                        line, buffer = buffer.split(b"\n", 1)
                        if not line:
                            continue
                        try:
                            payload = json.loads(line.decode("utf-8"))
                        except json.JSONDecodeError:
                            continue
                        callback(payload)
            finally:
                if sock:
                    sock.close()
            time.sleep(0.2)

    def play(self, url):
        self._send({"command": ["loadfile", url, "replace"]})

    def stop(self):
        self._send({"command": ["stop"]})

    def pause(self, paused):
        self._send({"command": ["set_property", "pause", paused]})

    def set_volume(self, volume):
        self._send({"command": ["set_property", "volume", volume]})

    def quit(self):
        self.stop_event_listener()
        if not self.process or self.process.poll() is not None:
            return
        try:
            self._send({"command": ["quit"]})
        except OSError:
            pass
        try:
            self.process.wait(timeout=1)
        except Exception:
            self.process.send_signal(signal.SIGTERM)


class RadioRow(Gtk.ListBoxRow):
    def __init__(self, radio_id, name, stream_url, homepage=None, favicon=None):
        super().__init__()
        self.radio_id = radio_id
        self.name = name
        self.stream_url = stream_url
        self.homepage = homepage
        self.favicon_url = favicon
        self.icon = Gtk.Image.new_from_icon_name("audio-x-generic", Gtk.IconSize.MENU)
        label = Gtk.Label(label=name, xalign=0)

        box = Gtk.Box(spacing=8)
        box.pack_start(self.icon, False, False, 0)
        box.pack_start(label, True, True, 0)
        box.set_margin_start(8)
        box.set_margin_end(8)
        box.set_margin_top(6)
        box.set_margin_bottom(6)
        self.add(box)

    def set_icon_from_file(self, path):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(path), 16, 16, True)
        except Exception:
            return
        self.icon.set_from_pixbuf(pixbuf)


class ClarionetApp(Gtk.ApplicationWindow):
    def __init__(self, application):
        super().__init__(title=f"{APP_NAME} {APP_VERSION}", application=application)
        self.base_title = f"{APP_NAME} {APP_VERSION}"
        self.set_wmclass("clarionet", "Clarionet")
        self.set_icon_name("clarionet")
        self.fixed_width = 640
        self.fixed_height = 395
        self.set_default_size(self.fixed_width, self.fixed_height)
        self.set_size_request(self.fixed_width, self.fixed_height)
        self.set_resizable(False)
        geometry = Gdk.Geometry()
        geometry.min_width = self.fixed_width
        geometry.min_height = self.fixed_height
        geometry.max_width = self.fixed_width
        geometry.max_height = self.fixed_height
        self.set_geometry_hints(
            self,
            geometry,
            Gdk.WindowHints.MIN_SIZE | Gdk.WindowHints.MAX_SIZE,
        )
        self.set_border_width(16)

        self._set_window_icons()
        icon_path = ASSETS_DIR / "icons" / "clarionet_icon_32x32.png"
        icon_pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(
            str(icon_path), 28, 28, True
        )
        self.header_icon = Gtk.Image.new_from_pixbuf(icon_pixbuf)
        self.state_label = Gtk.Label(label=STATE_IDLE, xalign=0)
        self.current_label = Gtk.Label(label="-", xalign=0.5)
        self.current_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.display_char_limit = 24
        self.current_label.set_max_width_chars(self.display_char_limit)
        self.track_label = Gtk.Label(label="-", xalign=0.5)
        self.track_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.track_label.set_max_width_chars(self.display_char_limit)
        self.track_label.set_no_show_all(True)
        self.track_label.hide()
        self.marquee_tasks = {}
        self.easter_timer_id = None
        self.size_lock_id = None

        register_font(DIGITAL_FONT_PATH)
        self.get_style_context().add_class("app-window")

        self.mpv = MpvController(MPV_SOCKET)
        legacy_dir = Path.home() / ".config" / "radiocity"
        legacy_config = legacy_dir / "config.json"
        legacy_radios = legacy_dir / "radios.json"
        if not RADIOS_PATH.exists() and legacy_radios.exists():
            RADIOS_PATH.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(legacy_radios, RADIOS_PATH)
        if not RADIOS_PATH.exists():
            save_json(RADIOS_PATH, DEFAULT_RADIOS)
        radios_raw = load_json(RADIOS_PATH, DEFAULT_RADIOS)
        if legacy_radios.exists():
            legacy_radios_raw = load_json(legacy_radios, [])
            existing = {
                (
                    (radio.get("name") or "").strip().lower(),
                    (radio.get("stream_url") or "").strip(),
                )
                for radio in radios_raw
            }
            for radio in legacy_radios_raw:
                key = (
                    (radio.get("name") or "").strip().lower(),
                    (radio.get("stream_url") or radio.get("url") or "").strip(),
                )
                if key not in existing:
                    radios_raw.append(radio)
                    existing.add(key)
        self.radios, radios_changed = normalize_radios(radios_raw)
        if radios_changed:
            save_json(RADIOS_PATH, self.radios)
        if not CONFIG_PATH.exists() and legacy_config.exists():
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(legacy_config, CONFIG_PATH)
        if not CONFIG_PATH.exists():
            save_json(
                CONFIG_PATH,
                {"volume": 50, "last_radio_id": None, "presets": [None] * 6},
            )
        config_raw = load_json(
            CONFIG_PATH,
            {"volume": 50, "last_radio_id": None, "presets": [None] * 6},
        )
        if legacy_config.exists():
            legacy_config_raw = load_json(legacy_config, {})
            legacy_presets = legacy_config_raw.get("presets") or []
            current_presets = config_raw.get("presets") or []
            if legacy_presets and not any(current_presets):
                config_raw["presets"] = legacy_presets
            if not config_raw.get("last_radio_id") and legacy_config_raw.get(
                "last_radio_id"
            ):
                config_raw["last_radio_id"] = legacy_config_raw.get("last_radio_id")
        self.config, config_changed = normalize_config(config_raw, self.radios)
        if config_changed:
            save_json(CONFIG_PATH, self.config)
        self.favicon_tasks = set()
        self.volume_save_id = None
        self.pause_blink_id = None
        self.play_blink_id = None
        self.state = STATE_IDLE
        self.playing_id = None
        self.playing_name = None
        self.selected_row = None

        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.listbox.set_sort_func(self.sort_rows)
        self.listbox.connect("row-selected", self.on_row_selected)
        self.listbox.connect("row-activated", self.on_row_activated)
        self.listbox.connect("button-release-event", self.on_list_click)
        self.listbox.connect("key-press-event", self.on_list_key_press)
        self.connect("key-press-event", self.on_window_key_press)
        self.key_return, _ = Gtk.accelerator_parse("Return")
        self.key_kp_enter, _ = Gtk.accelerator_parse("KP_Enter")

        for radio in self.radios:
            row = RadioRow(
                radio["id"],
                radio["name"],
                radio["stream_url"],
                homepage=radio.get("homepage"),
                favicon=radio.get("favicon"),
            )
            self.listbox.add(row)
            self.load_favicon_async(row)
        self.listbox.show_all()

        self.station_prev_button = Gtk.Button()
        self.station_next_button = Gtk.Button()
        self.station_prev_button.set_image(
            Gtk.Image.new_from_icon_name("go-previous-symbolic", Gtk.IconSize.BUTTON)
        )
        self.station_next_button.set_image(
            Gtk.Image.new_from_icon_name("go-next-symbolic", Gtk.IconSize.BUTTON)
        )
        self.station_prev_button.set_always_show_image(True)
        self.station_next_button.set_always_show_image(True)
        self.station_prev_button.connect("clicked", self.on_station_prev)
        self.station_next_button.connect("clicked", self.on_station_next)

        self.station_display = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.station_display.set_hexpand(True)
        self.station_display.set_halign(Gtk.Align.FILL)
        self.station_display.pack_start(self.current_label, True, True, 0)
        self.station_display.pack_start(self.track_label, True, True, 0)
        self.station_display.get_style_context().add_class("now-playing-box")

        self.play_button = Gtk.Button()
        self.pause_button = Gtk.Button()
        self.stop_button = Gtk.Button()
        self.play_button.set_image(
            Gtk.Image.new_from_icon_name(
                "media-playback-start-symbolic", Gtk.IconSize.BUTTON
            )
        )
        self.pause_button.set_image(
            Gtk.Image.new_from_icon_name(
                "media-playback-pause-symbolic", Gtk.IconSize.BUTTON
            )
        )
        self.stop_button.set_image(
            Gtk.Image.new_from_icon_name(
                "media-playback-stop-symbolic", Gtk.IconSize.BUTTON
            )
        )
        for button in (self.play_button, self.pause_button, self.stop_button):
            button.set_always_show_image(True)
        self.play_button.get_style_context().add_class("control-play")
        self.pause_button.get_style_context().add_class("control-pause")
        self.stop_button.get_style_context().add_class("control-stop")
        self.play_button.connect("clicked", self.on_play)
        self.pause_button.connect("clicked", self.on_pause)
        self.stop_button.connect("clicked", self.on_stop)

        volume_adjustment = Gtk.Adjustment(
            value=self.config.get("volume", 50),
            lower=0,
            upper=100,
            step_increment=1,
            page_increment=5,
        )
        self.volume_scale = Gtk.Scale(
            orientation=Gtk.Orientation.HORIZONTAL, adjustment=volume_adjustment
        )
        self.volume_scale.set_digits(0)
        self.volume_scale.set_draw_value(False)
        self.volume_scale.set_visible(False)
        self.volume_scale.connect("value-changed", self.on_volume_changed)

        self.volume_minus_button = Gtk.Button()
        self.volume_plus_button = Gtk.Button()
        self.volume_repeat_id = None
        self.volume_repeat_delta = 0
        self.volume_minus_button.set_image(
            Gtk.Image.new_from_icon_name("pan-down-symbolic", Gtk.IconSize.BUTTON)
        )
        self.volume_plus_button.set_image(
            Gtk.Image.new_from_icon_name("pan-up-symbolic", Gtk.IconSize.BUTTON)
        )
        self.volume_minus_button.set_always_show_image(True)
        self.volume_plus_button.set_always_show_image(True)
        self.volume_value_label = Gtk.Label(
            label=str(int(self.volume_scale.get_value())), xalign=0
        )
        self.volume_value_label.get_style_context().add_class("volume-value")
        self.volume_value_label.get_style_context().add_class("volume-accent")
        self.volume_minus_button.get_style_context().add_class("volume-step")
        self.volume_plus_button.get_style_context().add_class("volume-step")
        self.volume_minus_button.connect("clicked", self.on_volume_step, -VOLUME_STEP)
        self.volume_plus_button.connect("clicked", self.on_volume_step, VOLUME_STEP)
        self.volume_minus_button.connect("pressed", self.on_volume_press, -VOLUME_STEP)
        self.volume_minus_button.connect("released", self.on_volume_release)
        self.volume_plus_button.connect("pressed", self.on_volume_press, VOLUME_STEP)
        self.volume_plus_button.connect("released", self.on_volume_release)

        controls_box = Gtk.Box(spacing=8)
        controls_box.pack_start(self.station_prev_button, False, False, 0)
        controls_box.pack_start(self.play_button, False, False, 0)
        controls_box.pack_start(self.pause_button, False, False, 0)
        controls_box.pack_start(self.stop_button, False, False, 0)
        controls_box.pack_start(self.station_next_button, False, False, 0)
        controls_box.get_style_context().add_class("controls-box")

        self.current_label.set_hexpand(True)
        self.current_label.set_halign(Gtk.Align.FILL)

        self.preset_box = Gtk.Box(spacing=8)
        self.preset_buttons = []
        self.preset_timers = {}
        self.preset_saved = set()
        self.preset_css_provider = Gtk.CssProvider()
        self.preset_css_provider.load_from_data(
            b"""
            .preset-button { background-color: #000000; }
            .preset-button:active { background-color: #111111; }
            """
        )
        screen = Gdk.Screen.get_default()
        if screen:
            Gtk.StyleContext.add_provider_for_screen(
                screen,
                self.preset_css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_USER + 1,
            )
        for index, label in enumerate(("1", "2", "3", "4", "5", "6")):
            button = Gtk.Button()
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.get_style_context().add_class("preset-button")
            button.get_style_context().add_provider(
                self.preset_css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            drawing = Gtk.DrawingArea()
            drawing.set_hexpand(True)
            drawing.set_vexpand(True)
            drawing.connect("draw", self.on_preset_draw, index)
            button.add(drawing)
            button.connect("pressed", self.on_preset_pressed, index)
            button.connect("released", self.on_preset_released, index)
            self.preset_buttons.append(
                {"button": button, "drawing": drawing, "text": label, "active": False}
            )
            self.preset_box.pack_start(button, True, True, 0)
        self.add_station_button = self._build_add_station_button()
        self.add_station_button.get_style_context().add_provider(
            self.preset_css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
        self.preset_box.pack_start(self.add_station_button, False, False, 0)
        self.preset_box.get_style_context().add_class("preset-box")

        volume_box = Gtk.Box(spacing=8)
        self.volume_icon = Gtk.Image.new_from_icon_name(
            "audio-volume-high-symbolic", Gtk.IconSize.BUTTON
        )
        self.volume_icon.add_events(
            Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK
        )
        self.volume_icon.connect("button-press-event", self.on_easter_press)
        self.volume_icon.connect("button-release-event", self.on_easter_release)
        volume_box.pack_start(self.volume_icon, False, False, 0)
        volume_box.pack_start(self.volume_value_label, False, False, 0)
        volume_box.pack_start(self.volume_minus_button, False, False, 0)
        volume_box.pack_start(self.volume_plus_button, False, False, 0)
        volume_box.set_halign(Gtk.Align.END)

        body_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        body_box.pack_start(self.preset_box, False, False, 0)
        body_box.pack_start(self.station_display, False, False, 0)

        footer_box = Gtk.Box(spacing=16)
        footer_box.set_size_request(-1, 56)
        footer_box.set_margin_top(8)
        footer_box.set_hexpand(True)
        footer_box.pack_start(controls_box, False, False, 0)
        footer_box.pack_start(volume_box, True, True, 0)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        main_box.pack_start(body_box, True, True, 0)
        main_box.pack_start(footer_box, False, False, 0)

        self.add(main_box)

        footer_box.get_style_context().add_class("footer")
        self.current_label.get_style_context().add_class("now-playing")
        self.track_label.get_style_context().add_class("now-playing")
        self.connect("delete-event", self.on_delete_event)

        self.tray = self._build_tray()
        self._install_shortcuts()
        self._install_list_styles()
        self.mpv.start_event_listener(self.handle_mpv_event)
        self.connect("size-allocate", self.enforce_fixed_size)
        self.connect("map-event", self.on_map_event)
        self.connect("realize", self.on_realize)

        self.restore_selection()
        self.refresh_preset_labels()
        self.update_preset_styles()
        self.set_state(STATE_IDLE)
        self.update_control_styles()
        self.station_display.connect("size-allocate", self.on_display_resize)

    def _set_window_icons(self):
        icon_dir = ASSETS_DIR / "icons"
        icon_sizes = [16, 24, 32, 48, 64, 96, 128, 256, 512]
        pixbufs = []
        for size in icon_sizes:
            path = icon_dir / f"clarionet_icon_{size}x{size}.png"
            if not path.exists():
                continue
            try:
                pixbufs.append(GdkPixbuf.Pixbuf.new_from_file(str(path)))
            except Exception:
                continue
        if pixbufs:
            self.set_icon_list(pixbufs)

    def _build_tray(self):
        icon_path = ASSETS_DIR / "icons" / "clarionet_icon_32x32.png"
        try:
            if icon_path.exists():
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(icon_path))
                tray = Gtk.StatusIcon.new_from_pixbuf(pixbuf)
            else:
                tray = Gtk.StatusIcon.new_from_icon_name("clarionet")
        except Exception as exc:
            logger.warning("Tray icon unavailable: %s", exc)
            return None
        if not tray:
            logger.warning("Tray icon unavailable")
            return None
        tray.set_tooltip_text(f"{APP_NAME} {APP_VERSION}")
        tray.connect("activate", self.on_tray_activate)
        tray.connect("popup-menu", self.on_tray_menu)
        return tray

    def _build_add_station_button(self):
        menu = Gtk.Menu()

        add_stream_item = Gtk.MenuItem(label="Ajouter une radio")
        add_browser_item = Gtk.MenuItem(label="Importer Radio-Browser")

        add_stream_item.connect("activate", lambda *_: self.on_add(None))
        add_browser_item.connect("activate", lambda *_: self.on_add_browser())

        menu.append(add_stream_item)
        menu.append(add_browser_item)
        menu.show_all()

        button = Gtk.MenuButton()
        button.set_image(
            Gtk.Image.new_from_icon_name("list-add-symbolic", Gtk.IconSize.BUTTON)
        )
        button.set_popup(menu)
        button.get_style_context().add_class("preset-button")
        button.get_style_context().add_class("preset-add")
        return button

    def _install_shortcuts(self):
        accel_group = Gtk.AccelGroup()
        self.add_accel_group(accel_group)
        for widget, combo in (
            (self.play_button, "space"),
            (self.stop_button, "s"),
        ):
            keyval, modifier = Gtk.accelerator_parse(combo)
            widget.add_accelerator(
                "clicked", accel_group, keyval, modifier, Gtk.AccelFlags.VISIBLE
            )
        for callback, combo in (
            (lambda *_: self.on_add(None), "<Control>n"),
            (lambda *_: self.quit_app(), "<Control>q"),
        ):
            keyval, modifier = Gtk.accelerator_parse(combo)
            accel_group.connect(keyval, modifier, Gtk.AccelFlags.VISIBLE, callback)

    def restore_selection(self):
        last_radio_id = self.config.get("last_radio_id")
        rows = self.get_sorted_rows()
        if last_radio_id:
            for row in rows:
                if row.radio_id == last_radio_id:
                    self.listbox.select_row(row)
                    self.on_row_selected(None, row)
                    return
        if rows:
            self.listbox.select_row(rows[0])
            self.on_row_selected(None, rows[0])

    def sort_rows(self, row1, row2):
        name1 = row1.name.lower()
        name2 = row2.name.lower()
        if name1 < name2:
            return -1
        if name1 > name2:
            return 1
        return 0

    def set_state(self, state):
        self.state = state
        if state in (STATE_IDLE, STATE_ERROR):
            self.playing_id = None
            self.playing_name = None
            self.track_label.set_text("-")
            self.track_label.hide()
            self.update_marquee(self.track_label)
            if state == STATE_IDLE and self.selected_row:
                self.current_label.set_text(self.selected_row.name)
                self.update_marquee(self.current_label)
        self.update_preset_styles()
        self.state_label.set_text(state)
        self.set_title(f"{self.base_title} — {state}")
        if state == STATE_PAUSED:
            self.pause_button.set_tooltip_text("Reprendre")
        else:
            self.pause_button.set_tooltip_text("Pause")
        self.update_control_styles()
        self.refresh_row_styles()

    def update_control_styles(self):
        play_context = self.play_button.get_style_context()
        pause_context = self.pause_button.get_style_context()
        stop_context = self.stop_button.get_style_context()
        play_context.remove_class("is-active")
        pause_context.remove_class("is-active")
        stop_context.remove_class("is-active")
        stop_context.remove_class("is-stop")
        if self.state == STATE_PLAYING:
            play_context.add_class("is-active")
            self.stop_play_blink()
            self.stop_pause_blink()
        elif self.state == STATE_LOADING:
            self.start_play_blink()
            self.stop_pause_blink()
        elif self.state == STATE_PAUSED:
            pause_context.add_class("is-active")
            self.start_pause_blink()
            self.stop_play_blink()
        elif self.state == STATE_IDLE:
            stop_context.add_class("is-stop")
            self.stop_play_blink()
            self.stop_pause_blink()
        else:
            self.stop_play_blink()
            self.stop_pause_blink()

    def start_pause_blink(self):
        if self.pause_blink_id is not None:
            return

        def toggle():
            context = self.pause_button.get_style_context()
            if context.has_class("blink"):
                context.remove_class("blink")
            else:
                context.add_class("blink")
            return True

        self.pause_blink_id = GLib.timeout_add(500, toggle)

    def stop_pause_blink(self):
        if self.pause_blink_id is None:
            return
        GLib.source_remove(self.pause_blink_id)
        self.pause_blink_id = None
        self.pause_button.get_style_context().remove_class("blink")

    def start_play_blink(self):
        if self.play_blink_id is not None:
            return

        def toggle():
            context = self.play_button.get_style_context()
            if context.has_class("blink"):
                context.remove_class("blink")
            else:
                context.add_class("blink")
            return True

        self.play_blink_id = GLib.timeout_add(500, toggle)

    def stop_play_blink(self):
        if self.play_blink_id is None:
            return
        GLib.source_remove(self.play_blink_id)
        self.play_blink_id = None
        self.play_button.get_style_context().remove_class("blink")

    def handle_mpv_event(self, payload):
        event = payload.get("event")
        if event == "start-file":
            GLib.idle_add(self.set_state, STATE_LOADING)
            return
        if event in ("file-loaded", "playback-restart"):
            GLib.idle_add(self.set_state, STATE_PLAYING)
            return
        if event == "end-file":
            reason = payload.get("reason")
            if reason == "error":
                logger.error("Playback error")
                GLib.idle_add(self.set_state, STATE_ERROR)
            else:
                GLib.idle_add(self.set_state, STATE_IDLE)
            return
        if event == "shutdown":
            GLib.idle_add(self.set_state, STATE_IDLE)
            return
        if event == "property-change":
            if payload.get("name") == "pause":
                paused = payload.get("data")
                GLib.idle_add(
                    self.set_state,
                    STATE_PAUSED if paused else STATE_PLAYING,
                )
                return
            if payload.get("name") == "idle-active" and payload.get("data"):
                GLib.idle_add(self.set_state, STATE_IDLE)
                return
            if payload.get("name") == "media-title":
                title = (payload.get("data") or "").strip()
                if title:
                    GLib.idle_add(self.track_label.set_text, title)
                    GLib.idle_add(self.track_label.show)
                    GLib.idle_add(self.schedule_marquee_now, self.track_label, title)
                else:
                    GLib.idle_add(self.track_label.hide)
                    GLib.idle_add(self.track_label.set_text, "-")
                GLib.idle_add(self.update_marquee, self.track_label)

    def on_window_key_press(self, _, event):
        if event.keyval == Gdk.KEY_Left:
            self.adjust_volume(-VOLUME_STEP)
            return True
        if event.keyval == Gdk.KEY_Right:
            self.adjust_volume(VOLUME_STEP)
            return True
        if event.keyval == Gdk.KEY_Up:
            self.move_selection(-1)
            return True
        if event.keyval == Gdk.KEY_Down:
            self.move_selection(1)
            return True
        return False

    def adjust_volume(self, delta):
        value = int(self.volume_scale.get_value()) + delta
        value = max(0, min(100, value))
        self.volume_scale.set_value(value)

    def move_selection(self, offset):
        rows = self.get_sorted_rows()
        if not rows:
            return
        current = self.listbox.get_selected_row()
        if current in rows:
            index = rows.index(current)
        else:
            index = 0
        index = max(0, min(len(rows) - 1, index + offset))
        self.listbox.select_row(rows[index])

    def get_sorted_rows(self):
        rows = list(self.listbox.get_children())
        return sorted(rows, key=lambda row: row.name.lower())

    def on_station_next(self, *_):
        rows = self.get_sorted_rows()
        if not rows:
            return
        current = self.listbox.get_selected_row()
        if current in rows:
            index = rows.index(current)
            index = (index + 1) % len(rows)
        else:
            index = 0
        self.listbox.select_row(rows[index])
        self.on_row_selected(None, rows[index])

    def on_station_prev(self, *_):
        rows = self.get_sorted_rows()
        if not rows:
            return
        current = self.listbox.get_selected_row()
        if current in rows:
            index = rows.index(current)
            index = (index - 1) % len(rows)
        else:
            index = len(rows) - 1
        self.listbox.select_row(rows[index])
        self.on_row_selected(None, rows[index])

    def on_row_selected(self, _, row):
        if not row:
            return
        self.current_label.set_text(row.name)
        self.update_marquee(self.current_label)
        self.selected_row = row
        self.config["last_radio_id"] = row.radio_id
        save_json(CONFIG_PATH, self.config)
        self.refresh_row_styles()

    def on_display_resize(self, *_):
        self.update_marquee(self.current_label)
        self.update_marquee(self.track_label)

    def enforce_fixed_size(self, *_):
        self.resize(self.fixed_width, self.fixed_height)
        return False

    def on_map_event(self, *_):
        GLib.idle_add(self.resize, self.fixed_width, self.fixed_height)
        if self.size_lock_id is None:
            self.size_lock_id = GLib.timeout_add(250, self.ensure_size_locked)
        return False

    def on_realize(self, *_):
        window = self.get_window()
        if not window:
            return False
        window.set_functions(
            Gdk.WMFunction.MOVE | Gdk.WMFunction.MINIMIZE | Gdk.WMFunction.CLOSE
        )
        return False

    def ensure_size_locked(self):
        width, height = self.get_size()
        if width != self.fixed_width or height != self.fixed_height:
            self.resize(self.fixed_width, self.fixed_height)
        return True

    def on_easter_press(self, *_):
        if int(self.volume_scale.get_value()) != 21:
            return False
        if self.easter_timer_id is not None:
            GLib.source_remove(self.easter_timer_id)
        self.easter_timer_id = GLib.timeout_add(1500, self.open_easter_egg)
        return True

    def on_easter_release(self, *_):
        if self.easter_timer_id is not None:
            GLib.source_remove(self.easter_timer_id)
            self.easter_timer_id = None
        return True

    def open_easter_egg(self):
        self.easter_timer_id = None
        if int(self.volume_scale.get_value()) == 21:
            webbrowser.open("https://fr.wikipedia.org/wiki/Radio_Cit%C3%A9_(Bruxelles)")
        return False

    def on_preset_draw(self, widget, cr, index):
        entry = self.preset_buttons[index]
        alloc = widget.get_allocation()
        cr.set_source_rgb(0, 0, 0)
        cr.rectangle(0, 0, alloc.width, alloc.height)
        cr.fill()

        color = (0.0, 1.0, 0.4) if entry["active"] else (0.95, 0.95, 0.95)
        cr.set_source_rgb(*color)

        layout = widget.create_pango_layout(entry["text"])
        layout.set_ellipsize(Pango.EllipsizeMode.END)
        layout.set_alignment(Pango.Alignment.CENTER)
        layout.set_width(max(1, (alloc.width - 16)) * Pango.SCALE)
        font = Pango.FontDescription("Sans Bold 10")
        layout.set_font_description(font)

        text_width, text_height = layout.get_pixel_size()
        x = 0
        y = max(0, int((alloc.height - text_height) / 2))
        cr.move_to(x, y)
        PangoCairo.show_layout(cr, layout)

        return False

    def update_marquee(self, label):
        state = self.marquee_tasks.pop(label, None)
        if state:
            for key in ("start_id", "scroll_id"):
                task_id = state.get(key)
                if task_id:
                    GLib.source_remove(task_id)
        text = label.get_text() or ""
        if not text or text == "-":
            return
        if not self.label_overflows(label):
            return
        start_id = GLib.timeout_add(30000, self.start_marquee, label, text)
        self.marquee_tasks[label] = {"start_id": start_id, "text": text}

    def schedule_marquee_now(self, label, text):
        state = self.marquee_tasks.pop(label, None)
        if state:
            for key in ("start_id", "scroll_id"):
                task_id = state.get(key)
                if task_id:
                    GLib.source_remove(task_id)
        GLib.timeout_add(100, self.start_marquee_now, label, text)
        return False

    def start_marquee_now(self, label, text):
        if not self.label_overflows(label):
            return False
        self.start_marquee(label, text)
        return False

    def label_overflows(self, label):
        text = label.get_text() or ""
        if text == "-":
            return False
        layout = label.get_layout()
        if not layout:
            return len(text) > self.display_char_limit
        width, _ = layout.get_pixel_size()
        available = label.get_allocated_width()
        if available <= 0:
            return len(text) > self.display_char_limit
        return width > available or len(text) > self.display_char_limit

    def start_marquee(self, label, text):
        if not self.label_overflows(label):
            return False
        gap = "   "
        padded = text + gap
        total = len(padded)
        state = {"offset": 0, "text": text, "padded": padded, "total": total}

        def tick():
            state["offset"] += 1
            if state["offset"] >= state["total"]:
                label.set_text(text)
                self.update_marquee(label)
                return False
            rotated = (
                state["padded"][state["offset"] :] + state["padded"][: state["offset"]]
            )
            label.set_text(rotated)
            return True

        scroll_id = GLib.timeout_add(120, tick)
        self.marquee_tasks[label] = {"scroll_id": scroll_id, "text": text}
        return False

    def refresh_preset_labels(self):
        presets = self.config.get("presets", [None] * 6)
        for index, entry in enumerate(self.preset_buttons):
            preset_id = presets[index] if index < len(presets) else None
            if preset_id:
                radio = next(
                    (item for item in self.radios if item["id"] == preset_id), None
                )
                entry["text"] = radio["name"] if radio else str(index + 1)
            else:
                entry["text"] = str(index + 1)
            entry["drawing"].queue_draw()
        self.update_preset_styles()

    def update_preset_styles(self):
        presets = self.config.get("presets", [None] * 6)
        active_id = self.playing_id
        if (
            not active_id
            and self.selected_row
            and self.state
            in (
                STATE_PLAYING,
                STATE_PAUSED,
                STATE_LOADING,
            )
        ):
            active_id = self.selected_row.radio_id
        for index, entry in enumerate(self.preset_buttons):
            preset_id = presets[index] if index < len(presets) else None
            entry["active"] = bool(preset_id and preset_id == active_id)
            entry["drawing"].queue_draw()

    def on_preset_pressed(self, _, index):
        if index in self.preset_timers:
            GLib.source_remove(self.preset_timers[index])
        self.preset_saved.discard(index)
        self.preset_timers[index] = GLib.timeout_add(600, self._save_preset, index)

    def on_preset_released(self, _, index):
        timer_id = self.preset_timers.pop(index, None)
        if timer_id:
            GLib.source_remove(timer_id)
        if index in self.preset_saved:
            self.preset_saved.discard(index)
            return
        self._recall_preset(index)

    def _save_preset(self, index):
        timer_id = self.preset_timers.pop(index, None)
        if timer_id:
            GLib.source_remove(timer_id)
        row = self.selected_row or self.listbox.get_selected_row()
        if not row:
            return False
        presets = self.config.get("presets", [None] * 6)
        presets[index] = row.radio_id
        self.config["presets"] = presets
        save_json(CONFIG_PATH, self.config)
        self.refresh_preset_labels()
        self.preset_saved.add(index)
        return False

    def _recall_preset(self, index):
        presets = self.config.get("presets", [None] * 6)
        if index >= len(presets):
            return
        preset_id = presets[index]
        if not preset_id:
            return
        for row in self.listbox.get_children():
            if row.radio_id == preset_id:
                self.listbox.select_row(row)
                self.on_row_selected(None, row)
                self.play_selected_row()
                return

    def on_row_activated(self, *_):
        self.play_selected_row()

    def on_list_click(self, _, event):
        if getattr(event, "button", None) == 1:
            self.play_selected_row()
        return False

    def on_list_key_press(self, _, event):
        if event.keyval in (self.key_return, self.key_kp_enter):
            self.play_selected_row()
            return True
        return False

    def play_selected_row(self):
        row = self.listbox.get_selected_row() or self.selected_row
        if not row:
            return
        if self.playing_id == row.radio_id and self.state == STATE_PLAYING:
            return
        self.on_play(None)

    def on_add(self, _):
        dialog = Gtk.Dialog(title="Ajouter une radio", parent=self, flags=0)
        dialog.add_button("Annuler", Gtk.ResponseType.CANCEL)
        dialog.add_button("Ajouter", Gtk.ResponseType.OK)

        content = dialog.get_content_area()
        name_entry = Gtk.Entry()
        url_entry = Gtk.Entry()
        name_entry.set_placeholder_text("Nom")
        url_entry.set_placeholder_text("URL du stream")
        content.add(Gtk.Label(label="Nom", xalign=0))
        content.add(name_entry)
        content.add(Gtk.Label(label="URL", xalign=0))
        content.add(url_entry)

        content.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            name = name_entry.get_text().strip()
            url = url_entry.get_text().strip()
            if name and url:
                self.add_radios([{"name": name, "stream_url": url}])
        dialog.destroy()

    def on_add_browser(self):
        dialog = Gtk.Dialog(title="Importer une radio", parent=self, flags=0)
        dialog.add_button("Annuler", Gtk.ResponseType.CANCEL)
        dialog.add_button("Ajouter", Gtk.ResponseType.OK)
        dialog.set_default_size(520, 480)

        content = dialog.get_content_area()
        content.add(Gtk.Label(label="Importer depuis Radio-Browser", xalign=0))

        search_box = Gtk.Box(spacing=8)
        search_entry = Gtk.Entry()
        search_entry.set_placeholder_text("Recherche par nom")
        search_button = Gtk.Button(label="Rechercher")
        search_box.pack_start(search_entry, True, True, 0)
        search_box.pack_start(search_button, False, False, 0)
        content.add(search_box)

        status_label = Gtk.Label(label="", xalign=0)
        content.add(status_label)

        results_box = Gtk.ListBox()
        results_box.set_selection_mode(Gtk.SelectionMode.NONE)
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_min_content_height(220)
        scrolled.add(results_box)
        content.add(scrolled)

        def clear_results():
            for child in results_box.get_children():
                results_box.remove(child)

        def populate_results(stations, warning=None):
            clear_results()
            count = 0
            for station in stations:
                name = station.get("name", "").strip()
                url = station.get("url_resolved") or station.get("url")
                if not name or not url:
                    continue
                country = station.get("country", "").strip()
                codec = station.get("codec", "").strip()
                bitrate = station.get("bitrate")
                details = []
                if codec:
                    details.append(codec.upper())
                if bitrate:
                    details.append(f"{bitrate} kbps")
                if station.get("hls"):
                    details.append("HLS")
                base_label = f"{name} ({country})" if country else name
                if details:
                    label = f"{base_label} — {' · '.join(details)}"
                else:
                    label = base_label
                check = Gtk.CheckButton(label=label)
                row = Gtk.ListBoxRow()
                row.station = {
                    "name": name,
                    "stream_url": url,
                    "homepage": station.get("homepage"),
                    "favicon": station.get("favicon"),
                }
                row.add(check)
                results_box.add(row)
                count += 1
                if count >= 25:
                    break
            results_box.show_all()
            if warning:
                status_label.set_text(f"{count} resultat(s) - {warning}")
            else:
                status_label.set_text(f"{count} resultat(s)")
            search_button.set_sensitive(True)

        def on_result(stations, warning=None):
            populate_results(stations, warning)
            return False

        def on_error(message):
            logger.error("Radio-Browser error: %s", message)
            status_label.set_text(f"Erreur: {message}")
            search_button.set_sensitive(True)
            return False

        def on_search_clicked(_):
            query = search_entry.get_text().strip()
            if not query:
                status_label.set_text("Saisir un nom")
                return
            status_label.set_text("Recherche en cours...")
            search_button.set_sensitive(False)
            self.fetch_radio_browser(query, on_result, on_error)

        search_button.connect("clicked", on_search_clicked)

        content.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            selected = []
            for row in results_box.get_children():
                check = row.get_child()
                if check.get_active():
                    selected.append(row.station)
            if selected:
                self.add_radios(selected)
        dialog.destroy()

    def on_remove(self, _):
        row = self.listbox.get_selected_row()
        if not row:
            return
        if row.radio_id == self.playing_id:
            self.on_stop(None)
            self.playing_id = None
            self.playing_name = None
        self.listbox.remove(row)
        self.radios = [radio for radio in self.radios if radio["id"] != row.radio_id]
        if self.config.get("last_radio_id") == row.radio_id:
            self.config["last_radio_id"] = None
            save_json(CONFIG_PATH, self.config)
        save_json(RADIOS_PATH, self.radios)
        self.current_label.set_text("-")
        self.refresh_row_styles()

    def on_play(self, _):
        row = self.listbox.get_selected_row()
        if not row:
            return
        try:
            self.mpv.play(row.stream_url)
            self.mpv.set_volume(100)
            self.set_system_volume(int(self.volume_scale.get_value()))
        except RuntimeError as exc:
            self.show_error(str(exc))
            return
        self.playing_id = row.radio_id
        self.playing_name = row.name
        self.track_label.set_text("-")
        self.update_preset_styles()
        logger.info("Play %s", row.name)
        logger.info("Stream URL %s", row.stream_url)

    def on_pause(self, _):
        if self.state not in (STATE_PLAYING, STATE_PAUSED):
            return
        target_paused = self.state != STATE_PAUSED
        try:
            self.mpv.pause(target_paused)
        except RuntimeError as exc:
            self.show_error(str(exc))
            return
        logger.info("Pause %s", target_paused)

    def on_stop(self, _):
        if self.state == STATE_IDLE:
            return
        try:
            self.mpv.stop()
        except RuntimeError as exc:
            self.show_error(str(exc))
            return
        logger.info("Stop")

    def on_volume_changed(self, scale):
        volume = int(scale.get_value())
        self.volume_value_label.set_text(str(volume))
        self.config["volume"] = volume
        if self.volume_save_id is not None:
            GLib.source_remove(self.volume_save_id)
        self.volume_save_id = GLib.timeout_add(400, self._save_config)
        self.set_system_volume(volume)
        if self.state in (STATE_PLAYING, STATE_PAUSED, STATE_LOADING):
            try:
                self.mpv.set_volume(100)
            except RuntimeError:
                return

    def on_volume_step(self, _, delta):
        value = int(self.volume_scale.get_value()) + delta
        value = max(0, min(100, value))
        self.volume_scale.set_value(value)

    def on_volume_press(self, _, delta):
        self.on_volume_step(None, delta)
        self.volume_repeat_delta = delta
        if self.volume_repeat_id is not None:
            GLib.source_remove(self.volume_repeat_id)
        self.volume_repeat_id = GLib.timeout_add(300, self._start_volume_repeat)

    def on_volume_release(self, *_):
        if self.volume_repeat_id is not None:
            GLib.source_remove(self.volume_repeat_id)
            self.volume_repeat_id = None

    def _start_volume_repeat(self):
        self.volume_repeat_id = GLib.timeout_add(80, self._repeat_volume_step)
        return False

    def _repeat_volume_step(self):
        self.on_volume_step(None, self.volume_repeat_delta)
        return True

    def set_system_volume(self, volume):
        if not shutil.which("pactl"):
            logger.warning("pactl not available")
            return
        try:
            subprocess.run(
                ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{volume}%"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except Exception as exc:
            logger.warning("System volume update failed: %s", exc)

    def _save_config(self):
        save_json(CONFIG_PATH, self.config)
        self.volume_save_id = None
        return False

    def on_tray_activate(self, _):
        if self.get_visible():
            self.hide()
        else:
            self.show_all()
            self.present()

    def on_tray_menu(self, _, button, time):
        menu = Gtk.Menu()
        show_item = Gtk.MenuItem(label="Afficher")
        about_item = Gtk.MenuItem(label="A propos")
        quit_item = Gtk.MenuItem(label="Quitter")
        show_item.connect("activate", lambda *_: self.show_all())
        about_item.connect("activate", lambda *_: self.show_about())
        quit_item.connect("activate", lambda *_: self.quit_app())
        menu.append(show_item)
        menu.append(about_item)
        menu.append(quit_item)
        menu.show_all()
        menu.popup(None, None, None, None, button, time)

    def show_about(self):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=f"{APP_NAME} {APP_VERSION}",
        )
        dialog.run()
        dialog.destroy()

        dialog.format_secondary_text(
            "Easter egg: https://fr.wikipedia.org/wiki/Radio_Cit%C3%A9_(Bruxelles)"
        )
        dialog.add_button("Radio Cité", Gtk.ResponseType.APPLY)
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.APPLY:
            webbrowser.open("https://fr.wikipedia.org/wiki/Radio_Cit%C3%A9_(Bruxelles)")

    def _install_list_styles(self):
        self.css_provider = Gtk.CssProvider()
        background_image = (ASSETS_DIR / "background.webp").as_posix()
        css = f"""
        .row-odd {{ background-color: #ffffff; }}
        .row-even {{ background-color: #f2f2f2; }}
        .row-selected {{ background-color: #1a1a1a; color: #f2f2f2; }}
        .row-selected label {{ color: #f2f2f2; }}
        .row-playing {{ background-color: #d9f2d9; }}
        .row-playing label {{ color: #111111; }}
        .row-selected.row-playing {{ background-color: #2f6b2f; color: #f2f2f2; }}
        .row-selected.row-playing label {{ color: #f2f2f2; }}
        .top-bar {{
            min-height: 36px;
            padding: 6px 10px;
            background-color: rgba(0, 0, 0, 0.65);
            border-radius: 10px;
        }}
        .top-bar label {{
            color: #f2f2f2;
        }}
        .preset-box {{
            background-color: rgba(0, 0, 0, 0.6);
            border-radius: 12px;
            padding: 6px;
        }}
        .controls-box button {{
            background-color: rgba(245, 245, 245, 0.95);
            border-radius: 999px;
            min-width: 40px;
            min-height: 40px;
        }}
        .controls-box button label,
        .controls-box button image {{
            color: #111111;
        }}
        .footer {{
            min-height: 56px;
            padding: 8px 12px;
            background-color: rgba(17, 17, 17, 0.75);
            border-radius: 12px;
        }}
        .footer label,
        .footer image {{
            color: #f2f2f2;
        }}
        .footer button {{
            background-color: rgba(245, 245, 245, 0.95);
            border-radius: 8px;
        }}
        .footer button label,
        .footer button image {{
            color: #111111;
        }}
        .footer .volume-accent {{
            color: #00ff66;
        }}
        .now-playing {{
            font-size: 48px;
            font-family: "{DIGITAL_FONT_FAMILY}";
            color: #00ff66;
        }}
        .now-playing-box {{
            background-color: #000000;
            border-radius: 12px;
            padding: 12px 18px;
            min-width: 260px;
            min-height: 160px;
        }}
        .state-label {{ font-size: 14px; font-weight: 600; }}
        .volume-step {{ font-weight: 700; min-width: 36px; min-height: 36px; }}
        .volume-label {{ font-weight: 600; font-size: 18px; }}
        .volume-value {{
            font-weight: 600;
            font-size: 40px;
            font-family: "{DIGITAL_FONT_FAMILY}";
        }}
        .volume-accent {{ color: #00ff66; }}

        window.app-window {{
            background-image: url("file://{background_image}");
            background-repeat: no-repeat;
            background-position: center;
            background-size: cover;
            font-family: "Inter", sans-serif;
        }}
        """
        self.css_provider.load_from_data(css.encode("utf-8"))
        screen = Gdk.Screen.get_default()
        if screen:
            Gtk.StyleContext.add_provider_for_screen(
                screen, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )
        self.refresh_row_styles()

    def refresh_row_styles(self):
        for index, row in enumerate(self.listbox.get_children(), start=1):
            context = row.get_style_context()
            context.remove_class("row-odd")
            context.remove_class("row-even")
            context.remove_class("row-selected")
            context.remove_class("row-playing")
            class_name = "row-odd" if index % 2 == 1 else "row-even"
            context.add_class(class_name)
            if row == self.listbox.get_selected_row():
                context.add_class("row-selected")
            if row.radio_id == self.playing_id:
                context.add_class("row-playing")

    def add_radios(self, radios):
        existing = {(radio["name"], radio["stream_url"]) for radio in self.radios}
        added = False
        for radio in radios:
            name = radio.get("name", "").strip()
            stream_url = (radio.get("stream_url") or radio.get("url") or "").strip()
            homepage = (radio.get("homepage") or "").strip() or None
            favicon = (radio.get("favicon") or "").strip() or None
            if not name or not stream_url:
                continue
            if (name, stream_url) in existing:
                continue
            existing.add((name, stream_url))
            radio_id = radio.get("id") or str(uuid.uuid4())
            row = RadioRow(
                radio_id, name, stream_url, homepage=homepage, favicon=favicon
            )
            self.listbox.add(row)
            entry = {"id": radio_id, "name": name, "stream_url": stream_url}
            if homepage:
                entry["homepage"] = homepage
            if favicon:
                entry["favicon"] = favicon
            self.radios.append(entry)
            self.load_favicon_async(row)
            added = True
        if added:
            self.listbox.invalidate_sort()
            self.listbox.show_all()
            save_json(RADIOS_PATH, self.radios)
            self.refresh_row_styles()

    def confirm_insecure_ssl(self, message):
        done = threading.Event()
        result = {"allow": False}

        def prompt():
            dialog = Gtk.MessageDialog(
                parent=self,
                flags=0,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.NONE,
                text=message,
            )
            dialog.add_button("Annuler", Gtk.ResponseType.CANCEL)
            dialog.add_button("Continuer", Gtk.ResponseType.OK)
            response = dialog.run()
            dialog.destroy()
            result["allow"] = response == Gtk.ResponseType.OK
            done.set()
            return False

        GLib.idle_add(prompt)
        done.wait()
        return result["allow"]

    def fetch_radio_browser(self, name, on_result, on_error):
        def worker():
            try:
                query = urllib.parse.quote(name)
                urls = [
                    f"https://de1.api.radio-browser.info/json/stations/byname/{query}?limit=25",
                    f"https://api.radio-browser.info/json/stations/byname/{query}?limit=25",
                ]
                max_bytes = 2 * 1024 * 1024
                last_error = None
                insecure = False
                data = None
                for url in urls:
                    request = urllib.request.Request(
                        url,
                        headers={"User-Agent": "Clarionet/1.0"},
                    )
                    try:
                        payload, insecure = open_url(
                            request,
                            timeout=8,
                            max_bytes=max_bytes,
                            allow_insecure=False,
                        )
                    except ssl.SSLError as exc:
                        last_error = exc
                        if not self.confirm_insecure_ssl(
                            "Connexion SSL non verifiee. Continuer ?"
                        ):
                            raise RuntimeError(
                                "Connexion SSL non verifiee annulee"
                            ) from exc
                        payload, insecure = open_url(
                            request,
                            timeout=8,
                            max_bytes=max_bytes,
                            allow_insecure=True,
                        )
                    try:
                        if len(payload) > max_bytes:
                            raise ValueError("Reponse trop volumineuse")
                        data = json.loads(payload.decode("utf-8"))
                        break
                    except urllib.error.HTTPError as exc:
                        last_error = exc
                        if exc.code in (404, 429, 500, 502, 503, 504):
                            continue
                        raise
                    except Exception as exc:
                        last_error = exc
                        continue
                if data is None:
                    raise last_error or RuntimeError("Echec de la requete")
            except Exception as exc:
                GLib.idle_add(on_error, str(exc))
                return
            warning = "Connexion SSL non verifiee" if insecure else None
            GLib.idle_add(on_result, data, warning)

        threading.Thread(target=worker, daemon=True).start()

    def load_favicon_async(self, row):
        source_url = row.favicon_url or row.homepage or row.stream_url
        cache_path = favicon_cache_path(source_url)
        if not cache_path:
            return
        if cache_path.exists():
            row.set_icon_from_file(cache_path)
            return
        if cache_path in self.favicon_tasks:
            return
        self.favicon_tasks.add(cache_path)
        ICONS_DIR.mkdir(parents=True, exist_ok=True)
        if row.favicon_url:
            url = row.favicon_url
        else:
            url = favicon_url(source_url)
        if not url:
            self.favicon_tasks.discard(cache_path)
            return

        def worker():
            try:
                request = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Clarionet/1.0"},
                )
                max_bytes = 512 * 1024
                data, _ = open_url(
                    request,
                    timeout=5,
                    max_bytes=max_bytes,
                    allow_insecure=False,
                )
                if len(data) > max_bytes:
                    raise ValueError("Favicon trop volumineux")
                temp_path = cache_path.with_suffix(".tmp")
                with temp_path.open("wb") as handle:
                    handle.write(data)
                temp_path.replace(cache_path)
            except Exception:
                self.favicon_tasks.discard(cache_path)
                return

            def update_ui():
                row.set_icon_from_file(cache_path)
                self.favicon_tasks.discard(cache_path)
                return False

            GLib.idle_add(update_ui)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()

    def on_delete_event(self, *_):
        self.quit_app()
        return True

    def quit_app(self):
        logger.info("Quit")
        self.on_stop(None)
        self.mpv.quit()
        application = self.get_application()
        if application:
            application.quit()
        Gtk.main_quit()
        self.destroy()

    def show_error(self, message):
        logger.error("%s", message)
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message,
        )
        dialog.run()
        dialog.destroy()


class ClarionetApplication(Gtk.Application):
    def __init__(self):
        super().__init__(application_id="com.example.clarionet")

    def do_activate(self):
        logger.info("Start %s %s", APP_NAME, APP_VERSION)
        window = ClarionetApp(self)
        window.show_all()


if __name__ == "__main__":
    app = ClarionetApplication()
    exit_code = app.run(sys.argv)
    sys.exit(exit_code)
