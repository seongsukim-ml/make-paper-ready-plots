#!/usr/bin/env python3
"""Extract the exact stored QHFlow2 figure outputs from a verified local checkout."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Local QHFlow2 checkout")
    parser.add_argument("--output-dir", type=Path, default=HERE / "qhflow2")
    args = parser.parse_args()
    manifest = json.loads((HERE / "qhflow2" / "sources.json").read_text())
    # Verify all notebooks before writing any images; do not execute notebook cells.
    notebooks = {}
    for figure in manifest["figures"]:
        path = figure["source_path"]
        if path in notebooks:
            continue
        data = (args.source / path).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if blob != figure["source_git_blob_sha"]:
            raise ValueError(f"Source differs from pinned public version: {path}")
        notebooks[path] = json.loads(data)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    for figure in manifest["figures"]:
        nb = notebooks[figure["source_path"]]
        output = nb["cells"][figure["cell_index"]]["outputs"][figure["output_index"]]
        encoded = output["data"]["image/png"]
        data = base64.b64decode("".join(encoded), validate=False)
        digest = hashlib.sha256(data).hexdigest()
        if figure.get("output_sha256") and digest != figure["output_sha256"]:
            raise ValueError(f"Output checksum mismatch: {figure['file']}")
        target = args.output_dir / figure["file"]
        target.write_bytes(data)
        with Image.open(target) as image:
            size = image.size
            image.verify()
        print(f"{figure['file']}: {size[0]}x{size[1]}, SHA256 {digest}")


if __name__ == "__main__":
    main()
