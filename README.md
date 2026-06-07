<div align="center">

# FileSync Pro

**Smart Directory Sync + Incremental Backup — MD5-powered, cross-platform**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.1.0-purple.svg)](https://github.com/K2st0r/filesync/releases)
[![Donate](https://img.shields.io/badge/Donate-USDT-red.svg)](#donate)

</div>

### 🎯 One-liner

```bash
python filesync.py /projects /backup --backup
# → Copies only changed files. MD5-verified. Done.
```

### ✨ Features

| Feature | Description |
|---------|-------------|
| **MD5 Verification** | Only copy files whose hash differs — fast on large dirs |
| **Dry-run Mode** | Preview what would be copied/deleted without touching files |
| **Incremental Backup** | Timestamped backup folders: `/backup/2026-06-07_1030/` |
| **Glob Ignore** | Skip patterns like `*.pyc`, `.git`, `node_modules` |
| **Cleanup Mode** | Remove files in dest that don't exist in source (true mirror) |
| **Zero Deps** | Pure Python stdlib — no pip install needed |
| **Cross-platform** | Windows / macOS / Linux |

### 🚀 Usage

**CLI — sync directory:**

```bash
# Basic sync (copy new/changed files)
python filesync.py /source /destination

# Dry-run — see what would happen
python filesync.py /source /destination --dry-run

# Backup mode — timestamped snapshot
python filesync.py /projects /backups --backup
# → /backups/2026-06-07_103000/projects/...

# Full mirror — also delete extra files in dest
python filesync.py /source /destination --cleanup
```

**Python API:**

```python
from filesync import FileSync

# Sync with report
fs = FileSync()
report = fs.sync("/source", "/destination")
print(f"Copied: {report['copied']}, Updated: {report['updated']}, "
      f"Deleted: {report['deleted']}, Skipped: {report['skipped']}")

# Backup with timestamp
fs = FileSync(verbose=False)
fs.backup("/important_data", "/backup_drive")
```

**Output:**
```
Sync: /projects → /backup/projects
────────────────────────────────────
  COPY     /projects/main.py
  UPDATE   /projects/config.json
  SKIP     /projects/logo.png (unchanged)
────────────────────────────────────
  Done in 2.3s | Copy:2 Update:1 Delete:0 Skip:47 Error:0
```

### 🆚 vs Alternatives

| | **FileSync Pro** | rsync | robocopy | FreeFileSync |
|---|---|---|---|---|
| Platform | Any | Linux/Mac | Windows | Any (GUI) |
| Install | **Python = installed** | System pkg | Built-in | Download |
| MD5 skip | ✅ | ❌ (date/size) | ❌ (date/size) | ✅ |
| Dry-run | ✅ | ✅ `--dry-run` | ❌ `/L` limited | ✅ |
| Backup | ✅ Timestamped | ❌ | ❌ | ✅ |
| Scriptable | ✅ Python API | ⚠️ Shell | ⚠️ Batch | ❌ |

## 💎 Donate

**USDT (ERC20):** `0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697`

---

*MIT License · Made with ❤️ by [K2st0r](https://github.com/K2st0r)*
