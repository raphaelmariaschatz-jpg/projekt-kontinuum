from __future__ import annotations

import base64
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(os.environ.get("KONTINUUM_ROOT", "C:/Projekt Kontinuum"))
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.agents.agent_registry import AgentRouter, build_agents  # noqa: E402
from kontinuum.core.continuous_canonical_engine import ContinuousCanonicalEngine  # noqa: E402
from kontinuum.core.conversation import ConversationManager  # noqa: E402
from kontinuum.core.request_router import RequestRouter  # noqa: E402
from kontinuum.core.storage import Storage  # noqa: E402
from kontinuum.core.vision_agent import VisionAgentService  # noqa: E402
from kontinuum.tools.path_tools import PathTools  # noqa: E402


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
)
JPG_1X1 = base64.b64decode(
    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAP//////////////////////////////////////////////////////////////////////////////////////"
    "2wBDAf//////////////////////////////////////////////////////////////////////////////////////"
    "wAARCAABAAEDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAX/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oADAMBAAIQAxAAAAH/"
    "xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAEFAqf/xAAUEQEAAAAAAAAAAAAAAAAAAAAA/9oACAEDAQE/ASP/xAAUEQEAAAAAAAAA"
    "AAAAAAAAAAAA/9oACAECAQE/ASP/xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oACAEBAAY/Al//xAAUEAEAAAAAAAAAAAAAAAAAAAAA/9oA"
    "CAEBAAE/IV//2gAMAwEAAgADAAAAEP/EABQRAQAAAAAAAAAAAAAAAAAAABD/2gAIAQMBAT8QH//EABQRAQAAAAAAAAAAAAAAAAAAABD/"
    "2gAIAQIBAT8QH//EABQQAQAAAAAAAAAAAAAAAAAAABD/2gAIAQEAAT8QH//Z"
)


with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary:
    root = Path(temporary) / "project"
    outside = Path(temporary) / "outside.png"
    paths = PathTools(root)
    paths.ensure_all()
    image_dir = root / "30_import" / "vision"
    image_dir.mkdir(parents=True, exist_ok=True)

    png = image_dir / "valid.png"
    jpg = image_dir / "valid.jpg"
    missing = image_dir / "missing.png"
    unsupported = image_dir / "notes.txt"
    broken = image_dir / "broken.png"
    png.write_bytes(PNG_1X1)
    jpg.write_bytes(JPG_1X1)
    unsupported.write_text("kein Bild", encoding="utf-8")
    broken.write_bytes(b"not a png")
    outside.write_bytes(PNG_1X1)

    storage = Storage(paths.paths()["data"] / "kontinuum.db")
    canonical_engine = ContinuousCanonicalEngine(root, paths, storage, "34.1", strict_config=False)
    vision = VisionAgentService(paths, storage, canonical_engine)

    png_result = vision.analyze_image(str(png))["result"]
    assert png_result["status"] == "ok"
    assert png_result["format"] == "PNG"
    assert png_result["width"] == 1
    assert png_result["height"] == 1
    assert png_result["vision_model_available"] is False
    assert png_result["content_recognition_performed"] is False
    assert png_result["memory_write_performed"] is False
    assert png.read_bytes() == PNG_1X1

    jpg_result = vision.analyze_image(str(jpg))["result"]
    assert jpg_result["status"] == "ok"
    assert jpg_result["format"] == "JPEG"
    assert jpg_result["width"] == 1
    assert jpg_result["height"] == 1

    missing_result = vision.analyze_image(str(missing))["result"]
    assert missing_result["status"] == "error"
    assert "nicht gefunden" in missing_result["errors"][0]

    unsupported_result = vision.analyze_image(str(unsupported))["result"]
    assert unsupported_result["status"] == "error"
    assert "Nicht unterstütztes Bildformat" in unsupported_result["errors"][0]

    broken_result = vision.analyze_image(str(broken))["result"]
    assert broken_result["status"] == "error"
    assert "beschädigt" in broken_result["errors"][0]

    blocked_result = vision.analyze_image(str(outside))["result"]
    assert blocked_result["status"] == "error"
    assert "nicht freigegeben" in blocked_result["errors"][0]

    conversation = ConversationManager(storage, {"name": "Kontinuum", "creator": "Raphael"}, "34.1")
    request_router = RequestRouter(paths)
    prompt = f"analysiere bild {png}"
    decision = request_router.decide(prompt, conversation.classify(prompt))
    assert decision.request_class == "Bildanalyse"
    assert decision.selected_agent == "vision_agent"

    agents = build_agents(storage=storage, tools={}, config={"vision_agent": vision})
    routed = AgentRouter(agents).route(prompt, conversation.classify(prompt).name)
    assert routed is not None
    assert routed.agent == "vision_agent"
    assert "VisionAgent: Bild technisch analysiert." in routed.answer
    assert "Bildinhaltserkennung durchgeführt: nein" in routed.answer

    status = vision.format_status()
    assert "VisionAgent aktiv: ja" in status
    assert "echtes Vision-Modell verfügbar: nein" in status

print("Kontinuum VisionAgent 1.0 tests passed")
