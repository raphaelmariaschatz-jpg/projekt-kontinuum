from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "01_system"))

from kontinuum.agents.oracle_cloud_agent import OracleCloudAgent
from kontinuum.tools.oracle_cloud_tools import OracleCloudTools


with tempfile.TemporaryDirectory() as temporary_root:
    root = Path(temporary_root)
    config = root / "24_config" / "oracle_cloud.json"
    config.parent.mkdir(parents=True)
    config.write_text(json.dumps({"enabled": True, "allow_changes": False}), encoding="utf-8")
    tool = OracleCloudTools(root)
    status = tool.status()
    assert status["enabled"]
    assert not status["configured"]
    assert not tool.list_instances()["ok"]
    assert not tool.change_instance_state("start", "ocid1.instance.test", {})["ok"]

    tool.config["allow_changes"] = True
    assert not tool.change_instance_state("start", "ocid1.instance.test", {"role": "SUPERADMIN"})["ok"]
    admin = {
        "authenticated": True,
        "role": "SUPERADMIN",
        "is_superadmin": True,
        "permissions": {"can_execute_admin_commands": True},
    }
    assert tool._authorize_change(admin)["ok"]

    confirmed = []
    def confirmation(action, resource):
        confirmed.append((action, resource))
        return True

    agent = OracleCloudAgent(
        tools={"oracle_cloud_tools": tool},
        config={"conversation": {"user": admin}, "cost_confirmation_handler": confirmation},
    )
    assert agent.can_handle("oraclestatus")
    assert agent.can_handle("oracle instanzen")
    assert "Oracle Cloud Integration" in agent.handle("oraclestatus").answer
    tool._run = lambda arguments, event: {"ok": True, "message": "confirmed"}
    assert agent.handle("oracle starte ocid1.instance.test").answer == "confirmed"
    assert confirmed == [("Oracle-Instanz start", "ocid1.instance.test")]
    assert agent.handle("oracle starte ocid1.instance.test").answer == "confirmed"
    assert len(confirmed) == 2

print("Kontinuum Oracle Cloud tests passed")
