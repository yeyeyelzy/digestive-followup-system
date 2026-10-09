"""
知识库哈希变更检测模块
实现系统启动时的知识库变更自动识别
"""
import hashlib
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import yaml
from tqdm import tqdm

import sys
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from MyKnownlege.knowledge_base_v2.config.settings import config


class HashChecker:
    """知识库哈希变更检测器"""
    
    def __init__(self, config_instance=None):
        """
        初始化哈希检测器
        
        Args:
            config_instance: 配置实例，默认使用全局配置
        """
        self.config = config_instance or config
        self.hash_manifest_path = self.config.paths.kb_hash_manifest
        self.current_manifest: Dict = {}
        self.old_manifest: Dict = {}
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """
        计算文件的SHA-256哈希值
        
        Args:
            file_path: 文件路径
            
        Returns:
            SHA-256哈希值（十六进制字符串）
        """
        hash_sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(self.config.hash.chunk_size), b''):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            print(f"⚠️  计算哈希失败 {file_path}: {e}")
            return ""
    
    def get_file_tags(self, file_path: Path) -> List[str]:
        """
        基于文件路径和内容提取标签
        
        Args:
            file_path: 文件路径
            
        Returns:
            标签列表
        """
        tags = []
        path_str = str(file_path).lower()
        
        # 基于目录提取标签
        if "rag" in path_str:
            tags.append("医学指南")
        if "药物" in path_str or "drug" in path_str:
            tags.append("药物知识")
        if "冠心病" in path_str:
            tags.append("冠心病")
        if "心衰" in path_str or "heart" in path_str:
            tags.append("心力衰竭")
        if "康复" in path_str:
            tags.append("康复医学")
        if "运动" in path_str:
            tags.append("运动康复")
        if "饮食" in path_str:
            tags.append("饮食管理")
        
        # 基于文件类型
        if file_path.suffix.lower() == '.pdf':
            tags.append("PDF文档")
        elif file_path.suffix.lower() in ['.json', '.jsonl']:
            tags.append("结构化数据")
        elif file_path.suffix.lower() == '.md':
            tags.append("Markdown文档")
        elif file_path.suffix.lower() in ['.csv', '.xlsx']:
            tags.append("表格数据")
        
        return tags
    
    def scan_knowledge_base(self) -> Dict:
        """
        扫描知识库，生成当前哈希清单
        
        Returns:
            当前哈希清单字典
        """
        print("=" * 70)
        print("📚 扫描知识库")
        print("=" * 70)
        
        manifest = {
            "kb_version": "v2.0.0",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "base_path": str(self.config.paths.raw_data_dir),
            "file_list": []
        }
        
        # 扫描所有支持的文件类型
        raw_dir = self.config.paths.raw_data_dir
        files_found = 0
        
        for ext in tqdm(self.config.hash.supported_file_types, desc="扫描文件类型"):
            pattern = f"**/*.{ext}"
            for file_path in raw_dir.glob(pattern):
                if file_path.is_file():
                    files_found += 1
                    
                    # 计算相对路径
                    rel_path = file_path.relative_to(raw_dir)
                    
                    # 计算哈希
                    file_hash = self.calculate_file_hash(file_path)
                    
                    # 获取标签
                    tags = self.get_file_tags(file_path)
                    
                    # 获取修改时间
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    file_info = {
                        "file_path": str(rel_path),
                        "file_type": ext,
                        "file_tag": tags,
                        "sha256": file_hash,
                        "last_modified": mtime.strftime("%Y-%m-%d %H:%M:%S"),
                        "file_size": file_path.stat().st_size,
                        "processed_status": "pending"
                    }
                    
                    manifest["file_list"].append(file_info)
        
        print(f"✓ 扫描完成，共发现 {files_found} 个文件")
        self.current_manifest = manifest
        return manifest
    
    def load_old_manifest(self) -> Optional[Dict]:
        """
        加载旧的哈希清单
        
        Returns:
            旧的哈希清单，如果不存在则返回None
        """
        if not self.hash_manifest_path.exists():
            print("⚠️  未找到旧的哈希清单，首次运行")
            return None
        
        try:
            with open(self.hash_manifest_path, 'r', encoding='utf-8') as f:
                self.old_manifest = yaml.safe_load(f)
            print(f"✓ 加载旧的哈希清单 (版本: {self.old_manifest.get('kb_version', 'unknown')})")
            return self.old_manifest
        except Exception as e:
            print(f"⚠️  加载旧哈希清单失败: {e}")
            return None
    
    def compare_manifests(self) -> Tuple[List[Dict], List[Dict], List[Dict]]:
        """
        比较新旧哈希清单，找出变更的文件
        
        Returns:
            (新增文件列表, 修改文件列表, 删除文件列表)
        """
        if not self.old_manifest or "file_list" not in self.old_manifest:
            # 首次运行，所有文件都是新增
            return self.current_manifest.get("file_list", []), [], []
        
        old_files = {f["file_path"]: f for f in self.old_manifest.get("file_list", [])}
        new_files = {f["file_path"]: f for f in self.current_manifest.get("file_list", [])}
        
        added = []
        modified = []
        deleted = []
        
        # 检查新增和修改的文件
        for path, file_info in new_files.items():
            if path not in old_files:
                added.append(file_info)
            else:
                old_hash = old_files[path].get("sha256", "")
                new_hash = file_info.get("sha256", "")
                if old_hash != new_hash:
                    modified.append(file_info)
        
        # 检查删除的文件
        for path in old_files:
            if path not in new_files:
                deleted.append(old_files[path])
        
        return added, modified, deleted
    
    def save_current_manifest(self):
        """保存当前哈希清单到文件"""
        try:
            # 更新处理状态
            for file_info in self.current_manifest.get("file_list", []):
                file_info["processed_status"] = "completed"
            
            self.current_manifest["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            with open(self.hash_manifest_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.current_manifest, f, allow_unicode=True, default_flow_style=False)
            
            print(f"✓ 哈希清单已保存到 {self.hash_manifest_path}")
        except Exception as e:
            print(f"❌ 保存哈希清单失败: {e}")
    
    def check_changes(self) -> Dict:
        """
        执行完整的变更检测流程
        
        Returns:
            变更检测结果字典
        """
        print("\n" + "=" * 70)
        print("🔍 知识库变更检测")
        print("=" * 70)
        
        # 1. 扫描当前知识库
        self.scan_knowledge_base()
        
        # 2. 加载旧清单
        self.load_old_manifest()
        
        # 3. 比较变更
        added, modified, deleted = self.compare_manifests()
        
        # 4. 输出结果
        print("\n📊 变更统计:")
        print(f"  - 新增文件: {len(added)}")
        print(f"  - 修改文件: {len(modified)}")
        print(f"  - 删除文件: {len(deleted)}")
        
        if added:
            print("\n📄 新增文件:")
            for f in added[:5]:  # 最多显示5个
                print(f"  + {f['file_path']}")
            if len(added) > 5:
                print(f"  ... 还有 {len(added) - 5} 个文件")
        
        if modified:
            print("\n✏️  修改文件:")
            for f in modified[:5]:
                print(f"  * {f['file_path']}")
            if len(modified) > 5:
                print(f"  ... 还有 {len(modified) - 5} 个文件")
        
        if deleted:
            print("\n🗑️  删除文件:")
            for f in deleted[:5]:
                print(f"  - {f['file_path']}")
            if len(deleted) > 5:
                print(f"  ... 还有 {len(deleted) - 5} 个文件")
        
        # 5. 判断是否需要更新索引
        total_changes = len(added) + len(modified) + len(deleted)
        need_rebuild = total_changes > 0
        need_full_rebuild = total_changes >= len(self.current_manifest.get("file_list", [])) * 0.3  # 变更超过30%
        
        result = {
            "added": added,
            "modified": modified,
            "deleted": deleted,
            "total_changes": total_changes,
            "need_rebuild": need_rebuild,
            "need_full_rebuild": need_full_rebuild,
            "current_manifest": self.current_manifest
        }
        
        print("\n" + "=" * 70)
        if need_rebuild:
            if need_full_rebuild:
                print("⚠️  检测到大规模变更，建议全量重建索引")
            else:
                print("🔄 检测到变更，需要更新索引")
        else:
            print("✅ 知识库无变更，可直接使用现有索引")
        print("=" * 70)
        
        return result


def main():
    """测试哈希变更检测"""
    checker = HashChecker()
    result = checker.check_changes()
    
    # 保存新的清单
    if result["need_rebuild"]:
        checker.save_current_manifest()


if __name__ == "__main__":
    main()
