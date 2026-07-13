# © 2026 Raphael Maria Schatz – Projekt Kontinuum. Alle Rechte vorbehalten.

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class LanguageModelTools:
    DEFAULT_CONFIG = {
        "enabled": True,
        "provider": "ollama",
        "base_url": "http://127.0.0.1:11434",
        "model": "qwen2.5:3b",
        "language": "de",
        "timeout_seconds": 180,
        "temperature": 0.4,
        "system_prompt": (
            "Du bist Kontinuum, ein lokaler deutschsprachiger Assistent von Raphael Schatz. "
            "Antworte klar, hilfreich und ehrlich auf Deutsch. Erfinde keine Fakten oder ausgefuehrten Aktionen. "
            "Wenn dir Informationen fehlen, sage das offen. Halte Antworten standardmaessig kompakt. "
            "Priorisiere immer die aktuelle Frage. Ignoriere fruehere Themen, wenn sie fuer die aktuelle Frage "
            "nicht relevant sind. Eine Korrektur des Benutzers hat Vorrang vor deiner vorherigen Antwort."
        ),
    }

    def __init__(self, project_root: str | Path):
        self.project_root = Path(project_root)
        self.config_path = self.project_root / "24_config" / "language_model.json"
        self.config = self._load_config()
        self._status_cache: tuple[float, dict] | None = None

    def _load_config(self) -> dict:
        config = dict(self.DEFAULT_CONFIG)
        try:
            loaded = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
            if isinstance(loaded, dict):
                config.update(loaded)
        except (OSError, ValueError):
            pass

        config["enabled"] = os.getenv("KONTINUUM_LLM_ENABLED", str(config["enabled"])).casefold() not in {
            "0",
            "false",
            "no",
            "off",
        }
        config["base_url"] = os.getenv("KONTINUUM_LLM_BASE_URL", str(config["base_url"])).rstrip("/")
        config["model"] = os.getenv("KONTINUUM_LLM_MODEL", str(config["model"]))
        return config

    def status(self) -> dict:
        if self._status_cache and time.monotonic() - self._status_cache[0] < 10:
            return dict(self._status_cache[1])
        if not self.config["enabled"]:
            return {"available": False, "enabled": False, "message": "Lokales Sprachmodell ist deaktiviert."}
        try:
            payload = self._request("/api/tags", timeout=1)
            installed = [item.get("name", "") for item in payload.get("models", []) if isinstance(item, dict)]
            model = self.config["model"]
            available = model in installed or any(name.startswith(f"{model}:") for name in installed)
            if available:
                message = f"Lokales Sprachmodell aktiv: {model} ueber Ollama."
            else:
                message = f"Ollama ist erreichbar, aber das Modell {model} ist noch nicht installiert."
            result = {
                "available": available,
                "enabled": True,
                "provider": "ollama",
                "model": model,
                "installed_models": installed,
                "message": message,
            }
            self._status_cache = (time.monotonic(), result)
            return dict(result)
        except (OSError, ValueError) as exc:
            result = {
                "available": False,
                "enabled": True,
                "provider": "ollama",
                "model": self.config["model"],
                "message": f"Lokales Sprachmodell nicht erreichbar: {exc}",
            }
            self._status_cache = (time.monotonic(), result)
            return dict(result)

    def generate(
        self,
        prompt: str,
        context: list[dict] | None = None,
        local_truths: dict | None = None,
        user: dict | None = None,
        timeout_seconds: int | None = None,
    ) -> dict:
        if not self.config["enabled"]:
            return {"ok": False, "error": "Lokales Sprachmodell ist deaktiviert."}
        facts = dict(local_truths or {})
        active_user = dict(user or {})
        context_instruction = (
            "\nBestätigte lokale Wahrheiten haben Vorrang vor Vermutungen: "
            + json.dumps({"user": active_user, "facts": facts}, ensure_ascii=False)
        )
        messages = [{"role": "system", "content": self.config["system_prompt"] + context_instruction}]
        recent_context = [
            turn for turn in (context or []) if turn.get("intent") != "command"
        ][-6:]
        if recent_context and recent_context[-1].get("role") == "user" and recent_context[-1].get("content") == prompt:
            recent_context.pop()
        for turn in recent_context:
            role = str(turn.get("role", ""))
            content = str(turn.get("content", "")).strip()
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": prompt})
        body = {
            "model": self.config["model"],
            "stream": False,
            "messages": messages,
            "options": {"temperature": self.config["temperature"]},
        }
        try:
            payload = self._request(
                "/api/chat",
                body,
                timeout=int(timeout_seconds or self.config["timeout_seconds"]),
            )
            answer = str(payload.get("message", {}).get("content", "")).strip()
            if not answer:
                return {"ok": False, "error": "Das Sprachmodell lieferte keine Antwort."}
            return {"ok": True, "answer": answer, "model": self.config["model"], "provider": "ollama"}
        except (OSError, ValueError) as exc:
            return {"ok": False, "error": str(exc), "model": self.config["model"], "provider": "ollama"}

    def generate_grounded_answer(self, question: str, sources: list[dict], timeout_seconds: int = 8) -> dict:
        if not sources:
            return {"ok": False, "error": "Keine abrufbaren Quellen vorhanden."}
        source_blocks = []
        for index, source in enumerate(sources, start=1):
            source_blocks.append(
                f"[{index}] Titel: {source.get('title', '')}\n"
                f"URL: {source.get('url', '')}\n"
                f"Auszug: {str(source.get('text', ''))[:1600]}"
            )
        prompt = (
            "Beantworte die Frage ausschließlich anhand der folgenden Quellen. "
            "Belege jede wesentliche Tatsachenbehauptung mit [1], [2] usw. "
            "Wenn Quellen widersprüchlich oder unzureichend sind, sage das ausdrücklich. "
            "Erfinde keine Informationen und füge keine Quellen hinzu.\n\n"
            f"Frage: {question}\n\nQuellen:\n" + "\n\n".join(source_blocks)
        )
        return self.generate(prompt, context=[], local_truths={}, user={}, timeout_seconds=timeout_seconds)

    def _request(self, endpoint: str, body: dict | None = None, timeout: int = 10) -> dict:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8") if body is not None else None
        request = Request(
            f"{self.config['base_url']}{endpoint}",
            data=data,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            method="POST" if body is not None else "GET",
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise OSError(f"Ollama HTTP-Fehler {exc.code}: {detail[:300]}") from exc
        except URLError as exc:
            raise OSError(f"Ollama-Verbindung fehlgeschlagen: {exc.reason}") from exc
