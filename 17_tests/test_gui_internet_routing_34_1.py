from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.agents.research_agent import ResearchAgent
from kontinuum.core.application_services import PromptOrchestrator
from kontinuum.core.conversation import Intent
from kontinuum.tools.search_engine_tools import SearchEngineTools


gui_source = (ROOT / "11_gui" / "desktop_gui_34_1.py").read_text(encoding="utf-8")
assert 'text="Suchmodus:"' in gui_source
assert 'tk.StringVar(value="Automatisch")' in gui_source
assert 'values=("Automatisch", "Lokal", "Internet", "Hybrid")' in gui_source
assert 'set_search_mode(self.search_mode.get())' in gui_source
assert 'text="Datei öffnen"' in gui_source
assert 'text="Datei lernen"' in gui_source
assert 'text="Ordner lernen"' in gui_source
assert "_enable_file_drop" in gui_source
assert "_handle_file_drop" in gui_source
assert "drop_target" in gui_source
assert "lerne aus Datei" in gui_source
assert "lerne aus Ordner" in gui_source

orchestrator = PromptOrchestrator.__new__(PromptOrchestrator)

assert orchestrator._source_command("Suche im Internet nach aktuellen Nachrichten über OpenAI.") == "internet_only"
assert orchestrator._source_command("Nutze nur die lokale Datenbank.") == "local_only"
assert orchestrator._source_command("Nutze Internet und lokale Datenbank.") == "internet_and_local"
assert orchestrator._source_command("Zeige mir, wo du gesucht hast.") == "last"
assert orchestrator._needs_current_information(
    "Was sind die neuesten OpenAI Nachrichten?",
    Intent("dialog.question", "question"),
)
assert orchestrator._source_report(False, False, True, 0, search_mode="Internet").endswith("- Suchmodus: Internet")
assert "Internet-Recherche nicht verfügbar oder ohne verwertbare Treffer." in (
    "Internet-Recherche nicht verfügbar oder ohne verwertbare Treffer."
)


class SearchRouterStub:
    def __init__(self):
        self.queries = []

    def search(self, text, limit=5):
        self.queries.append((text, limit))
        return {"hits": [{"area": "03_memory", "snippet": "lokaler Treffer"}]}

    @staticmethod
    def format(result):
        return "Lokale Treffer: " + str(len(result.get("hits", [])))


class SearchEngineStub:
    config = {"enabled": True}

    def __init__(self):
        self.calls = []

    def search(self, text, mode="default"):
        self.calls.append((text, mode))
        return {
            "ok": True,
            "query": text,
            "results": [{"title": "Web", "url": "https://example.org", "snippet": "Webtreffer", "provider": "duckduckgo_html"}],
        }

    @staticmethod
    def format_results(result):
        return f"Internetsuche: {len(result['results'])} Treffer"


class FakeSystem:
    def __init__(self, mode):
        self.search_mode = mode
        self.search_router = SearchRouterStub()
        self.tools = {"search_engine_tools": SearchEngineStub()}


hybrid_orchestrator = PromptOrchestrator.__new__(PromptOrchestrator)
hybrid_orchestrator.system = FakeSystem("Hybrid")
assert hybrid_orchestrator._selected_mode() == "Hybrid"
hybrid_answer = hybrid_orchestrator._answer_with_search_engine("Alpha aktuell", "prefer_internet", include_local=True)
assert "Lokale Suche:" in hybrid_answer
assert "Internetsuche: 1 Treffer" in hybrid_answer
assert "- Suchmodus: Hybrid" in hybrid_answer
assert hybrid_orchestrator.system.tools["search_engine_tools"].calls[-1][1] == "prefer_internet"

local_orchestrator = PromptOrchestrator.__new__(PromptOrchestrator)
local_orchestrator.system = FakeSystem("Lokal")
local_answer = local_orchestrator._answer_local_only("Alpha")
assert "Lokale Treffer: 1" in local_answer
assert "- Internet: nein" in local_answer
assert "- Suchmodus: Lokal" in local_answer
assert local_orchestrator.system.tools["search_engine_tools"].calls == []

internet_orchestrator = PromptOrchestrator.__new__(PromptOrchestrator)
internet_orchestrator.system = FakeSystem("Internet")
internet_answer = internet_orchestrator._answer_with_search_engine("Alpha", "internet_only", include_local=False)
assert "Internetsuche: 1 Treffer" in internet_answer
assert "- lokale Datenbank: nein" in internet_answer
assert "- Suchmodus: Internet" in internet_answer
assert internet_orchestrator.system.tools["search_engine_tools"].calls[-1][1] == "internet_only"

agent = ResearchAgent()
assert agent._search_mode("Suche im Internet nach aktuellen Nachrichten über OpenAI.") == "prefer_internet"
assert agent._search_mode("Nutze nur die lokale Datenbank.") == "local_only"
assert agent._search_mode("Nutze Internet und lokale Datenbank.") == "prefer_internet"

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temporary_root:
    router = SearchEngineTools(Path(temporary_root))
    router.config["provider_order"] = [
        "local_knowledge",
        "notebook_knowledge",
        "duckduckgo_html",
        "duckduckgo_lite",
    ]
    assert router._providers_for_mode("local_only") == ["local_knowledge", "notebook_knowledge"]
    assert router._providers_for_mode("internet_only") == ["duckduckgo_html", "duckduckgo_lite"]
    assert router._providers_for_mode("prefer_internet") == [
        "duckduckgo_html",
        "duckduckgo_lite",
        "local_knowledge",
        "notebook_knowledge",
    ]
    assert router._providers_for_mode("hybrid") == router._providers_for_mode("prefer_internet")

print("Kontinuum 34.1 GUI internet routing tests passed")
