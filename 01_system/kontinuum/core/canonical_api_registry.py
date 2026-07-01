from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path


class CanonicalAPIRegistryManager:
    """Read-only verifier for Kontinuum's canonical API contract."""

    VERSION = "1.3"
    REQUIRED_FIELDS = (
        "api_uid",
        "api_id",
        "canonical_name",
        "symbol",
        "introduced_in",
        "deprecated_in",
        "supersedes",
        "creator",
        "canonical_hash",
        "contract_version",
        "owner",
        "responsibility",
        "path",
        "kind",
        "version",
        "stability",
        "inputs",
        "outputs",
        "dependencies",
        "foundation_relevance",
        "security_class",
        "mutation_policy",
        "test_coverage",
        "change_policy",
    )
    ALLOWED_STABILITY = {"stable", "release_stable", "protected"}
    ALLOWED_SECURITY_CLASSES = {
        "foundation_protected",
        "canonical_protected",
        "release_protected",
        "protected_read_only",
    }
    ALLOWED_MUTATION_POLICIES = {
        "read_only",
        "read_only_verification",
        "append_only_audit",
        "controlled_migration_only",
    }

    def __init__(
        self,
        project_root: str | Path,
        release_version: str = "34.1",
        strict_config: bool = True,
    ):
        self.root = Path(project_root).resolve()
        self.release_version = release_version
        token = release_version.replace(".", "_")
        self.config_path = self.root / "24_config" / f"canonical_api_registry_{token}.json"
        self.strict_config = strict_config
        self.config = self._load_config()

    def _load_config(self) -> dict:
        try:
            value = json.loads(self.config_path.read_text(encoding="utf-8-sig"))
        except (OSError, ValueError) as exc:
            if not self.strict_config:
                return {"version": self.release_version, "configured": False, "apis": []}
            raise RuntimeError(f"Canonical-API-Registry-Konfiguration fehlt oder ist ungueltig: {self.config_path}") from exc
        if value.get("version") != self.release_version:
            raise RuntimeError("Canonical-API-Registry-Konfiguration gehoert nicht zur aktiven Version.")
        return value

    @staticmethod
    def _signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
        arguments = list(node.args.posonlyargs) + list(node.args.args) + list(node.args.kwonlyargs)
        names = [argument.arg for argument in arguments]
        return [name for name in names if name != "self"]

    @staticmethod
    def _class_methods(node: ast.ClassDef) -> dict[str, ast.FunctionDef | ast.AsyncFunctionDef]:
        return {
            child.name: child
            for child in node.body
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
        }

    @staticmethod
    def _mutating_calls(node: ast.AST) -> list[str]:
        calls = []
        for child in ast.walk(node):
            if not isinstance(child, ast.Call):
                continue
            function = child.func
            if isinstance(function, ast.Attribute):
                name = function.attr
            elif isinstance(function, ast.Name):
                name = function.id
            else:
                continue
            if name in {"write_text", "unlink", "remove", "rmdir", "mkdir", "rename", "copy", "copy2"}:
                calls.append(name)
            if name in {"execute", "executemany"}:
                sql = child.args[0] if child.args else None
                if isinstance(sql, ast.Constant) and isinstance(sql.value, str):
                    first = sql.value.strip().split(None, 1)[0].casefold() if sql.value.strip() else ""
                    if first in {"insert", "update", "delete", "drop", "create", "alter", "replace"}:
                        calls.append(f"sql:{first}")
        return sorted(set(calls))

    def _load_symbols(self, relative: str) -> dict:
        path = self.root / relative
        if not path.is_file():
            return {"ok": False, "path": relative, "error": "Datei fehlt."}
        try:
            tree = ast.parse(path.read_text(encoding="utf-8-sig"))
        except (OSError, SyntaxError) as exc:
            return {"ok": False, "path": relative, "error": str(exc)}
        symbols = {
            node.name: node
            for node in tree.body
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
        }
        return {"ok": True, "path": relative, "tree": tree, "symbols": symbols}

    @staticmethod
    def _canonical_hash(api: dict) -> str:
        payload = {key: value for key, value in api.items() if key != "canonical_hash"}
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def _verify_api(self, api: dict) -> dict:
        missing_fields = [field for field in self.REQUIRED_FIELDS if field not in api]
        symbol = api.get("symbol", "")
        path = api.get("path", "")
        issues = []
        if missing_fields:
            issues.append("required_fields")
        canonical_hash = self._canonical_hash(api)
        hash_ok = bool(api.get("canonical_hash")) and api.get("canonical_hash") == canonical_hash
        if not hash_ok:
            issues.append("canonical_hash")
        canonical_name_ok = bool(api.get("canonical_name")) and api.get("canonical_name") == symbol
        if not canonical_name_ok:
            issues.append("canonical_name")
        loaded = self._load_symbols(path) if path else {"ok": False, "error": "Pfad fehlt.", "symbols": {}}
        if not loaded["ok"]:
            return {
                "ok": False,
                "api_uid": api.get("api_uid", ""),
                "api_id": api.get("api_id", ""),
                "canonical_name": api.get("canonical_name", ""),
                "symbol": symbol,
                "missing_fields": missing_fields,
                "expected_canonical_hash": canonical_hash,
                "hash_ok": hash_ok,
                "issues": issues + ["path"],
                "error": loaded.get("error", ""),
            }

        symbols = loaded["symbols"]
        class_name, _, method_name = symbol.partition(".")
        node = symbols.get(class_name)
        if not node:
            return {
                "ok": False,
                "api_uid": api.get("api_uid", ""),
                "api_id": api.get("api_id", ""),
                "canonical_name": api.get("canonical_name", ""),
                "symbol": symbol,
                "missing_fields": missing_fields,
                "expected_canonical_hash": canonical_hash,
                "hash_ok": hash_ok,
                "issues": issues + ["symbol"],
            }

        methods = self._class_methods(node) if isinstance(node, ast.ClassDef) else {}
        target = methods.get(method_name) if method_name else node
        if method_name and target is None:
            issues.append("symbol")

        expected_inputs = api.get("inputs", [])
        expected_input_names = [
            item["name"] if isinstance(item, dict) else str(item)
            for item in expected_inputs
        ]
        actual_signature = self._signature(target) if isinstance(target, (ast.FunctionDef, ast.AsyncFunctionDef)) else []
        if method_name and expected_input_names != actual_signature:
            issues.append("signature")

        required_methods = api.get("required_methods", [])
        missing_methods = [name for name in required_methods if name not in methods]
        if missing_methods:
            issues.append("required_methods")

        outputs = api.get("outputs", {})
        required_keys = outputs.get("required_keys", []) if isinstance(outputs, dict) else []
        if outputs and not isinstance(outputs, dict):
            issues.append("outputs")
        if outputs and not outputs.get("type"):
            issues.append("outputs")
        if required_keys and outputs.get("type") != "dict":
            issues.append("outputs")

        invalid_stability = api.get("stability") not in self.ALLOWED_STABILITY
        invalid_security = api.get("security_class") not in self.ALLOWED_SECURITY_CLASSES
        invalid_mutation = api.get("mutation_policy") not in self.ALLOWED_MUTATION_POLICIES
        if invalid_stability:
            issues.append("stability")
        if invalid_security:
            issues.append("security_class")
        if invalid_mutation:
            issues.append("mutation_policy")

        missing_tests = [
            relative
            for relative in api.get("test_coverage", [])
            if not (self.root / relative).is_file()
        ]
        if missing_tests:
            issues.append("test_coverage")

        mutation_violations = []
        if api.get("mutation_policy") in {"read_only", "read_only_verification"}:
            scan_node = target if method_name and target is not None else node
            mutation_violations = self._mutating_calls(scan_node)
            if mutation_violations:
                issues.append("mutation_policy_violation")

        return {
            "ok": not missing_fields and not issues,
            "api_uid": api.get("api_uid", ""),
            "api_id": api.get("api_id", ""),
            "canonical_name": api.get("canonical_name", ""),
            "symbol": symbol,
            "path": path,
            "kind": api.get("kind", ""),
            "missing_fields": missing_fields,
            "contract_version": api.get("contract_version", ""),
            "introduced_in": api.get("introduced_in", ""),
            "deprecated_in": api.get("deprecated_in"),
            "supersedes": api.get("supersedes"),
            "expected_canonical_hash": canonical_hash,
            "hash_ok": hash_ok,
            "actual_signature": actual_signature,
            "expected_signature": expected_input_names,
            "missing_methods": missing_methods,
            "required_keys": required_keys,
            "invalid_stability": invalid_stability,
            "invalid_security_class": invalid_security,
            "invalid_mutation_policy": invalid_mutation,
            "missing_tests": missing_tests,
            "mutation_violations": mutation_violations,
            "issues": sorted(set(issues)),
        }

    def status(self) -> dict:
        if not self.config.get("configured", True):
            return {
                "version": self.VERSION,
                "registry_version": self.release_version,
                "active": False,
                "ok": False,
                "configured": False,
                "mutation_policy": "read_only_verification; controlled_migration_only",
            }
        apis = self.config.get("apis", [])
        results = [self._verify_api(api) for api in apis]
        api_uids = [api.get("api_uid", "") for api in apis]
        canonical_names = [api.get("canonical_name", "") for api in apis]
        duplicate_ids = sorted({
            api_id
            for api_id in [api.get("api_id", "") for api in apis]
            if api_id and [item.get("api_id", "") for item in apis].count(api_id) > 1
        })
        duplicate_uids = sorted({
            api_uid
            for api_uid in api_uids
            if api_uid and api_uids.count(api_uid) > 1
        })
        duplicate_canonical_names = sorted({
            canonical_name
            for canonical_name in canonical_names
            if canonical_name and canonical_names.count(canonical_name) > 1
        })
        checks = {
            "manifest": bool(apis),
            "unique_api_ids": not duplicate_ids,
            "unique_api_uids": not duplicate_uids,
            "unique_canonical_names": not duplicate_canonical_names,
            "canonical_names": all("canonical_name" not in result["issues"] for result in results),
            "canonical_hashes": all("canonical_hash" not in result["issues"] for result in results),
            "symbols": all("symbol" not in result["issues"] for result in results),
            "signatures": all("signature" not in result["issues"] for result in results),
            "required_methods": all("required_methods" not in result["issues"] for result in results),
            "outputs": all("outputs" not in result["issues"] for result in results),
            "stability": all("stability" not in result["issues"] for result in results),
            "security": all("security_class" not in result["issues"] for result in results),
            "mutation_policy": all(
                "mutation_policy" not in result["issues"] and "mutation_policy_violation" not in result["issues"]
                for result in results
            ),
            "test_coverage": all("test_coverage" not in result["issues"] for result in results),
            "required_fields": all(not result["missing_fields"] for result in results),
        }
        return {
            "version": self.VERSION,
            "registry_version": self.release_version,
            "active": True,
            "configured": True,
            "ok": all(checks.values()),
            "api_count": len(apis),
            "checks": checks,
            "duplicate_api_ids": duplicate_ids,
            "duplicate_api_uids": duplicate_uids,
            "duplicate_canonical_names": duplicate_canonical_names,
            "apis": results,
            "scope": self.config.get("scope", ""),
            "mutation_policy": "read_only_verification; controlled_migration_only",
        }

    def format_status(self) -> str:
        status = self.status()
        if not status.get("configured", True):
            return "Canonical API Registry Manager 1.3: nicht konfiguriert."
        return (
            f"Canonical API Registry Manager {self.VERSION}: "
            f"{'VERIFIZIERT' if status.get('ok') else 'NICHT VERIFIZIERT'}.\n"
            f"- Registrierte Kern-APIs: {status.get('api_count', 0)}; "
            f"Symbole={status.get('checks', {}).get('symbols', False)}, "
            f"Signaturen={status.get('checks', {}).get('signatures', False)}.\n"
            f"- Pflichtmethoden={status.get('checks', {}).get('required_methods', False)}, "
            f"Outputs={status.get('checks', {}).get('outputs', False)}, "
            f"Tests={status.get('checks', {}).get('test_coverage', False)}.\n"
            f"- API-Identitaeten={status.get('checks', {}).get('unique_api_uids', False)}, "
            f"kanonische Hashes={status.get('checks', {}).get('canonical_hashes', False)}.\n"
            "- Pruefung ist read-only; API-Aenderungen erfordern kontrollierte Migration und Release-Pruefung."
        )
