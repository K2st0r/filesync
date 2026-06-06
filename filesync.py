#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FileSync Pro v1.0 - 智能文件同步工具
==============================================
功能: 目录同步、增量备份、冲突处理、日志记录
特点: 纯Python实现，无需外网，即开即用
打赏: 0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697 (ETH/USDT)
==============================================
"""
import os
import shutil
import hashlib
import json
import time
from datetime import datetime
from pathlib import Path

__version__ = "1.0.0"
__wallet__ = "0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697"

class FileSync:
    """智能文件同步工具"""
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run
        self.log = []
        self.stats = {"copied": 0, "updated": 0, "deleted": 0, "skipped": 0}
    
    def _md5(self, path):
        """计算文件MD5"""
        h = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                h.update(chunk)
        return h.hexdigest()
    
    def _log(self, action, path):
        self.log.append(f"[{action}] {path}")
        if not self.dry_run:
            print(f"  {action}: {path}")
    
    def sync(self, src, dst, delete=False, ignore=None):
        """
        同步目录
        
        Args:
            src: 源目录
            dst: 目标目录
            delete: 是否删除目标端多余文件
            ignore: 忽略的文件列表 ['.git', '__pycache__', '.DS_Store']
        """
        src = Path(src)
        dst = Path(dst)
        ignore = ignore or ['.git', '__pycache__', '.DS_Store', '*.pyc']
        
        if not src.exists():
            raise FileNotFoundError(f"源目录不存在: {src}")
        
        dst.mkdir(parents=True, exist_ok=True)
        
        print(f"同步: {src} -> {dst}")
        if self.dry_run:
            print("[模拟运行模式]")
        
        t0 = time.time()
        
        # 遍历源目录
        for root, dirs, files in os.walk(src):
            rel = Path(root).relative_to(src)
            target_dir = dst / rel
            target_dir.mkdir(exist_ok=True)
            
            # 过滤忽略目录
            dirs[:] = [d for d in dirs if d not in ignore]
            
            for f in files:
                src_file = Path(root) / f
                
                # 忽略匹配的文件
                if any(f.endswith(ext.replace('*', '')) for ext in ignore if ext.startswith('*')):
                    continue
                if f in ignore:
                    continue
                
                dst_file = target_dir / f
                
                if not dst_file.exists():
                    if not self.dry_run:
                        shutil.copy2(src_file, dst_file)
                    self.stats["copied"] += 1
                    self._log("COPY", str(src_file))
                else:
                    src_md5 = self._md5(src_file)
                    dst_md5 = self._md5(dst_file)
                    if src_md5 != dst_md5:
                        if not self.dry_run:
                            shutil.copy2(src_file, dst_file)
                        self.stats["updated"] += 1
                        self._log("UPDATE", str(src_file))
                    else:
                        self.stats["skipped"] += 1
        
        # 删除目标端多余文件
        if delete:
            for root, dirs, files in os.walk(dst):
                rel = Path(root).relative_to(dst)
                src_dir = src / rel
                
                if not src_dir.exists():
                    if not self.dry_run:
                        shutil.rmtree(root)
                    self._log("DELETE_DIR", str(root))
                    continue
                
                src_files = {f.name for f in src_dir.iterdir() if f.is_file()}
                for f in files:
                    if f not in src_files:
                        dst_file = Path(root) / f
                        if not self.dry_run:
                            dst_file.unlink()
                        self.stats["deleted"] += 1
                        self._log("DELETE", str(dst_file))
        
        elapsed = time.time() - t0
        print(f"\n完成! 耗时: {elapsed:.1f}s")
        print(f"  复制: {self.stats['copied']}  更新: {self.stats['updated']}")
        print(f"  删除: {self.stats['deleted']}  跳过: {self.stats['skipped']}")
        
        return self.stats
    
    def backup(self, src, dst_dir, suffix=None):
        """增量备份（带时间戳）"""
        dst_dir = Path(dst_dir)
        ts = suffix or datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = dst_dir / f"backup_{ts}"
        return self.sync(src, backup_path)


if __name__ == "__main__":
    print(f"\nFileSync Pro v{__version__}")
    print(f"打赏: {__wallet__} (ETH/USDT)\n")
    print("使用方法:")
    print("  from filesync import FileSync")
    print("  fs = FileSync()")
    print("  fs.sync('/path/src', '/path/dst')\n")
