import json

import pytest

from patchpilot.showcase import load_showcase


def test_changed_saved_artifact_is_rejected(tmp_path):
    from patchpilot.config import ROOT

    envelope = json.loads((ROOT / "patchpilot/assets/showcase.json").read_text(encoding="utf-8"))
    envelope["payload"]["run"]["verification"][0]["actual"] = {"forged": True}
    path = tmp_path / "changed.json"
    path.write_text(json.dumps(envelope), encoding="utf-8")
    with pytest.raises(ValueError, match="checksum mismatch"):
        load_showcase(path)
