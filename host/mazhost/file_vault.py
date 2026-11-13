"""Read-only documents from one explicitly selected home folder."""
from __future__ import annotations

import base64
import hashlib
import mimetypes
import os
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query

from .core import MazCore, SKIP_DIRS

MAX_BYTES = 10 * 1024 * 1024
MAX_FILES = 2000
EXTENSIONS = {'.pdf', '.png', '.jpg', '.jpeg', '.webp', '.txt', '.md', '.docx'}


class FileVault:
    def __init__(self, folder: str = ''):
        self.root = Path(folder).expanduser().resolve() if folder.strip() else None

    @property
    def enabled(self):
        return self.root is not None and self.root.is_dir()

    def _files(self):
        if not self.enabled:
            return
        visited = 0
        for folder, dirs, files in os.walk(self.root, followlinks=False):
            base = Path(folder)
            dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.startswith('.')
                             and self._inside(base / d))
            for name in sorted(files):
                visited += 1
                if visited > MAX_FILES:
                    yield None
                    return
                path = base / name
                if (name.startswith('.') or path.suffix.lower() not in EXTENSIONS
                        or MazCore._secret_name(path) or not self._inside(path)):
                    continue
                try:
                    if not path.is_file() or path.stat().st_size > MAX_BYTES:
                        continue
                except OSError:
                    continue
                relative = path.relative_to(self.root).as_posix()
                ident = hashlib.sha256(relative.encode('utf-8')).hexdigest()[:24]
                yield ident, path, relative

    def _inside(self, path):
        try:
            # Reject symlinks and Windows junctions rather than following them.
            if path.is_symlink() or getattr(path.lstat(), 'st_file_attributes', 0) & 0x400:
                return False
            path.resolve().relative_to(self.root)
            return True
        except (OSError, ValueError):
            return False

    def search(self, query=''):
        terms = re.findall(r'\w+', query.casefold())
        matches = []
        truncated = False
        for entry in self._files():
            if entry is None:
                truncated = True
                break
            ident, path, relative = entry
            words = ' '.join(re.findall(r'\w+', path.name.casefold()))
            if all(term in words for term in terms):
                try:
                    size = path.stat().st_size
                except OSError:
                    continue
                matches.append({'id': ident, 'name': path.name, 'path': relative,
                                'mime': mimetypes.guess_type(path.name)[0] or 'application/octet-stream',
                                'size': size})
                if len(matches) == 21:
                    truncated = True
                    break
        return {'enabled': self.enabled, 'files': matches[:20], 'truncated': truncated}

    def resolve(self, ident):
        if not re.fullmatch(r'[0-9a-f]{24}', ident):
            raise FileNotFoundError
        for entry in self._files():
            if entry is None:
                break
            file_id, path, _ = entry
            if ident == file_id:
                return path
        raise FileNotFoundError

    def fetch(self, ident):
        path = self.resolve(ident)
        with path.open('rb') as source:
            # Verify the opened handle, not a pathname another process can swap.
            if os.name == 'nt':
                import ctypes
                import msvcrt
                from ctypes import wintypes
                get_path = ctypes.WinDLL('kernel32', use_last_error=True).GetFinalPathNameByHandleW
                get_path.argtypes = [wintypes.HANDLE, wintypes.LPWSTR, wintypes.DWORD, wintypes.DWORD]
                get_path.restype = wintypes.DWORD
                buffer = ctypes.create_unicode_buffer(32768)
                length = get_path(msvcrt.get_osfhandle(source.fileno()), buffer, len(buffer), 0)
                if not length or length >= len(buffer):
                    raise OSError('cannot_verify_file_handle')
                final = buffer.value
                if final.startswith('\\\\?\\UNC\\'):
                    final = '\\\\' + final[8:]
                elif final.startswith('\\\\?\\'):
                    final = final[4:]
            else:
                final = os.readlink(f'/proc/self/fd/{source.fileno()}')
            Path(final).relative_to(self.root)
            if os.fstat(source.fileno()).st_size > MAX_BYTES:
                raise ValueError('file_too_large')
            content = source.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise ValueError('file_too_large')
        return {'name': path.name, 'mime': mimetypes.guess_type(path.name)[0] or 'application/octet-stream',
                'content_base64': base64.b64encode(content).decode('ascii')}


def build_vault_router(vault: FileVault):
    router = APIRouter(prefix='/vault', tags=['vault'])

    @router.get('')
    def search(q: str = Query('', max_length=200)):
        return vault.search(q)

    @router.get('/{ident}')
    def fetch(ident: str):
        try:
            return vault.fetch(ident)
        except FileNotFoundError:
            raise HTTPException(404, 'vault_file_not_found') from None
        except (OSError, ValueError):
            raise HTTPException(503, 'vault_file_unavailable') from None

    return router
