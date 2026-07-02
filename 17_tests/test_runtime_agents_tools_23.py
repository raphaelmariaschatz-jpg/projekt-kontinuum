from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.tools.tool_registry import build_tools
from kontinuum.agents.agent_registry import build_agents, route_prompt

tools = build_tools(root=ROOT)
agents = build_agents(tools=tools)

for prompt in [
    "Wie ist dein Name?",
    "Wer ist dein Schöpfer?",
    "lerne Mathematik",
    "suche Mathematik",
    "internetstatus",
    "autostatus",
]:
    result = route_prompt(prompt, agents)
    print("PROMPT:", prompt)
    print("AGENT:", result.agent)
    print(result.answer)
    print("-" * 60)
