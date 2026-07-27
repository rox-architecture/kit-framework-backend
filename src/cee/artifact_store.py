"""Artifact storage used to exchange node values between Celery workers."""

import json
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from cee.config import ARTIFACT_ROOT
from cee.schema.execution_schema import Item


class ArtifactStore(ABC):
    """Storage contract for node output items."""

    @abstractmethod
    def put(self, execution_id: str, node_id: str, port: str, item: Item) -> str:
        """Store an item and return its opaque reference."""

    @abstractmethod
    def get(self, reference: str) -> Item:
        """Load an item from an opaque reference."""

    @abstractmethod
    def delete_execution(self, execution_id: str) -> None:
        """Delete every artifact belonging to an execution."""


class FileArtifactStore(ArtifactStore):
    """Store metadata and binary payloads under a shared filesystem root."""

    def __init__(self, root: Path = ARTIFACT_ROOT) -> None:
        """Create a file store rooted at the configured shared directory."""
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _safe(value: str) -> str:
        if not value or value in {".", ".."} or "/" in value or "\\" in value:
            message = f"Unsafe artifact path component: {value!r}"
            raise ValueError(message)
        return value

    def _base(self, execution_id: str, node_id: str, port: str) -> Path:
        return (
            self.root
            / self._safe(execution_id)
            / self._safe(node_id)
            / self._safe(port)
        )

    def put(self, execution_id: str, node_id: str, port: str, item: Item) -> str:
        """Store one item as JSON metadata and a binary sidecar."""
        base = self._base(execution_id, node_id, port)
        base.parent.mkdir(parents=True, exist_ok=True)
        binary_path = base.with_suffix(".bin")
        metadata_path = base.with_suffix(".json")
        binary_path.write_bytes(item.binary)
        metadata = item.model_dump(mode="json")["json_data"]
        metadata_path.write_text(json.dumps(metadata), encoding="utf-8")
        return str(metadata_path.relative_to(self.root))

    def get(self, reference: str) -> Item:
        """Read an item using a root-relative reference."""
        metadata_path = (self.root / reference).resolve()
        if self.root not in metadata_path.parents:
            message = "Artifact reference escapes the configured root"
            raise ValueError(message)
        binary_path = metadata_path.with_suffix(".bin")
        metadata: dict[str, Any] = json.loads(metadata_path.read_text(encoding="utf-8"))
        return Item(json_data=metadata, binary=binary_path.read_bytes())

    def reference(self, execution_id: str, node_id: str, port: str) -> str:
        """Return the deterministic reference for an existing output."""
        path = self._base(execution_id, node_id, port).with_suffix(".json")
        return str(path.relative_to(self.root))

    def delete_execution(self, execution_id: str) -> None:
        """Delete all artifacts for an execution."""
        path = self.root / self._safe(execution_id)
        shutil.rmtree(path, ignore_errors=True)
