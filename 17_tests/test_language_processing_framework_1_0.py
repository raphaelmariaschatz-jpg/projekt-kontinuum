from __future__ import annotations

import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.core.language_processing import CanonicalLanguageProcessingFramework
from kontinuum.core.system import KontinuumSystem


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_directory:
    system = KontinuumSystem(temporary_directory)
    try:
        framework = system.language_processing_framework
        assert isinstance(framework, CanonicalLanguageProcessingFramework)
        assert system.agent_config["language_processing_framework"] is framework
        status = framework.status()
        assert status["active"] is True
        assert status["processing_steps"] == 6
        assert status["token_fields"] == 11
        assert status["tokenization"] is False
        assert status["model_integration"] is False
        assert status["semantic_inference"] is False
        assert status["training"] is False
        assert status["fine_tuning"] is False
        assert status["weight_management"] is False
        assert status["direct_memory_write"] is False
        assert system.status()["language_processing_framework"]["active"] is True

        assert [item["id"] for item in framework.list_processing_steps()] == [
            f"CLPF-{index:02d}" for index in range(1, 7)
        ]
        assert "token_id" in framework.token_schema()

        with system.storage.connect() as database:
            memories_before = database.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            events_before = database.execute("SELECT COUNT(*) FROM events").fetchone()[0]

        tokens = [
            {
                "token_id": "token-0",
                "surface": "Project",
                "position": {"absolute_index": 0, "sentence_index": 0},
                "span": {"source_start": 0, "source_end": 7},
                "sentence_id": "sentence-0",
                "document_id": "document-1",
                "metadata": {"provenance": "caller_supplied"},
            },
            {
                "token_id": "token-1",
                "surface": "Kontinuum",
                "position": {"absolute_index": 1, "sentence_index": 0},
                "span": {"source_start": 8, "source_end": 17},
                "sentence_id": "sentence-0",
                "document_id": "document-1",
                "metadata": {"provenance": "caller_supplied"},
            },
        ]
        sequence = framework.build_token_sequence(
            document_id="document-1",
            language="de",
            tokenizer_type="rule_based",
            tokenizer_version="caller-1",
            tokens=tokens,
        )
        duplicate = framework.build_token_sequence(
            document_id="document-1",
            language="de",
            tokenizer_type="rule_based",
            tokenizer_version="caller-1",
            tokens=tokens,
        )
        assert sequence.sequence_id == duplicate.sequence_id
        assert sequence.completed_stage_ids == ["CLPF-01", "CLPF-02", "CLPF-03"]
        assert sequence.model_independent is True
        assert sequence.model_invoked is False
        assert sequence.semantic_representation_generated is False
        assert sequence.training_performed is False
        assert sequence.direct_memory_write is False

        with system.storage.connect() as database:
            assert database.execute("SELECT COUNT(*) FROM memories").fetchone()[0] == memories_before
            assert database.execute("SELECT COUNT(*) FROM events").fetchone()[0] == events_before

        invalid = [dict(tokens[0])]
        invalid[0]["document_id"] = "other-document"
        try:
            framework.build_token_sequence(
                document_id="document-1",
                language="de",
                tokenizer_type="rule_based",
                tokenizer_version="caller-1",
                tokens=invalid,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("Invalid CLPF token sequence was accepted")
    finally:
        system.close()

print("Canonical Language Processing Framework 1.0 tests passed")
