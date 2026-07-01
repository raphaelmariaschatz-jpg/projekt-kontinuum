from __future__ import annotations

import hashlib
import json
from pathlib import Path


class CanonicalArtifactManager:
    """Read-only verifier for Kontinuum's canonical artifact contract."""

    VERSION = "1.4"
    ARTIFACT_CLASSES = (
        "release-critical",
        "audit-evidence",
        "migration-artifact",
        "documentation",
        "generated-cache",
        "historical-archive",
    )
    REQUIRED_ARTIFACT_FIELDS = ("artifact_id", "artifact_class", "path", "required", "expected_root")

    def __init__(
        self,
        project_root: str | Path,
        release_version: str = "34.1",
        strict_config: bool = True,
    ):
        self.root = Path(project_root).resolve()
        self.release_version = release_version
        token = release_version.replace(".", "_")
        self.config_path = self.root / "24_config" / f"canonical_artifacts_{token}.json"
        self.strict_config = strict_config
        self.config = self._load_config()

    def _load_config(self) -> dict:
        try:
            value = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            if not self.strict_config:
                return {"version": self.release_version, "configured": False, "artifacts": []}
            raise RuntimeError(f"Canonical-Artifact-Konfiguration fehlt oder ist ungueltig: {self.config_path}") from exc
        if value.get("version") != self.release_version:
            raise RuntimeError("Canonical-Artifact-Konfiguration gehoert nicht zur aktiven Version.")
        return value

    @staticmethod
    def _digest_json(value: dict | list) -> str:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def _verify_signed_document(cls, path: Path) -> bool:
        try:
            document = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError):
            return False
        payload = {key: value for key, value in document.items() if key != "proof_hash"}
        return bool(document.get("proof_hash")) and document["proof_hash"] == cls._digest_json(payload)

    def _inside_expected_root(self, relative: str, expected_root: str) -> bool:
        if not expected_root:
            return True
        path = Path(relative).as_posix().rstrip("/")
        root = Path(expected_root).as_posix().rstrip("/")
        return path == root or path.startswith(f"{root}/")

    def _matches(self, pattern: str) -> list[Path]:
        return sorted(
            (path for path in self.root.glob(pattern) if path.exists()),
            key=lambda path: path.relative_to(self.root).as_posix().casefold(),
        )

    def _verify_artifact(self, artifact: dict) -> dict:
        missing_fields = [field for field in self.REQUIRED_ARTIFACT_FIELDS if field not in artifact]
        artifact_class = artifact.get("artifact_class", "")
        relative = artifact.get("path", "")
        expected_root = artifact.get("expected_root", "")
        path = self.root / relative
        exists = path.exists()
        missing_required = bool(artifact.get("required", False) and not exists)
        wrong_class = artifact_class not in self.ARTIFACT_CLASSES
        wrong_location = bool(relative and not self._inside_expected_root(relative, expected_root))
        signed_required = bool(artifact.get("signed", False))
        signature_ok = True
        if signed_required:
            signature_ok = path.is_file() and self._verify_signed_document(path)
        lifecycle_policy = artifact.get("lifecycle_policy", "")
        lifecycle_ok = lifecycle_policy in self.config.get("allowed_lifecycle_policies", [])
        issues = []
        if missing_fields:
            issues.append("required_fields")
        if missing_required:
            issues.append("missing")
        if wrong_class:
            issues.append("artifact_class")
        if wrong_location:
            issues.append("location")
        if signed_required and not signature_ok:
            issues.append("signature")
        if not lifecycle_ok:
            issues.append("lifecycle_policy")
        return {
            "ok": not issues,
            "artifact_id": artifact.get("artifact_id", ""),
            "artifact_class": artifact_class,
            "path": relative,
            "exists": exists,
            "required": bool(artifact.get("required", False)),
            "expected_root": expected_root,
            "signed": signed_required,
            "signature_ok": signature_ok,
            "lifecycle_policy": lifecycle_policy,
            "missing_fields": missing_fields,
            "issues": issues,
        }

    def _verify_pattern(self, pattern_spec: dict) -> dict:
        pattern = pattern_spec.get("pattern", "")
        matches = self._matches(pattern) if pattern else []
        min_count = int(pattern_spec.get("min_count", 0))
        max_count = pattern_spec.get("max_count")
        if max_count is not None:
            max_count = int(max_count)
        expected_root = pattern_spec.get("expected_root", "")
        wrong_location = [
            path.relative_to(self.root).as_posix()
            for path in matches
            if not self._inside_expected_root(path.relative_to(self.root).as_posix(), expected_root)
        ]
        unsigned = []
        if pattern_spec.get("signed", False):
            unsigned = [
                path.relative_to(self.root).as_posix()
                for path in matches
                if not path.is_file() or not self._verify_signed_document(path)
            ]
        count = len(matches)
        issues = []
        if count < min_count:
            issues.append("min_count")
        if max_count is not None and count > max_count:
            issues.append("max_count")
        if wrong_location:
            issues.append("location")
        if unsigned:
            issues.append("signature")
        return {
            "ok": not issues,
            "pattern_id": pattern_spec.get("pattern_id", ""),
            "artifact_class": pattern_spec.get("artifact_class", ""),
            "pattern": pattern,
            "count": count,
            "min_count": min_count,
            "max_count": max_count,
            "expected_root": expected_root,
            "wrong_location": wrong_location,
            "unsigned": unsigned,
            "matches": [path.relative_to(self.root).as_posix() for path in matches],
            "issues": issues,
        }

    def _lifecycle_check(self) -> dict:
        policy_path = self.root / self.config.get("lifecycle_policy", "24_config/retention_policy.json")
        expected = self.config.get("required_lifecycle_values", {})
        try:
            policy = json.loads(policy_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            return {"ok": False, "path": str(policy_path), "error": str(exc), "invalid_values": expected}
        invalid = {
            key: {"expected": value, "actual": policy.get(key)}
            for key, value in expected.items()
            if policy.get(key) != value
        }
        required_roots = self.config.get("required_lifecycle_roots", [])
        missing_roots = [
            relative
            for relative in required_roots
            if not (self.root / relative).exists()
        ]
        return {
            "ok": not invalid and not missing_roots,
            "path": self.config.get("lifecycle_policy", "24_config/retention_policy.json"),
            "invalid_values": invalid,
            "missing_roots": missing_roots,
        }

    def _generated_cache_check(self) -> dict:
        cache_names = set(self.config.get("generated_cache_names", []))
        suffixes = tuple(self.config.get("generated_cache_suffixes", []))
        protected_roots = tuple(self.config.get("protected_cache_roots", []))
        findings = []
        for root in self.config.get("cache_scan_roots", []):
            base = self.root / root
            if not base.exists():
                continue
            for path in base.rglob("*"):
                relative = path.relative_to(self.root).as_posix()
                if path.is_dir() and path.name in cache_names:
                    findings.append(relative)
                elif path.is_file() and suffixes and path.suffix.casefold() in suffixes:
                    findings.append(relative)
        protected_findings = [
            relative
            for relative in findings
            if any(relative == root or relative.startswith(f"{root.rstrip('/')}/") for root in protected_roots)
        ]
        return {
            "ok": not protected_findings,
            "findings": sorted(set(findings)),
            "protected_findings": sorted(set(protected_findings)),
            "mode": "report_only_no_delete",
        }

    def status(self) -> dict:
        if not self.config.get("configured", True):
            return {
                "version": self.VERSION,
                "artifact_version": self.release_version,
                "active": False,
                "ok": False,
                "configured": False,
                "mutation_policy": "read_only_verification; no_move_no_delete_no_autofix",
            }
        artifacts = [self._verify_artifact(item) for item in self.config.get("artifacts", [])]
        patterns = [self._verify_pattern(item) for item in self.config.get("artifact_patterns", [])]
        lifecycle = self._lifecycle_check()
        generated_cache = self._generated_cache_check()
        class_counts = {
            artifact_class: sum(1 for item in artifacts if item["artifact_class"] == artifact_class)
            for artifact_class in self.ARTIFACT_CLASSES
        }
        checks = {
            "artifacts": all(item["ok"] for item in artifacts),
            "patterns": all(item["ok"] for item in patterns),
            "required_artifacts": all("missing" not in item["issues"] for item in artifacts),
            "locations": all("location" not in item["issues"] for item in artifacts + patterns),
            "signatures": all("signature" not in item["issues"] for item in artifacts + patterns),
            "classes": all("artifact_class" not in item["issues"] for item in artifacts),
            "lifecycle": lifecycle["ok"],
            "generated_cache": generated_cache["ok"],
        }
        return {
            "version": self.VERSION,
            "artifact_version": self.release_version,
            "active": True,
            "configured": True,
            "ok": all(checks.values()),
            "artifact_count": len(artifacts),
            "pattern_count": len(patterns),
            "artifact_classes": list(self.ARTIFACT_CLASSES),
            "class_counts": class_counts,
            "checks": checks,
            "artifacts": artifacts,
            "patterns": patterns,
            "lifecycle": lifecycle,
            "generated_cache": generated_cache,
            "mutation_policy": "read_only_verification; no_move_no_delete_no_autofix",
        }

    def format_status(self) -> str:
        status = self.status()
        if not status.get("configured", True):
            return "Canonical Artifact Manager 1.4: nicht konfiguriert."
        return (
            f"Canonical Artifact Manager {self.VERSION}: "
            f"{'VERIFIZIERT' if status.get('ok') else 'NICHT VERIFIZIERT'}.\n"
            f"- Artefakte={status.get('artifact_count', 0)}, Muster={status.get('pattern_count', 0)}, "
            f"Pflichtartefakte={status.get('checks', {}).get('required_artifacts', False)}.\n"
            f"- Signaturen={status.get('checks', {}).get('signatures', False)}, "
            f"Lifecycle={status.get('checks', {}).get('lifecycle', False)}, "
            f"Archivmuster={status.get('checks', {}).get('patterns', False)}.\n"
            "- Pruefung ist read-only; keine Artefakte werden verschoben, geloescht oder automatisch korrigiert."
        )
