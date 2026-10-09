"""
多层级精准检索引擎V2.0
实现：标签前置过滤→关联文件召回→向量相似性检索→结果重排序
"""
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
import jieba
import jieba.analyse

import sys
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from MyKnownlege.knowledge_base_v2.config.settings import config


@dataclass
class RetrievalResult:
    """检索结果"""
    segment_id: str
    file_id: str
    file_path: str
    content: str
    score: float
    evidence_level: str
    tags: List[str]
    source_type: str  # tag_filter / relation / vector


class MultiLayerRetriever:
    """多层级精准检索器"""
    
    def __init__(self, config_instance=None):
        """
        初始化多层级检索器
        
        Args:
            config_instance: 配置实例
        """
        self.config = config_instance or config
        self.file_index: Dict = {}
        self.segment_index: Dict = {}
        self.tag_to_segments: Dict[str, List[str]] = {}
        self.question_to_segments: Dict[str, List[str]] = {}
        
        # 加载索引
        self._load_indexes()
        
        # 初始化jieba
        jieba.initialize()
        
        # 查询关键词提取器
        self.query_keywords = {
            "冠心病": ["冠心病", "冠脉", "PCI", "支架"],
            "心力衰竭": ["心衰", "心力衰竭", "心功能不全"],
            "高血压": ["高血压", "血压高"],
            "糖尿病": ["糖尿病", "血糖高"],
            "运动": ["运动", "锻炼", "活动", "康复训练"],
            "饮食": ["饮食", "吃", "食物", "营养"],
            "药物": ["药物", "吃药", "用药", "剂量"],
            "心率": ["心率", "心跳", "脉搏"],
            "风险": ["风险", "危险", "警告", "注意"],
            "康复": ["康复", "恢复", "术后"]
        }
    
    def _load_indexes(self):
        """加载索引文件"""
        print("=" * 70)
        print("📚 加载知识库索引")
        print("=" * 70)
        
        # 加载文件关联索引
        if self.config.paths.kb_file_relation_index.exists():
            try:
                with open(self.config.paths.kb_file_relation_index, 'r', encoding='utf-8') as f:
                    self.file_index = yaml.safe_load(f) or {}
                print(f"✓ 文件关联索引已加载 (版本: {self.file_index.get('version', 'unknown')})")
            except Exception as e:
                print(f"⚠️  加载文件关联索引失败: {e}")
        else:
            print("⚠️  未找到文件关联索引")
        
        # 加载片段特征索引
        if self.config.paths.kb_segment_feature_index.exists():
            try:
                with open(self.config.paths.kb_segment_feature_index, 'r', encoding='utf-8') as f:
                    seg_data = yaml.safe_load(f) or {}
                self.segment_index = seg_data.get("segments", {})
                self.tag_to_segments = seg_data.get("tag_to_segments", {})
                self.question_to_segments = seg_data.get("question_to_segments", {})
                print(f"✓ 片段特征索引已加载 (版本: {seg_data.get('version', 'unknown')})")
                print(f"  - 片段数量: {len(self.segment_index)}")
                print(f"  - 标签映射: {len(self.tag_to_segments)} 个标签")
            except Exception as e:
                print(f"⚠️  加载片段特征索引失败: {e}")
        else:
            print("⚠️  未找到片段特征索引")
        
        print("=" * 70)
    
    def extract_query_tags(self, query: str) -> List[str]:
        """
        从查询中提取标签
        
        Args:
            query: 用户查询
            
        Returns:
            标签列表
        """
        tags = []
        query_lower = query.lower()
        
        # 匹配关键词
        for category, keywords in self.query_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    tags.append(category)
                    tags.append(keyword)
                    break
        
        # 使用TF-IDF提取补充标签
        tfidf_tags = jieba.analyse.extract_tags(query, topK=10)
        for tag in tfidf_tags:
            if len(tag) >= 2 and tag not in tags:
                tags.append(tag)
        
        return list(set(tags))
    
    def layer1_tag_filter(self, query_tags: List[str]) -> List[str]:
        """
        第一层：标签前置过滤
        
        Args:
            query_tags: 查询标签
            
        Returns:
            匹配的片段ID列表
        """
        if not self.config.retrieval.enable_tag_filter:
            return list(self.segment_index.keys())
        
        matched_segments = set()
        
        for tag in query_tags:
            if tag in self.tag_to_segments:
                matched_segments.update(self.tag_to_segments[tag])
        
        # 同时匹配核心问题
        for question, segments in self.question_to_segments.items():
            for tag in query_tags:
                if tag in question:
                    matched_segments.update(segments)
                    break
        
        result = list(matched_segments)[:self.config.retrieval.top_k_tags]
        print(f"🔍 第一层 - 标签过滤: 匹配到 {len(result)} 个片段")
        return result
    
    def layer2_relation_recall(self, candidate_segments: List[str]) -> List[str]:
        """
        第二层：关联文件召回
        
        Args:
            candidate_segments: 候选片段ID列表
            
        Returns:
            扩展后的片段ID列表
        """
        if not self.config.retrieval.enable_relation_recall:
            return candidate_segments
        
        extended_segments = set(candidate_segments)
        
        # 收集涉及的文件
        file_ids = set()
        for seg_id in candidate_segments:
            if seg_id in self.segment_index:
                file_ids.add(self.segment_index[seg_id]["file_id"])
        
        # 召回关联文件的片段
        for file_id in file_ids:
            if file_id in self.file_index.get("files", {}):
                file_data = self.file_index["files"][file_id]
                for related_file in file_data.get("related_files", []):
                    related_file_id = related_file["file_id"]
                    # 查找该文件的所有片段
                    for seg_id, seg_data in self.segment_index.items():
                        if seg_data["file_id"] == related_file_id:
                            extended_segments.add(seg_id)
        
        result = list(extended_segments)[:self.config.retrieval.top_k_tags + self.config.retrieval.top_k_relations]
        print(f"🔗 第二层 - 关联召回: 扩展到 {len(result)} 个片段")
        return result
    
    def layer3_vector_search(self, query: str, candidate_segments: List[str]) -> List[Tuple[str, float]]:
        """
        第三层：向量相似性检索（简化版，使用词频匹配）
        
        Args:
            query: 用户查询
            candidate_segments: 候选片段ID列表
            
        Returns:
            (片段ID, 相似度) 列表
        """
        if not self.config.retrieval.enable_vector_search:
            return [(seg_id, 1.0) for seg_id in candidate_segments[:self.config.retrieval.top_k_vectors]]
        
        # 提取查询关键词
        query_words = set(jieba.lcut(query))
        
        scored_segments = []
        
        for seg_id in candidate_segments:
            if seg_id not in self.segment_index:
                continue
            
            seg_data = self.segment_index[seg_id]
            content = seg_data["content"]
            
            # 简单词频匹配作为相似度（实际应使用向量模型）
            content_words = set(jieba.lcut(content))
            intersection = query_words & content_words
            union = query_words | content_words
            
            if union:
                similarity = len(intersection) / len(union)
            else:
                similarity = 0.0
            
            # 标签匹配加分
            tag_match = 0
            seg_tags = set(seg_data.get("fine_grained_tags", []))
            for word in query_words:
                if word in seg_tags:
                    tag_match += 0.1
            
            similarity = min(similarity + tag_match, 1.0)
            scored_segments.append((seg_id, similarity))
        
        # 按相似度排序
        scored_segments.sort(key=lambda x: x[1], reverse=True)
        result = scored_segments[:self.config.retrieval.top_k_vectors]
        
        print(f"🎯 第三层 - 向量检索: Top-{len(result)} 相关片段")
        if result:
            print(f"  最高相似度: {result[0][1]:.3f}")
        
        return result
    
    def layer4_rerank(self, scored_segments: List[Tuple[str, float]]) -> List[RetrievalResult]:
        """
        第四层：结果重排序与校验
        
        Args:
            scored_segments: 带分数的片段列表
            
        Returns:
            重排序后的检索结果列表
        """
        if not self.config.retrieval.enable_rerank:
            results = []
            for seg_id, score in scored_segments[:self.config.retrieval.top_k_final]:
                if seg_id in self.segment_index:
                    seg_data = self.segment_index[seg_id]
                    results.append(RetrievalResult(
                        segment_id=seg_id,
                        file_id=seg_data["file_id"],
                        file_path=seg_data["parent_file_path"],
                        content=seg_data["content"],
                        score=score,
                        evidence_level=seg_data.get("evidence_level", "C级"),
                        tags=seg_data.get("fine_grained_tags", []),
                        source_type="vector"
                    ))
            return results
        
        reranked = []
        
        for seg_id, base_score in scored_segments:
            if seg_id not in self.segment_index:
                continue
            
            seg_data = self.segment_index[seg_id]
            
            # 证据等级权重
            evidence_weight = {
                "A级": 1.0,
                "B级": 0.8,
                "C级": 0.6
            }
            weight = evidence_weight.get(seg_data.get("evidence_level", "C级"), 0.6)
            
            # 计算最终分数
            final_score = base_score * weight
            
            reranked.append((seg_id, final_score, seg_data))
        
        # 按最终分数排序
        reranked.sort(key=lambda x: x[1], reverse=True)
        
        # 构建结果对象
        results = []
        for seg_id, score, seg_data in reranked[:self.config.retrieval.top_k_final]:
            results.append(RetrievalResult(
                segment_id=seg_id,
                file_id=seg_data["file_id"],
                file_path=seg_data["parent_file_path"],
                content=seg_data["content"],
                score=score,
                evidence_level=seg_data.get("evidence_level", "C级"),
                tags=seg_data.get("fine_grained_tags", []),
                source_type="reranked"
            ))
        
        print(f"📊 第四层 - 重排序: 最终 Top-{len(results)} 结果")
        return results
    
    def retrieve(self, query: str) -> List[RetrievalResult]:
        """
        执行完整的多层级检索流程
        
        Args:
            query: 用户查询
            
        Returns:
            检索结果列表
        """
        print("\n" + "=" * 70)
        print(f"🔍 多层级检索: {query}")
        print("=" * 70)
        
        # 1. 提取查询标签
        query_tags = self.extract_query_tags(query)
        print(f"📌 查询标签: {', '.join(query_tags)}")
        
        # 2. 第一层：标签过滤
        candidate_segments = self.layer1_tag_filter(query_tags)
        
        if not candidate_segments:
            print("⚠️  未找到匹配的片段")
            return []
        
        # 3. 第二层：关联召回
        candidate_segments = self.layer2_relation_recall(candidate_segments)
        
        # 4. 第三层：向量检索
        scored_segments = self.layer3_vector_search(query, candidate_segments)
        
        if not scored_segments:
            print("⚠️  向量检索无结果")
            return []
        
        # 5. 第四层：重排序
        final_results = self.layer4_rerank(scored_segments)
        
        # 输出结果摘要
        print("\n" + "=" * 70)
        print("📋 检索结果摘要:")
        print("=" * 70)
        for i, result in enumerate(final_results, 1):
            print(f"\n{i}. [{result.evidence_level}] {result.file_path}")
            print(f"   分数: {result.score:.3f}")
            print(f"   标签: {', '.join(result.tags[:5])}")
            print(f"   内容: {result.content[:100]}...")
        
        print("\n" + "=" * 70)
        
        return final_results
    
    def format_results_for_llm(self, results: List[RetrievalResult]) -> str:
        """
        将检索结果格式化为LLM输入
        
        Args:
            results: 检索结果列表
            
        Returns:
            格式化的字符串
        """
        if not results:
            return "未找到相关医学知识"
        
        formatted = "【知识库检索结果】\n\n"
        
        for i, result in enumerate(results, 1):
            formatted += f"--- 结果 {i} (证据等级: {result.evidence_level}, 相关度: {result.score:.2f}) ---\n"
            formatted += f"来源: {result.file_path}\n"
            formatted += f"内容: {result.content}\n\n"
        
        return formatted


def main():
    """测试多层级检索器"""
    retriever = MultiLayerRetriever()
    
    # 测试查询
    test_queries = [
        "PCI术后患者的目标心率范围是多少？",
        "冠心病患者如何进行运动康复？",
        "PCI术后需要服用什么药物？"
    ]
    
    for query in test_queries:
        results = retriever.retrieve(query)
        print("\n" + "=" * 70)
        print("LLM输入格式:")
        print("=" * 70)
        print(retriever.format_results_for_llm(results))


if __name__ == "__main__":
    main()
