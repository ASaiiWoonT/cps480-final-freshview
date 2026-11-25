"""Download only the reviewed banana folders from versioned public ZIP archives."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import yaml

from src.config import ROOT
from src.dataset_download import RangeReader, extract_member


def download(source_name, list_only=False):
    config = yaml.safe_load((ROOT / "configs/datasets.yaml").read_text())
    spec = config["sources"][source_name]
    destination = ROOT / spec["root"]
    with RangeReader(spec["archive_url"], spec["archive_size"]) as reader, zipfile.ZipFile(reader) as archive:
        selected = []
        counts = {folder: 0 for folder in spec["labels"]}
        names = set()
        for info in archive.infolist():
            if info.is_dir():
                continue
            path = PurePosixPath(info.filename)
            image = path.parent.as_posix() in counts and path.suffix.lower() in {".jpg", ".jpeg", ".png"}
            if image or info.filename in spec["extra_files"]:
                if info.filename in names:
                    raise ValueError(f"Repeated archive path: {info.filename}")
                names.add(info.filename)
                selected.append(info)
                if image:
                    counts[path.parent.as_posix()] += 1
        expected = {folder: rule["expected_images"] for folder, rule in spec["labels"].items()}
        if counts != expected or not set(spec["extra_files"]).issubset(names):
            raise ValueError(f"Archive layout changed: expected {expected}; found {counts}")
        print(f"{source_name}: {sum(counts.values())} images; selected size {sum(i.file_size for i in selected) / 1e6:.1f} MB", flush=True)
        if list_only:
            print(json.dumps(counts, indent=2))
            return
        rows = []
        # Archive order reuses adjacent cached blocks instead of fetching every image individually.
        for number, info in enumerate(sorted(selected, key=lambda i: i.header_offset), start=1):
            path, downloaded = extract_member(archive, info, destination)
            with path.open("rb") as handle:
                sha256 = hashlib.file_digest(handle, "sha256").hexdigest()
            rows.append({"archive_member": info.filename, "image_path": path.relative_to(ROOT).as_posix(),
                         "bytes": info.file_size, "crc32": f"{info.CRC:08x}",
                         "sha256": sha256})
            if number % 25 == 0 or number == len(selected):
                print(f"  verified {number}/{len(selected)} files", flush=True)
        receipt = {"source": source_name, "version": spec["version"], "doi": spec["doi"],
                   "source_url": spec["source_url"], "license": spec["license"],
                   "archive_url": spec["archive_url"], "archive_size": spec["archive_size"],
                   "verification": "ZIP member CRC32 verified; local SHA256 recorded; full archive hash NOT verified (partial download)",
                   "files": sorted(rows, key=lambda row: row["archive_member"])}
        output = ROOT / "data/manifests/downloads" / f"{source_name}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        temporary = output.with_suffix(".tmp")
        temporary.write_text(json.dumps(receipt, indent=2) + "\n")
        temporary.replace(output)
        print(f"Receipt: {output.relative_to(ROOT)}; transferred {reader.transferred_bytes / 1e6:.1f} MB", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", choices=["mendeley_banana", "tr6_banana", "all"])
    parser.add_argument("--list-only", action="store_true", help="Validate archive inventory without downloading images")
    args = parser.parse_args()
    for source in (["mendeley_banana", "tr6_banana"] if args.source == "all" else [args.source]):
        download(source, args.list_only)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        raise SystemExit(f"Download failed: {error}. Rerun to resume verified files.") from error
