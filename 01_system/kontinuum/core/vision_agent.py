from __future__ import annotations

import json
import os
import re
import struct
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class VisionAgentService:
    VERSION = "1.0"
    MODE = "diagnostic_read_only"
    SUPPORTED_SUFFIXES = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tiff", ".tif"}
    WINDOWS_PATH_PATTERN = re.compile(r"(?i)\b[a-z]:[\\/][^\s\"']+")
    IMAGE_SUFFIX_PATTERN = re.compile(r"(?i)([^\s\"']+\.(?:png|jpg|jpeg|webp|bmp|gif|tiff|tif))")
    COMMAND_MARKERS = (
        "analysiere bild",
        "beschreibe bild",
        "vision ",
        "lies bild",
        "lese bild",
        "visionagentstatus",
    )
    DEFAULT_CONFIG = {
        "enabled": True,
        "mode": MODE,
        "vision_model_available": False,
        "no_source_mutation": True,
        "auto_memory_write": False,
        "allowed_roots": [
            ".",
            "30_import",
            "14_documents",
            "04_knowledge",
            "06_learning",
            "32_data",
        ],
    }

    def __init__(self, path_tools, storage: Any | None = None, canonical_engine: Any | None = None):
        self.path_tools = path_tools
        self.storage = storage
        self.canonical_engine = canonical_engine
        self.root = path_tools.project_root().resolve()
        self.config_path = path_tools.paths()["config"] / "vision_agent_1_0.json"
        self.config = self._load_config()
        self.output_dir = path_tools.paths()["data"] / "vision_agent_analyses"
        self.log_path = path_tools.paths()["logs"] / "vision_agent_1_0.jsonl"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.touch(exist_ok=True)
        self._last_result: dict[str, Any] = {}
        self._last_errors: list[str] = []

    def _load_config(self) -> dict[str, Any]:
        config = dict(self.DEFAULT_CONFIG)
        home = Path(os.environ.get("USERPROFILE", str(Path.home())))
        for candidate in (home / "Documents", home / "Dokumente"):
            value = str(candidate)
            if value not in config["allowed_roots"]:
                config["allowed_roots"].append(value)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        return config

    @classmethod
    def looks_like_vision_command(cls, text: str) -> bool:
        lower = (text or "").casefold()
        return any(marker in lower for marker in cls.COMMAND_MARKERS) or bool(cls.IMAGE_SUFFIX_PATTERN.search(text or ""))

    def status(self) -> dict[str, Any]:
        return {
            "active": bool(self.config.get("enabled", False)),
            "mode": self.config.get("mode", self.MODE),
            "vision_model_available": bool(self.config.get("vision_model_available", False)),
            "supported_formats": sorted(suffix.lstrip(".") for suffix in self.SUPPORTED_SUFFIXES),
            "allowed_roots": [str(path) for path in self._allowed_roots()],
            "last_source_path": self._last_result.get("source_path", ""),
            "last_status": self._last_result.get("status", ""),
            "last_export_path": self._last_result.get("export_path", ""),
            "last_errors": self._last_errors[-5:],
        }

    def format_status(self) -> str:
        status = self.status()
        errors = "; ".join(status["last_errors"]) if status["last_errors"] else "-"
        return "\n".join([
            "VisionAgent 1.0 Status:",
            f"- VisionAgent aktiv: {'ja' if status['active'] else 'nein'}",
            f"- Modus: {status['mode']}",
            f"- echtes Vision-Modell verfügbar: {'ja' if status['vision_model_available'] else 'nein'}",
            "- unterstützte Bildformate: " + ", ".join(status["supported_formats"]),
            "- erlaubte Verzeichnisse: " + "; ".join(status["allowed_roots"]),
            f"- letzte Quelle: {status['last_source_path'] or '-'}",
            f"- letzter Status: {status['last_status'] or '-'}",
            f"- letzter JSON-Export: {status['last_export_path'] or '-'}",
            f"- letzte Fehler: {errors}",
        ])

    def handle_command(self, text: str) -> dict[str, Any]:
        lower = (text or "").casefold().strip()
        if lower.strip(" .!?") == "visionagentstatus":
            return {"ok": True, "message": self.format_status(), "result": self.status()}
        return self.analyze_image(self._extract_path(text))

    def analyze_image(self, path: str) -> dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        result = self._base_result(path, timestamp)
        try:
            resolved = self._resolve_path(path)
        except ValueError as exc:
            result.update({"status": "error", "errors": [str(exc)]})
            return self._finish(result, "VISION_ANALYSIS_BLOCKED", "medium")

        result["source_path"] = str(resolved)
        result["file_exists"] = resolved.is_file()
        if not result["file_exists"]:
            result.update({"status": "error", "errors": ["Datei nicht gefunden oder nicht lesbar."]})
            return self._finish(result, "VISION_ANALYSIS_FAILED", "medium")

        suffix = resolved.suffix.casefold()
        if suffix not in self.SUPPORTED_SUFFIXES:
            result.update({
                "status": "error",
                "errors": [f"Nicht unterstütztes Bildformat: {suffix or 'ohne Endung'}"],
            })
            return self._finish(result, "VISION_ANALYSIS_FAILED", "medium")

        try:
            metadata = self._read_metadata(resolved, suffix)
        except Exception as exc:
            result.update({"status": "error", "errors": [f"Bilddatei beschädigt oder nicht lesbar: {exc}"]})
            return self._finish(result, "VISION_ANALYSIS_FAILED", "medium")

        result.update(metadata)
        result["status"] = "ok"
        result["summary"] = (
            f"Technische Bildanalyse: {metadata.get('format')}, "
            f"{metadata.get('width')}x{metadata.get('height')} px, "
            f"Farbraum/Modus: {metadata.get('mode') or metadata.get('color_space') or 'unbekannt'}. "
            "Kein echtes Vision-Modell angebunden; es wurden keine Bildinhalte interpretiert."
        )
        return self._finish(result, "VISION_ANALYSIS_COMPLETED", "info")

    def _base_result(self, path: str, timestamp: str) -> dict[str, Any]:
        return {
            "status": "pending",
            "source_path": str(path or ""),
            "file_exists": False,
            "format": "",
            "width": None,
            "height": None,
            "mode": "",
            "color_space": "",
            "summary": "",
            "warnings": [],
            "errors": [],
            "timestamp": timestamp,
            "agent": "VisionAgent",
            "method": "metadata_header_analysis",
            "vision_model_available": bool(self.config.get("vision_model_available", False)),
            "content_recognition_performed": False,
            "local_file": True,
            "memory_write_performed": False,
            "export_path": "",
        }

    def _read_metadata(self, path: Path, suffix: str) -> dict[str, Any]:
        raw = path.read_bytes()
        if suffix == ".png":
            return self._png(raw)
        if suffix in {".jpg", ".jpeg"}:
            return self._jpeg(raw)
        if suffix == ".gif":
            return self._gif(raw)
        if suffix == ".bmp":
            return self._bmp(raw)
        if suffix in {".tiff", ".tif"}:
            return self._tiff(raw)
        if suffix == ".webp":
            return self._webp(raw)
        raise ValueError("Format nicht unterstützt.")

    @staticmethod
    def _png(raw: bytes) -> dict[str, Any]:
        if len(raw) < 33 or raw[:8] != b"\x89PNG\r\n\x1a\n" or raw[12:16] != b"IHDR":
            raise ValueError("ungültiger PNG-Header")
        width, height = struct.unpack(">II", raw[16:24])
        color_type = raw[25]
        color_map = {
            0: "grayscale",
            2: "truecolor_rgb",
            3: "indexed_color",
            4: "grayscale_alpha",
            6: "truecolor_rgba",
        }
        return {"format": "PNG", "width": width, "height": height, "mode": color_map.get(color_type, "unknown"), "color_space": color_map.get(color_type, "unknown")}

    @staticmethod
    def _jpeg(raw: bytes) -> dict[str, Any]:
        if len(raw) < 4 or raw[:2] != b"\xff\xd8":
            raise ValueError("ungültiger JPEG-Header")
        index = 2
        while index + 9 < len(raw):
            while index < len(raw) and raw[index] == 0xFF:
                index += 1
            marker = raw[index]
            index += 1
            if marker in {0xD8, 0xD9}:
                continue
            if index + 2 > len(raw):
                break
            length = struct.unpack(">H", raw[index:index + 2])[0]
            if length < 2 or index + length > len(raw):
                break
            if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                precision = raw[index + 2]
                height, width = struct.unpack(">HH", raw[index + 3:index + 7])
                components = raw[index + 7]
                mode = {1: "grayscale", 3: "YCbCr/RGB", 4: "CMYK"}.get(components, f"{components}_components")
                return {"format": "JPEG", "width": width, "height": height, "mode": mode, "color_space": mode, "precision_bits": precision}
            index += length
        raise ValueError("keine JPEG-SOF-Metadaten gefunden")

    @staticmethod
    def _gif(raw: bytes) -> dict[str, Any]:
        if len(raw) < 10 or raw[:6] not in {b"GIF87a", b"GIF89a"}:
            raise ValueError("ungültiger GIF-Header")
        width, height = struct.unpack("<HH", raw[6:10])
        return {"format": "GIF", "width": width, "height": height, "mode": "indexed_color", "color_space": "palette"}

    @staticmethod
    def _bmp(raw: bytes) -> dict[str, Any]:
        if len(raw) < 30 or raw[:2] != b"BM":
            raise ValueError("ungültiger BMP-Header")
        dib_size = struct.unpack("<I", raw[14:18])[0]
        if dib_size < 12:
            raise ValueError("unbekannter BMP-DIB-Header")
        if dib_size == 12:
            width, height = struct.unpack("<HH", raw[18:22])
            bits = struct.unpack("<H", raw[24:26])[0]
        else:
            width, height = struct.unpack("<ii", raw[18:26])
            bits = struct.unpack("<H", raw[28:30])[0]
        return {"format": "BMP", "width": abs(width), "height": abs(height), "mode": f"{bits}_bit", "color_space": "bitmap"}

    @staticmethod
    def _tiff(raw: bytes) -> dict[str, Any]:
        if len(raw) < 8 or raw[:2] not in {b"II", b"MM"}:
            raise ValueError("ungültiger TIFF-Header")
        endian = "<" if raw[:2] == b"II" else ">"
        if struct.unpack(endian + "H", raw[2:4])[0] != 42:
            raise ValueError("ungültige TIFF-Magic")
        offset = struct.unpack(endian + "I", raw[4:8])[0]
        if offset + 2 > len(raw):
            raise ValueError("TIFF-IFD fehlt")
        count = struct.unpack(endian + "H", raw[offset:offset + 2])[0]
        width = height = None
        bits = ""
        cursor = offset + 2
        for _ in range(count):
            if cursor + 12 > len(raw):
                break
            tag, field_type, amount, value = struct.unpack(endian + "HHII", raw[cursor:cursor + 12])
            if tag == 256:
                width = value
            elif tag == 257:
                height = value
            elif tag == 258:
                bits = str(value if amount == 1 else "multi")
            cursor += 12
        if width is None or height is None:
            raise ValueError("TIFF-Bildgröße nicht gefunden")
        return {"format": "TIFF", "width": width, "height": height, "mode": f"{bits or 'unknown'}_bit", "color_space": "unknown"}

    @staticmethod
    def _webp(raw: bytes) -> dict[str, Any]:
        if len(raw) < 30 or raw[:4] != b"RIFF" or raw[8:12] != b"WEBP":
            raise ValueError("ungültiger WebP-Header")
        chunk = raw[12:16]
        if chunk == b"VP8X":
            width = 1 + int.from_bytes(raw[24:27], "little")
            height = 1 + int.from_bytes(raw[27:30], "little")
            return {"format": "WEBP", "width": width, "height": height, "mode": "unknown", "color_space": "unknown"}
        if chunk == b"VP8 " and len(raw) >= 30:
            width = struct.unpack("<H", raw[26:28])[0] & 0x3FFF
            height = struct.unpack("<H", raw[28:30])[0] & 0x3FFF
            return {"format": "WEBP", "width": width, "height": height, "mode": "lossy", "color_space": "YCbCr"}
        if chunk == b"VP8L" and len(raw) >= 25:
            b0, b1, b2, b3 = raw[21], raw[22], raw[23], raw[24]
            width = 1 + (((b1 & 0x3F) << 8) | b0)
            height = 1 + (((b3 & 0x0F) << 10) | (b2 << 2) | ((b1 & 0xC0) >> 6))
            return {"format": "WEBP", "width": width, "height": height, "mode": "lossless", "color_space": "unknown"}
        raise ValueError("WebP-Variante nicht erkannt")

    def _finish(self, result: dict[str, Any], event_type: str, severity: str) -> dict[str, Any]:
        if result.get("errors"):
            self._last_errors.append("; ".join(result["errors"]))
        if result.get("status") == "ok":
            export_path = self.output_dir / f"vision_analysis_{uuid.uuid4().hex}.json"
            result["export_path"] = str(export_path)
            export_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
        self._last_result = result
        self._log(result)
        self._emit_event(event_type, result, severity)
        return {"ok": result.get("status") == "ok", "result": result, "message": self.format_analysis(result)}

    def format_analysis(self, result: dict[str, Any]) -> str:
        if result.get("status") != "ok":
            return "\n".join([
                "VisionAgent: Bildanalyse nicht durchgeführt.",
                f"- Pfad: {result.get('source_path') or '-'}",
                f"- Fehler: {'; '.join(result.get('errors') or ['unbekannt'])}",
                "- Originaldatei verändert: nein",
            ])
        return "\n".join([
            "VisionAgent: Bild technisch analysiert.",
            f"- Datei: {result['source_path']}",
            f"- Format: {result['format']}",
            f"- Größe: {result['width']} x {result['height']} px",
            f"- Farbraum/Modus: {result.get('mode') or result.get('color_space') or 'unbekannt'}",
            f"- Analysezeitpunkt: {result['timestamp']}",
            "- verwendeter Agent: VisionAgent",
            f"- Verfahren: {result['method']}",
            f"- echtes Vision-Modell verfügbar: {'ja' if result['vision_model_available'] else 'nein'}",
            "- Bildinhaltserkennung durchgeführt: nein",
            "- Originaldatei verändert: nein",
            f"- JSON-Export: {result.get('export_path') or '-'}",
            f"- Kurzbeschreibung: {result['summary']}",
        ])

    def _resolve_path(self, value: str | Path) -> Path:
        raw = str(value or "").strip().strip('"')
        if not raw:
            raise ValueError("Kein Bildpfad angegeben.")
        path = Path(raw)
        if not path.is_absolute():
            path = self.root / path
        try:
            resolved = path.resolve()
        except OSError as exc:
            raise ValueError(str(exc)) from exc
        if not any(self._is_relative_to(resolved, root) for root in self._allowed_roots()):
            raise ValueError(f"Pfad ist nicht freigegeben: {resolved}")
        return resolved

    def _allowed_roots(self) -> list[Path]:
        roots = []
        for item in self.config.get("allowed_roots", []):
            item_path = Path(str(item))
            root = item_path.resolve() if item_path.is_absolute() else (self.root / item_path).resolve()
            roots.append(root)
        return roots or [self.root]

    @staticmethod
    def _is_relative_to(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
            return True
        except ValueError:
            return False

    @classmethod
    def _extract_path(cls, text: str) -> str:
        quoted = re.search(r'"([^"]+)"|\'([^\']+)\'', text or "")
        if quoted:
            return quoted.group(1) or quoted.group(2)
        windows_path = cls.WINDOWS_PATH_PATTERN.search(text or "")
        if windows_path:
            return windows_path.group(0).rstrip(".,;:!?)]}")
        suffix_path = cls.IMAGE_SUFFIX_PATTERN.search(text or "")
        if suffix_path:
            return suffix_path.group(1).rstrip(".,;:!?)]}")
        match = re.search(r"(?:analysiere bild|beschreibe bild|lies bild|lese bild|vision)\s+(.+)$", text or "", flags=re.I)
        if match:
            return match.group(1).strip()
        return (text or "").split()[-1] if (text or "").split() else ""

    def _log(self, result: dict[str, Any]) -> None:
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": result.get("status"),
            "source_path": result.get("source_path"),
            "format": result.get("format"),
            "width": result.get("width"),
            "height": result.get("height"),
            "errors": result.get("errors", []),
            "export_path": result.get("export_path", ""),
        }
        with self.log_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    def _emit_event(self, event_type: str, result: dict[str, Any], severity: str) -> None:
        engine = self.canonical_engine
        if not engine:
            return
        try:
            engine.ingest(
                event_type=event_type,
                source_component="vision_agent",
                affected_path=result.get("source_path", ""),
                affected_object_id=result.get("source_path", ""),
                severity=severity,
                payload={
                    "status": result.get("status"),
                    "format": result.get("format"),
                    "width": result.get("width"),
                    "height": result.get("height"),
                    "vision_model_available": result.get("vision_model_available", False),
                    "content_recognition_performed": result.get("content_recognition_performed", False),
                    "errors": result.get("errors", []),
                },
                provenance={"agent": "VisionAgentService", "version": self.VERSION, "method": result.get("method", "")},
                governance_context={"vision_analysis": True, "requires_review": False, "read_only": True},
            )
        except Exception as exc:
            self._last_errors.append(f"Canonical Event Bus: {exc}")
