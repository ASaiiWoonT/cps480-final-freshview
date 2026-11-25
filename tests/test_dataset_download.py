import io
import stat
import zipfile

import pytest

from src.dataset_download import RangeReader, extract_member, safe_destination


class Response:
    def __init__(self, data, status=206, content_range=""):
        self.data, self.status_code = data, status
        self.headers = {"Content-Range": content_range}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def raise_for_status(self):
        pass

    def iter_content(self, size):
        yield self.data


class Session:
    def __init__(self, data, mode="valid"):
        self.data, self.mode, self.calls = data, mode, 0

    def get(self, url, headers, **kwargs):
        self.calls += 1
        start, end = map(int, headers["Range"].removeprefix("bytes=").split("-"))
        data = self.data[start:end + 1]
        status = 200 if self.mode == "ignored" else 206
        if self.mode == "short":
            data = data[:-1]
        return Response(data, status, f"bytes {start}-{end}/{len(self.data)}")

    def close(self):
        pass


def make_archive():
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("Banana/example.txt", b"banana data" * 100)
    return buffer.getvalue()


def test_remote_zip_reads_and_reuses_matching_files(tmp_path):
    data = make_archive()
    session = Session(data)
    with RangeReader("https://example.invalid/test.zip", len(data), block_size=64, session=session) as reader:
        with zipfile.ZipFile(reader) as archive:
            info = archive.infolist()[0]
            path, downloaded = extract_member(archive, info, tmp_path)
            assert downloaded and path.read_bytes() == b"banana data" * 100
            before = path.stat().st_mtime_ns
            same, downloaded = extract_member(archive, info, tmp_path)
            assert same == path and not downloaded and path.stat().st_mtime_ns == before
            path.write_bytes(b"user's existing work")
            with pytest.raises(ValueError, match="Existing file differs"):
                extract_member(archive, info, tmp_path)
            assert path.read_bytes() == b"user's existing work"


@pytest.mark.parametrize("mode", ["ignored", "short"])
def test_range_reader_rejects_ignored_or_incomplete_ranges(mode):
    with RangeReader("https://example.invalid", 10, block_size=4,
                     session=Session(b"0123456789", mode)) as reader:
        with pytest.raises(ValueError):
            reader.read(2)


def test_range_cache_and_seek_bounds():
    session = Session(b"0123456789")
    with RangeReader("https://example.invalid", 10, block_size=4, session=session) as reader:
        assert reader.read(2) == b"01"
        assert reader.read(2) == b"23" and session.calls == 1
        reader.seek(-2, 2)
        assert reader.read(20) == b"89"
        assert reader.read(1) == b""
        with pytest.raises(ValueError):
            reader.seek(-1)


@pytest.mark.parametrize("name", ["../escape.jpg", "/escape.jpg", "C:/escape.jpg", "dir\\escape.jpg"])
def test_archive_traversal_is_rejected(tmp_path, name):
    with pytest.raises(ValueError, match="Unsafe ZIP"):
        safe_destination(tmp_path, zipfile.ZipInfo(name))


def test_archive_and_destination_symlinks_are_rejected(tmp_path):
    info = zipfile.ZipInfo("link.jpg")
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    with pytest.raises(ValueError):
        safe_destination(tmp_path, info)
    external = tmp_path / "external"
    external.mkdir()
    root = tmp_path / "dataset"
    root.mkdir()
    (root / "out").symlink_to(external, target_is_directory=True)
    with pytest.raises(ValueError, match="escapes"):
        safe_destination(root, zipfile.ZipInfo("out/file.jpg"))
