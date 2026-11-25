"""Read selected public ZIP members with bounded HTTP Range requests."""
import io
from pathlib import Path, PurePosixPath
import stat
import zlib

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class RangeReader(io.RawIOBase):
    """Seekable, cached HTTP reader; never silently downloads a whole archive."""

    def __init__(self, url, size, block_size=4 * 1024 * 1024, session=None):
        super().__init__()
        if size <= 0 or block_size <= 0:
            raise ValueError("Archive size and block size must be positive")
        self.url, self.size, self.block_size = url, size, block_size
        self.position = 0
        self.cache_start, self.cache = 0, b""
        self.transferred_bytes = 0
        self.session = session or requests.Session()
        if session is None:
            retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
            self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        if whence not in {0, 1, 2}:
            raise ValueError("Invalid seek mode")
        position = offset + (0 if whence == 0 else self.position if whence == 1 else self.size)
        if position < 0:
            raise ValueError("Cannot seek before archive start")
        self.position = position
        return position

    def read(self, size=-1):
        size = min(self.size - self.position, size if size >= 0 else self.size - self.position)
        if size <= 0:
            return b""
        if size > 64 * 1024 * 1024:
            raise ValueError("Requested archive block exceeds 64 MiB")
        end = self.position + size
        if not (self.cache_start <= self.position and end <= self.cache_start + len(self.cache)):
            start = self.position
            stop = min(self.size, start + max(size, self.block_size))
            expected_range = f"bytes {start}-{stop - 1}/{self.size}"
            with self.session.get(self.url, headers={"Range": f"bytes={start}-{stop - 1}",
                                                    "Accept-Encoding": "identity"},
                                  stream=True, timeout=(15, 60)) as response:
                response.raise_for_status()
                if response.status_code != 206 or response.headers.get("Content-Range") != expected_range:
                    raise ValueError("Server did not honor the requested byte range; refusing full download")
                chunks, received = [], 0
                for chunk in response.iter_content(1024 * 1024):
                    received += len(chunk)
                    if received > stop - start:
                        raise ValueError("Server returned too much data")
                    chunks.append(chunk)
                if received != stop - start:
                    raise ValueError("Truncated archive range")
            self.cache_start, self.cache = start, b"".join(chunks)
            self.transferred_bytes += received
        data = self.cache[self.position - self.cache_start:end - self.cache_start]
        self.position = end
        return data

    def close(self):
        if not self.closed and hasattr(self, "session"):
            self.session.close()
        super().close()


def safe_destination(root, info):
    """Reject traversal, Windows paths and archive symlinks before extraction."""
    path = PurePosixPath(info.filename)
    if (path.is_absolute() or ".." in path.parts or "\\" in info.filename
            or ":" in info.filename or not path.parts
            or stat.S_ISLNK(info.external_attr >> 16)):
        raise ValueError(f"Unsafe ZIP member: {info.filename}")
    root = Path(root).resolve()
    destination = root.joinpath(*path.parts)
    if not destination.resolve().is_relative_to(root) or destination.is_symlink():
        raise ValueError(f"ZIP destination escapes the dataset folder: {info.filename}")
    return destination


def crc32_file(path):
    checksum = 0
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            checksum = zlib.crc32(block, checksum)
    return checksum & 0xFFFFFFFF


def extract_member(archive, info, root):
    """Idempotent extraction; existing matching files are reused, others preserved."""
    destination = safe_destination(root, info)
    if info.file_size > 64 * 1024 * 1024:
        raise ValueError(f"Selected file exceeds 64 MiB: {info.filename}")
    if destination.exists():
        if destination.stat().st_size == info.file_size and crc32_file(destination) == info.CRC:
            return destination, False
        raise ValueError(f"Existing file differs: {destination}. Move it aside before retrying.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".part")
    # A stale interrupted transfer is safe to remove: it is never a completed dataset file.
    if temporary.is_symlink():
        raise ValueError(f"Refusing symlink temporary file: {temporary}")
    try:
        with archive.open(info) as source, temporary.open("wb") as target:
            received = 0
            while block := source.read(1024 * 1024):
                received += len(block)
                if received > info.file_size:
                    raise ValueError("ZIP member exceeded declared size")
                target.write(block)
        if received != info.file_size or crc32_file(temporary) != info.CRC:
            raise ValueError(f"ZIP checksum mismatch: {info.filename}")
        temporary.replace(destination)
    finally:
        temporary.unlink(missing_ok=True)
    return destination, True
