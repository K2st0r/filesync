#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================
FileSync Pro v2.1 — Smart File Sync & Incremental Backup Tool
   智能文件同步与增量备份工具
=============================================================
Category:   CLI Tool
License:    MIT
Donate:     0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697 (ETH/USDT)
=============================================================
Features:
  - Directory mirroring (one-way sync)
  - Incremental backup with timestamps
  - MD5 integrity verification — skip unchanged files
  - Dry-run preview mode
  - Cleanup mode (delete extra files in destination)
  - fnmatch ignore patterns (glob-style)
  - Detailed sync report generation
  - Cross-platform — Windows / macOS / Linux
  - Zero external dependencies (pure Python stdlib)
=============================================================
"""
import argparse
import fnmatch
import hashlib
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.stdout.reconfigure(encoding="utf-8")

__version__ = "2.1.0"
__wallet__  = "0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697"

# Default ignore patterns
DEFAULT_IGNORE = [".git", "__pycache__", ".DS_Store", "*.pyc", ".idea", "node_modules", ".env"]


class FileSync:
    """
    Smart file sync and incremental backup tool.

    Usage::

        fs = FileSync()
        fs.sync("/source", "/destination")
        fs.backup("/project", "/backups")

    Parameters:
        dry_run: If ``True``, only preview — no actual writes.
        verbose: If ``False``, suppress console output.
    """

    def __init__(self, dry_run: bool = False, verbose: bool = True) -> None:
        self.dry_run = dry_run
        self.verbose = verbose
        self._log: List[str] = []
        self.stats: Dict[str, int] = {
            "copied": 0, "updated": 0, "deleted": 0,
            "skipped": 0, "errors": 0,
        }

    # ── Internal ────────────────────────────────────────

    @staticmethod
    def _md5(filepath: Path, chunk_size: int = 8192) -> Optional[str]:
        """Compute MD5 hash of a file. Returns ``None`` on error."""
        try:
            h = hashlib.md5()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    h.update(chunk)
            return h.hexdigest()
        except (OSError, PermissionError):
            return None

    def _log_action(self, action: str, path: str) -> None:
        ts = datetime.now().strftime("%H:%M:%S")
        self._log.append(f"[{ts}] [{action}] {path}")
        if self.verbose:
            print(f"  {action:<8} {path}")

    @staticmethod
    def _should_ignore(name: str, patterns: List[str]) -> bool:
        return any(fnmatch.fnmatch(name, pat) for pat in patterns)

    # ── Public API ──────────────────────────────────────

    def sync(self, src: str, dst: str,
             delete: bool = False,
             ignore: Optional[List[str]] = None) -> Dict[str, int]:
        """
        Mirror *src* directory to *dst*.

        Args:
            src:    Source directory path.
            dst:    Destination directory path.
            delete: If ``True``, remove files in *dst* not present in *src*.
            ignore: List of fnmatch patterns to skip (defaults to common VCS/IDE files).

        Returns:
            Stats dict: ``{copied, updated, deleted, skipped, errors}``.
        """
        src_path = Path(src).resolve()
        dst_path = Path(dst).resolve()
        patterns = ignore or DEFAULT_IGNORE

        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {src_path}")
        dst_path.mkdir(parents=True, exist_ok=True)

        mode_label = "[DRY RUN] " if self.dry_run else ""
        if self.verbose:
            print(f"\n{mode_label}Sync: {src_path} → {dst_path}")
            print("-" * 60)

        t0 = time.perf_counter()

        # Walk source
        for root, dirs, files in os.walk(src_path):
            rel = Path(root).relative_to(src_path)
            target_dir = dst_path / rel
            target_dir.mkdir(exist_ok=True)

            dirs[:] = [d for d in dirs if not self._should_ignore(d, patterns)]

            for filename in files:
                if self._should_ignore(filename, patterns):
                    continue

                src_file = Path(root) / filename
                dst_file = target_dir / filename

                try:
                    src_hash = self._md5(src_file)
                    if src_hash is None:
                        self.stats["errors"] += 1
                        continue

                    if not dst_file.exists():
                        if not self.dry_run:
                            shutil.copy2(src_file, dst_file)
                        self.stats["copied"] += 1
                        self._log_action("COPY", str(src_file))
                    else:
                        dst_hash = self._md5(dst_file)
                        if src_hash != dst_hash:
                            if not self.dry_run:
                                shutil.copy2(src_file, dst_file)
                            self.stats["updated"] += 1
                            self._log_action("UPDATE", str(src_file))
                        else:
                            self.stats["skipped"] += 1
                except Exception as exc:
                    self.stats["errors"] += 1
                    self._log_action("ERROR", f"{src_file} ({exc})")

        # Delete extras in destination
        if delete:
            for root, dirs, files in os.walk(dst_path):
                rel = Path(root).relative_to(dst_path)
                src_dir = src_path / rel
                if not src_dir.exists():
                    if not self.dry_run:
                        shutil.rmtree(root)
                    self._log_action("DEL_DIR", str(root))
                    continue
                src_filenames = {f.name for f in src_dir.iterdir() if f.is_file()}
                for f in files:
                    if f not in src_filenames and not self._should_ignore(f, patterns):
                        fpath = Path(root) / f
                        if not self.dry_run:
                            fpath.unlink()
                        self.stats["deleted"] += 1
                        self._log_action("DELETE", str(fpath))

        elapsed = time.perf_counter() - t0
        if self.verbose:
            print("-" * 60)
            print(f"  Done in {elapsed:.1f}s | "
                  f"Copy:{self.stats['copied']} Update:{self.stats['updated']} "
                  f"Delete:{self.stats['deleted']} Skip:{self.stats['skipped']} "
                  f"Error:{self.stats['errors']}")

        return self.stats

    def backup(self, src: str, dst_dir: str,
               suffix: Optional[str] = None) -> Dict[str, int]:
        """
        Create a timestamped backup of *src* inside *dst_dir*.

        Args:
            src:     Source directory.
            dst_dir: Parent backup directory.
            suffix:  Custom suffix (default: ``YYYYMMDD_HHMMSS``).

        Returns:
            Stats dict.
        """
        ts = suffix or datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = Path(dst_dir) / f"backup_{ts}"
        return self.sync(src, str(backup_path))

    def generate_report(self) -> str:
        """Generate a formatted sync report."""
        lines = [
            f"FileSync Pro v{__version__} — Sync Report",
            "=" * 55,
            f"Time:  {datetime.now().isoformat()}",
            f"Stats: Copy={self.stats['copied']} Update={self.stats['updated']} "
            f"Delete={self.stats['deleted']} Skip={self.stats['skipped']} "
            f"Error={self.stats['errors']}",
            "=" * 55,
            "Operations:",
        ]
        lines.extend(self._log)
        return "\n".join(lines)


# ─── CLI Interface (参考 rsync 风格) ────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="filesync",
        description=f"FileSync Pro v{__version__} — Smart file sync & backup",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  filesync.py /source /dest                       # Mirror sync
  filesync.py /source /dest --delete              # Sync + remove extra files
  filesync.py /source /dest --dry-run             # Preview only
  filesync.py /project /backups --backup          # Timestamped backup
  filesync.py /project /backups --backup v1.0     # Named backup
  filesync.py /src /dst --ignore "*.log" "*.tmp"  # Custom ignore
        """
    )
    p.add_argument("src", help="Source directory")
    p.add_argument("dst", help="Destination (or backup parent dir)")
    p.add_argument("--backup", "-b", nargs="?", const=True, metavar="SUFFIX",
                   help="Create timestamped backup (optional custom suffix)")
    p.add_argument("--delete", "-d", action="store_true",
                   help="Delete extra files in destination")
    p.add_argument("--dry-run", "-n", action="store_true",
                   help="Preview without writing")
    p.add_argument("--ignore", nargs="+", metavar="PATTERN",
                   help="Additional ignore patterns")
    p.add_argument("--quiet", "-q", action="store_true",
                   help="Suppress progress output")
    p.add_argument("--report", "-r", metavar="FILE",
                   help="Save sync report to file")
    p.add_argument("--version", action="version",
                   version=f"%(prog)s {__version__}")
    return p


def main() -> None:
    args = build_parser().parse_args()

    fs = FileSync(dry_run=args.dry_run, verbose=not args.quiet)
    ignore = (DEFAULT_IGNORE + args.ignore) if args.ignore else DEFAULT_IGNORE

    if args.backup is True:
        # Auto timestamp
        stats = fs.backup(args.src, args.dst)
    elif isinstance(args.backup, str):
        stats = fs.backup(args.src, args.dst, suffix=args.backup)
    else:
        stats = fs.sync(args.src, args.dst, delete=args.delete, ignore=ignore)

    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(fs.generate_report())
        print(f"  Report saved to: {args.report}")

    print(f"  Donate: {__wallet__} (USDT/ERC20)\n")


if __name__ == "__main__":
    main()
