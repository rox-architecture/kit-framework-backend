from dotenv import load_dotenv
from pathlib import Path
import sys
import json

sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[2] / "src"),
)

from cee.adapters_plugins.ts_adapter import TsAdapter

load_dotenv(Path("../..") / ".env")

adapter = TsAdapter()
response = adapter.transfer_data_pull("vdma-sample-aas-5")

print("\n".join(response.text.splitlines()[:20]))
