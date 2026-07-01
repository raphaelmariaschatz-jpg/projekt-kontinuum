from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from kontinuum.version import APP_VERSION


class InternetLearningService:
    DEFAULT_CONFIG = {
        "enabled": True,
        "bandwidth_limit_percent": 10,
        "max_requests_per_minute": 2,
        "min_delay_between_requests_seconds": 10,
        "max_download_mb_per_hour": 5,
        "max_response_bytes": 500000,
        "request_timeout_seconds": 6,
        "cycle_interval_seconds": 900,
        "startup_delay_seconds": 10,
        "max_sources_per_cycle": 2,
        "allowed_source_classes": [
            "scientific_publication",
            "university",
            "public_documentation",
            "government",
            "technical_documentation",
            "encyclopedia",
        ],
        "blocked_source_classes": [
            "paywall_bypass",
            "illegal_source",
            "login_required",
            "private_data",
            "mass_scraping",
            "aggressive_crawler",
        ],
        "review_required": True,
        "write_to_memory_directly": False,
        "perform_startup_speedtest": False,
        "seed_sources": [],
    }

    USER_AGENT = f"Projekt-Kontinuum/{APP_VERSION} controlled-internet-learning"

    def __init__(self, path_tools, fetcher=None):
        self.path_tools = path_tools
        self.config_path = path_tools.paths()["config"] / "internet_learning_policy_34_1.json"
        self.config = self._load_config()
        data_root = path_tools.paths()["data"]
        self.queue_dir = data_root / "internet_learning_queue"
        self.review_dir = data_root / "internet_learning_review"
        self.log_path = path_tools.paths()["logs"] / "internet_learning_errors.jsonl"
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.review_dir.mkdir(parents=True, exist_ok=True)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.fetcher = fetcher or self._fetch_url
        self._stop = threading.Event()
        self._wake = threading.Event()
        self._pause = threading.Event()
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._request_times: list[float] = []
        self._download_events: list[tuple[float, int]] = []
        self._last_request_at = 0.0
        self._last_source = ""
        self._last_learning_time = ""
        self._last_message = "Internet-Lernen aus."
        self._new_findings = self._count_queue()

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass
        if "continuous_internet_learning_enabled" in config:
            config["enabled"] = bool(config.get("continuous_internet_learning_enabled"))
        config["continuous_internet_learning_enabled"] = bool(config.get("enabled", False))
        return config

    def start(self) -> bool:
        if not self.config.get("enabled", False):
            self._last_message = "Internet-Lernen aus."
            return False
        if self.is_running():
            return True
        self._stop.clear()
        self._wake.clear()
        self._thread = threading.Thread(target=self._worker, daemon=True, name="KontinuumInternetLearning")
        self._thread.start()
        return True

    def stop(self, timeout: float = 3.0) -> bool:
        self._stop.set()
        self._wake.set()
        thread = self._thread
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=timeout)
        return not self.is_running()

    def set_enabled(self, enabled: bool) -> bool:
        self.config["enabled"] = bool(enabled)
        self.config["continuous_internet_learning_enabled"] = bool(enabled)
        self._save_config()
        if enabled:
            return self.resume()
        self.pause()
        self.stop()
        self._last_message = "Internet-Lernen aus."
        return True

    def _save_config(self) -> None:
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config_path.write_text(json.dumps(self.config, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def pause(self) -> None:
        self._pause.set()
        self._last_message = "Internet-Lernen pausiert."

    def resume(self) -> bool:
        self._pause.clear()
        self._wake.set()
        return self.start()

    def is_running(self) -> bool:
        return bool(self._thread and self._thread.is_alive())

    def status(self) -> dict:
        state = "aus"
        if self.is_running():
            state = "pausiert" if self._pause.is_set() else "aktiv"
        elif self.config.get("enabled", False):
            state = "pausiert" if self._pause.is_set() else "bereit"
        return {
            "enabled": bool(self.config.get("enabled", False)),
            "running": self.is_running(),
            "state": state,
            "mode": "continuous_internet_learning",
            "last_source": self._last_source,
            "last_learning_time": self._last_learning_time,
            "new_findings": self._count_queue(),
            "bandwidth_limit_active": True,
            "bandwidth_limit_percent": int(self.config.get("bandwidth_limit_percent", 10)),
            "max_requests_per_minute": int(self.config.get("max_requests_per_minute", 2)),
            "min_delay_between_requests_seconds": float(self.config.get("min_delay_between_requests_seconds", 10)),
            "max_download_mb_per_hour": float(self.config.get("max_download_mb_per_hour", 5)),
            "review_required": bool(self.config.get("review_required", True)),
            "write_to_memory_directly": bool(self.config.get("write_to_memory_directly", False)),
            "queue_dir": str(self.queue_dir),
            "review_dir": str(self.review_dir),
            "message": self._last_message,
        }

    def run_cycle(self, reason: str = "background") -> dict:
        if not self.config.get("enabled", False):
            result = {"ok": False, "message": "Internet-Lernen aus."}
            self._last_message = result["message"]
            return result
        if self._pause.is_set():
            result = {"ok": False, "message": "Internet-Lernen pausiert."}
            self._last_message = result["message"]
            return result
        with self._lock:
            sources = self._allowed_sources()[: max(1, int(self.config.get("max_sources_per_cycle", 2)))]
            if not sources:
                result = {
                    "ok": False,
                    "message": "Internet-Lernen pausiert: Internet nicht verfügbar oder keine verwertbaren Quellen.",
                    "new_findings": 0,
                }
                self._last_message = result["message"]
                return result
            added = 0
            blocked = 0
            errors = 0
            for source in sources:
                decision = self._throttle_decision()
                if not decision["ok"]:
                    self._last_message = str(decision["message"])
                    break
                if not self._respect_min_delay():
                    break
                outcome = self._learn_source(source)
                added += int(outcome.get("added", False))
                blocked += int(outcome.get("blocked", False))
                errors += int(outcome.get("error", False))
            if added:
                message = f"Internet-Lernen: {added} neue Funde in Review/Queue abgelegt."
                ok = True
            elif errors or blocked:
                message = "Internet-Lernen pausiert: Internet nicht verfügbar oder keine verwertbaren Quellen."
                ok = False
            else:
                message = "Internet-Lernen: keine neuen Funde."
                ok = True
            result = {"ok": ok, "new_findings": added, "blocked": blocked, "errors": errors, "message": message}
            self._last_message = message
            return result

    def _worker(self) -> None:
        if self._stop.wait(max(0, int(self.config.get("startup_delay_seconds", 10)))):
            return
        while not self._stop.is_set():
            try:
                self.run_cycle()
            except Exception as exc:
                self._last_message = f"Internet-Lernen pausiert: {exc}"
                self._log_error("", str(exc), "worker")
            self._wake.clear()
            self._wake.wait(max(30, int(self.config.get("cycle_interval_seconds", 900))))

    def _allowed_sources(self) -> list[dict]:
        allowed = set(self.config.get("allowed_source_classes", []))
        blocked = set(self.config.get("blocked_source_classes", []))
        result = []
        for raw in self.config.get("seed_sources", []):
            if not isinstance(raw, dict):
                continue
            url = str(raw.get("url", "")).strip()
            source_class = str(raw.get("source_class", "unknown")).strip()
            if source_class in blocked or source_class not in allowed:
                self._log_error(url, f"Quelle blockiert: {source_class}", "policy")
                continue
            if not url.startswith("https://"):
                self._log_error(url, "Nur HTTPS-Quellen erlaubt.", "policy")
                continue
            result.append({"url": url, "source_class": source_class, "title": str(raw.get("title", ""))})
        return result

    def _learn_source(self, source: dict) -> dict:
        url = source["url"]
        try:
            payload = self.fetcher(url, int(self.config.get("request_timeout_seconds", 6)), int(self.config.get("max_response_bytes", 500000)))
        except Exception as exc:
            self._log_error(url, str(exc), "fetch")
            return {"error": True}
        content = str(payload.get("text", ""))
        if not content.strip():
            self._log_error(url, "Leerer oder nicht verwertbarer Inhalt.", "fetch")
            return {"error": True}
        byte_count = int(payload.get("bytes", len(content.encode("utf-8", errors="replace"))))
        self._record_bandwidth(byte_count)
        digest = hashlib.sha256(content.encode("utf-8", errors="replace")).hexdigest()
        queue_file = self.queue_dir / f"{digest}.json"
        review_file = self.review_dir / f"{digest}.json"
        if queue_file.exists() or review_file.exists():
            self._last_source = url
            return {"added": False}
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "url": url,
            "source_class": source.get("source_class", ""),
            "title": payload.get("title") or source.get("title", ""),
            "retrieved_at": now,
            "sha256": digest,
            "summary": self._summary(content),
            "bytes": byte_count,
            "review_required": True,
            "write_to_memory_directly": False,
            "status": "queued_for_review",
            "policy": "internet_learning_policy_34_1",
        }
        queue_file.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
        review_file.write_text(json.dumps({**record, "review_status": "pending"}, ensure_ascii=False, indent=2), encoding="utf-8")
        self._last_source = url
        self._last_learning_time = now
        self._new_findings = self._count_queue()
        return {"added": True}

    def _throttle_decision(self) -> dict:
        now = time.monotonic()
        self._request_times = [value for value in self._request_times if now - value < 60]
        if len(self._request_times) >= int(self.config.get("max_requests_per_minute", 2)):
            return {"ok": False, "message": "Internet-Lernen pausiert: Bandbreitenlimit erreicht."}
        self._download_events = [(ts, size) for ts, size in self._download_events if now - ts < 3600]
        max_bytes = float(self.config.get("max_download_mb_per_hour", 5)) * 1024 * 1024
        if sum(size for _, size in self._download_events) >= max_bytes:
            return {"ok": False, "message": "Internet-Lernen pausiert: Downloadlimit pro Stunde erreicht."}
        return {"ok": True}

    def _respect_min_delay(self) -> bool:
        now = time.monotonic()
        delay = float(self.config.get("min_delay_between_requests_seconds", 10))
        remaining = delay - (now - self._last_request_at)
        if remaining > 0 and self._last_request_at:
            return not self._stop.wait(remaining)
        self._last_request_at = time.monotonic()
        self._request_times.append(self._last_request_at)
        return True

    def _record_bandwidth(self, byte_count: int) -> None:
        self._download_events.append((time.monotonic(), max(0, int(byte_count))))

    def _fetch_url(self, url: str, timeout: int, max_bytes: int) -> dict:
        request = Request(url, headers={"User-Agent": self.USER_AGENT, "Accept": "text/html,text/plain,application/json"})
        try:
            with urlopen(request, timeout=timeout) as response:
                raw = response.read(max(1, max_bytes))
                charset = response.headers.get_content_charset() or "utf-8"
        except HTTPError as exc:
            raise RuntimeError(f"HTTP-Fehler {exc.code}: {exc.reason}") from exc
        except URLError as exc:
            raise RuntimeError(f"Netzwerkfehler: {exc.reason}") from exc
        text = raw.decode(charset, errors="replace")
        title_match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.I | re.S)
        title = " ".join(re.sub(r"<[^>]+>", " ", title_match.group(1)).split()) if title_match else ""
        cleaned = re.sub(r"<(script|style).*?</\1>", " ", text, flags=re.I | re.S)
        cleaned = " ".join(re.sub(r"<[^>]+>", " ", cleaned).split())
        return {"url": url, "title": title, "text": cleaned or text, "bytes": len(raw)}

    @staticmethod
    def _summary(content: str) -> str:
        return " ".join(content.split())[:700]

    def _count_queue(self) -> int:
        try:
            return len([path for path in self.queue_dir.glob("*.json") if path.is_file()])
        except OSError:
            return 0

    def _log_error(self, url: str, error: str, stage: str) -> None:
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "url": url,
            "stage": stage,
            "error": error,
        }
        try:
            with self.log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except OSError:
            pass
