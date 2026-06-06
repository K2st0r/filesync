<div align="center">

# FileSync Pro

**Smart File Sync & Incremental Backup Tool**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-2.1.0-purple.svg)](https://github.com/K2st0r/filesync/releases)
[![Donate](https://img.shields.io/badge/Donate-USDT-red.svg)](#donate)

</div>

---

## Table of Contents

- [English](#english)
- [中文](#chinese)
- [Donate / 打赏](#donate--打赏)

---

## English

### What is FileSync Pro?

FileSync Pro is a **command-line tool and Python library** for directory mirroring and incremental backups. It uses **MD5 checksums** to skip unchanged files — making sync operations fast even on large directories. Think of it as a lightweight, cross-platform alternative to `rsync` with built-in backup timestamping.

### Features

| Category | Description |
|----------|-------------|
| **Directory Mirror** | One-way sync: source → destination |
| **Incremental Backup** | Auto-timestamped backups (or custom suffix) |
| **MD5 Verification** | Skip files with identical content — huge speed gains |
| **Dry-Run Mode** | Preview what would happen, without writing |
| **Cleanup** | Optionally delete destination files not present in source |
| **Ignore Patterns** | Glob/fnmatch patterns: `.git`, `*.pyc`, `node_modules`, etc. |
| **Sync Reports** | Detailed operation logs, saveable to file |
| **Cross-Platform** | Windows / macOS / Linux — pure Python, no dependencies |
| **Zero Deps** | Standard library only — works on a fresh Python install |

### Installation

```bash
git clone https://github.com/K2st0r/filesync.git
cd filesync
# Zero dependencies — ready to use!
```

### CLI Usage

```bash
# Basic sync
python filesync.py /path/source /path/destination

# Sync + delete extra files in destination
python filesync.py /source /dest --delete

# Preview (dry-run) — no actual writes
python filesync.py /source /dest --dry-run

# Timestamped backup
python filesync.py /project /backups --backup
# Creates: /backups/backup_20260606_160000/

# Named backup
python filesync.py /project /backups --backup v1.0-release
# Creates: /backups/backup_v1.0-release/

# Custom ignore patterns
python filesync.py /src /dst --ignore "*.log" "*.tmp" ".venv"

# Quiet mode + save report
python filesync.py /src /dst --quiet --report sync_report.txt

# Help
python filesync.py --help
```

### Python API

```python
from filesync import FileSync

# Basic sync
fs = FileSync()
fs.sync("/source", "/destination")

# Dry-run preview
fs_dry = FileSync(dry_run=True)
fs_dry.sync("/source", "/dest")

# Incremental backup
fs.backup("/project", "/backups")
fs.backup("/project", "/backups", suffix="v2.0")

# Sync with cleanup
fs.sync("/source", "/dest", delete=True)

# Custom ignore
fs.sync("/src", "/dst", ignore=[".git", "*.pyc", "*.log", "node_modules"])

# Get a report
report = fs.generate_report()
print(report)
```

---

## 中文

### 概述

FileSync Pro 是一个**命令行工具和 Python 库**，用于目录镜像同步和增量备份。通过 MD5 校验跳过未修改的文件，大规模目录也很快。可以理解为轻量级跨平台 `rsync`。

### 安装

```bash
git clone https://github.com/K2st0r/filesync.git
cd filesync
# 零依赖 — 开箱即用！
```

### CLI 命令

```bash
python filesync.py /source /dest                   # 基本同步
python filesync.py /source /dest --delete          # 同步 + 删除目标多余文件
python filesync.py /source /dest --dry-run         # 试运行预览
python filesync.py /project /backups --backup      # 自动时间戳备份
python filesync.py /project /backups --backup v2.0 # 命名备份
python filesync.py /src /dst --ignore "*.log" "*.tmp"  # 自定义忽略
python filesync.py /src /dst --quiet --report report.txt  # 静默 + 报告
```

### Python API

```python
from filesync import FileSync

fs = FileSync()
fs.sync("/source", "/destination")
fs.backup("/project", "/backups")
stats = fs.sync("/src", "/dst", delete=True)
print(f"复制:{stats['copied']} 更新:{stats['updated']} 删除:{stats['deleted']}")
```

### 默认忽略

`.git`, `__pycache__`, `.DS_Store`, `*.pyc`, `.idea`, `node_modules`, `.env`

---

## Donate / 打赏

<div align="center">
<img src="https://raw.githubusercontent.com/K2st0r/filesync/main/static/zan.png" width="200" alt="WeChat Pay">

📱 微信扫码赞赏

**USDT (ERC20):** `0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697`

</div>

---

MIT License · Made with ❤️ by [K2st0r](https://github.com/K2st0r)
