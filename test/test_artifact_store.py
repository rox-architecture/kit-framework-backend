from pathlib import Path

import pytest

from cee.artifact_store import FileArtifactStore
from cee.schema.execution_schema import Item


def test_round_trip_and_execution_isolation(tmp_path: Path) -> None:
    """Artifacts round-trip and remain isolated by execution ID."""
    store = FileArtifactStore(tmp_path)
    first = Item(json_data={"content_type": "text/plain"}, binary=b"first")
    second = Item(json_data={"content_type": "text/plain"}, binary=b"second")

    first_reference = store.put("execution-1", "node", "output_0", first)
    second_reference = store.put("execution-2", "node", "output_0", second)

    assert store.get(first_reference) == first
    assert store.get(second_reference) == second

    store.delete_execution("execution-1")
    assert not (tmp_path / "execution-1").exists()
    assert store.get(second_reference) == second


def test_rejects_unsafe_path_components(tmp_path: Path) -> None:
    """Path traversal cannot escape the configured artifact root."""
    store = FileArtifactStore(tmp_path)

    with pytest.raises(ValueError, match="Unsafe artifact"):
        store.put("../outside", "node", "output_0", Item(binary=b""))
