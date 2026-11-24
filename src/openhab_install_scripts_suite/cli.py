from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

from .common import Config

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    parser = argparse.ArgumentParser(description="OpenHAB binding setup examples")
    parser.add_argument("binding", choices=("hue", "sonos"))
    args = parser.parse_args()
    config = Config.from_env()
    module_path = ROOT / "bindings" / args.binding / "install.py"
    spec = importlib.util.spec_from_file_location(f"binding_{args.binding}", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    with config.client() as client:
        module.run(client)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"[FEHLER] {exc}", file=sys.stderr)
        raise SystemExit(1)

