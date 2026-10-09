"""
知识库管理器 - 整合哈希检测、特征工程和检索
"""
import sys
from pathlib import Path
from typing import Dict, List, Any

project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from MyKnownlege.knowledge_base_v2.src.hash_checker import HashChecker
from MyKnownlege.knowledge_base_v2.src.feature_engineering import FeatureEngineer
from MyKnownlege.knowledge_base_v2.src.retriever_v2 import MultiLayerRetriever, RetrievalResult
from optimized_system_v2.core.utils.config import config


class KnowledgeBaseManager:
    """知识库管理器"""
    
    def __init__(self):
        self.hash_checker = None
        self.feature_engineer = None
        self.retriever = None
        self.is_initialized = False
        self.system_check_log = []
        
    def _log(self, message: str):
        """记录系统自检日志"""
        print(message)
        self.system_check_log.append(message)
        
    def initialize(self, force_rebuild: bool = False) -> Dict[str, Any]:
        """
        初始化知识库系统
        
        Args:
            force_rebuild: 是否强制重建索引
            
        Returns:
            初始化结果
        """
        self._log("=" * 80)
        self._log("📚 知识库系统初始化")
        self._log("=" * 80)
        
        result = {
            "success": False,
            "steps": [],
            "errors": []
        }
        
        try:
            # 步骤1: 哈希变更检测
            self._log("\n[步骤 1/4] 知识库变更检测")
            self._log("-" * 80)
            self.hash_checker = HashChecker()
            change_result = self.hash_checker.check_changes()
            
            result["steps"].append({
                "name": "知识库变更检测",
                "result": change_result
            })
            
            need_rebuild = change_result["need_rebuild"] or force_rebuild
            
            # 步骤2: 特征工程与索引构建
            if need_rebuild:
                self._log("\n[步骤 2/4] 特征工程与索引构建")
                self._log("-" * 80)
                self.feature_engineer = FeatureEngineer()
                fe_result = self.feature_engineer.run_feature_engineering(
                    change_result["current_manifest"]["file_list"]
                )
                self.hash_checker.save_current_manifest()
                
                result["steps"].append({
                    "name": "特征工程与索引构建",
                    "result": fe_result
                })
            else:
                self._log("\n[步骤 2/4] 加载现有索引")
                self._log("-" * 80)
                self.feature_engineer = FeatureEngineer()
                result["steps"].append({
                    "name": "加载现有索引",
                    "status": "skipped - 无变更"
                })
            
            # 步骤3: 初始化检索引擎
            self._log("\n[步骤 3/4] 初始化检索引擎")
            self._log("-" * 80)
            self.retriever = MultiLayerRetriever()
            
            result["steps"].append({
                "name": "初始化检索引擎",
                "status": "completed"
            })
            
            self.is_initialized = True
            result["success"] = True
            
            self._log("\n" + "=" * 80)
            self._log("✅ 知识库系统初始化完成!")
            self._log("=" * 80)
            
        except Exception as e:
            self._log(f"\n❌ 知识库初始化失败: {str(e)}")
            result["errors"].append(str(e))
            import traceback
            self._log(traceback.format_exc())
            
        return result
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        执行检索
        
        Args:
            query: 查询文本
            
        Returns:
            检索结果列表
        """
        if not self.is_initialized or not self.retriever:
            self._log("⚠️  知识库未初始化，先执行初始化")
            self.initialize()
        
        self._log(f"\n🔍 执行检索: {query}")
        self._log("-" * 80)
        
        results = self.retriever.retrieve(query)
        
        formatted_results = []
        for i, result in enumerate(results, 1):
            result_dict = {
                "rank": i,
                "segment_id": result.segment_id,
                "file_id": result.file_id,
                "file_path": result.file_path,
                "content": result.content,
                "score": result.score,
                "evidence_level": result.evidence_level,
                "tags": result.tags,
                "source_type": result.source_type
            }
            formatted_results.append(result_dict)
            
            self._log(f"\n{i}. [{result.evidence_level}] {result.file_path}")
            self._log(f"   分数: {result.score:.3f}")
            self._log(f"   标签: {', '.join(result.tags[:5])}")
            self._log(f"   内容片段: {result.content[:120]}...")
        
        return formatted_results
    
    def get_system_check_log(self) -> List[str]:
        """获取系统自检日志"""
        return self.system_check_log
    
    def save_system_check_report(self, output_path: Path = None):
        """保存系统自检报告"""
        if output_path is None:
            output_path = config.paths.system_check_output / "知识库自检报告.md"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# 知识库系统自检报告\n\n")
            f.write(f"生成时间: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## 详细日志\n\n")
            for line in self.system_check_log:
                f.write(f"{line}\n")
        
        self._log(f"\n📄 自检报告已保存到: {output_path}")
        return output_path
