"""
知识库特征工程与索引构建模块
实现两级预索引（文件级+片段级）的特征工程
"""
import re
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import jieba
import jieba.analyse
import yaml
from tqdm import tqdm

import sys
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from MyKnownlege.knowledge_base_v2.config.settings import config


@dataclass
class FileMeta:
    """文件元数据"""
    file_id: str
    file_path: str
    file_type: str
    file_name: str
    topic_domain: str = ""
    target_user: str = ""
    evidence_level: str = ""
    update_time: str = ""
    primary_tags: List[str] = None
    secondary_tags: List[str] = None
    tertiary_tags: List[str] = None
    related_files: List[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.primary_tags is None:
            self.primary_tags = []
        if self.secondary_tags is None:
            self.secondary_tags = []
        if self.tertiary_tags is None:
            self.tertiary_tags = []
        if self.related_files is None:
            self.related_files = []


@dataclass
class SegmentMeta:
    """片段元数据"""
    segment_id: str
    file_id: str
    parent_file_path: str
    start_position: int
    end_position: int
    content: str
    core_questions: List[str] = None
    fine_grained_tags: List[str] = None
    scenario_tags: List[str] = None
    evidence_level: str = ""
    vector_id: str = ""
    
    def __post_init__(self):
        if self.core_questions is None:
            self.core_questions = []
        if self.fine_grained_tags is None:
            self.fine_grained_tags = []
        if self.scenario_tags is None:
            self.scenario_tags = []


class TextProcessor:
    """文本处理器"""
    
    def __init__(self):
        # 初始化jieba
        jieba.initialize()
        
        # 医学关键词
        self.medical_keywords = {
            "primary": ["冠心病", "心力衰竭", "高血压", "糖尿病", "PCI", "支架", "康复", "运动", "饮食", "药物"],
            "secondary": ["心率", "血压", "血糖", "血脂", "血小板", "抗凝", "抗血小板", "β受体阻滞剂", "他汀"],
            "tertiary": ["静息心率", "目标心率", "运动强度", "METs", "依从性", "禁忌症", "适应症"]
        }
        
        # 场景标签
        self.scenario_patterns = {
            "患者日常咨询": ["患者", "日常", "咨询", "应该", "可以", "能否"],
            "医生方案制定": ["医生", "方案", "制定", "调整", "治疗", "处方"],
            "风险预警判断": ["风险", "预警", "危险", "警告", "注意", "避免"],
            "康复训练指导": ["康复", "训练", "运动", "锻炼", "活动"],
            "用药管理指导": ["用药", "药物", "剂量", "服用", "漏服"]
        }
    
    def extract_tags(self, text: str, max_tags: int = 10) -> Tuple[List[str], List[str], List[str]]:
        """
        从文本中提取三级标签
        
        Args:
            text: 输入文本
            max_tags: 最大标签数
            
        Returns:
            (一级标签, 二级标签, 三级标签)
        """
        primary = []
        secondary = []
        tertiary = []
        
        text_lower = text.lower()
        
        # 匹配关键词
        for keyword in self.medical_keywords["primary"]:
            if keyword in text_lower:
                primary.append(keyword)
        
        for keyword in self.medical_keywords["secondary"]:
            if keyword in text_lower:
                secondary.append(keyword)
        
        for keyword in self.medical_keywords["tertiary"]:
            if keyword in text_lower:
                tertiary.append(keyword)
        
        # 使用TF-IDF提取补充标签
        tfidf_tags = jieba.analyse.extract_tags(text, topK=max_tags)
        for tag in tfidf_tags:
            if len(tag) >= 2 and tag not in primary + secondary + tertiary:
                if len(primary) < 3:
                    primary.append(tag)
                elif len(secondary) < 4:
                    secondary.append(tag)
                elif len(tertiary) < 3:
                    tertiary.append(tag)
        
        return primary[:3], secondary[:4], tertiary[:3]
    
    def extract_core_questions(self, text: str) -> List[str]:
        """
        提取片段可解决的核心问题
        
        Args:
            text: 输入文本
            
        Returns:
            核心问题列表
        """
        questions = []
        
        # 基于内容推断问题
        if "心率" in text and "目标" in text:
            questions.append("PCI术后患者的目标心率范围是多少？")
        if "运动" in text and "康复" in text:
            questions.append("PCI术后患者如何进行运动康复？")
        if "药物" in text and "服用" in text:
            questions.append("PCI术后患者需要服用哪些药物？")
        if "饮食" in text:
            questions.append("PCI术后患者的饮食应该注意什么？")
        if "风险" in text or "禁忌" in text:
            questions.append("PCI术后患者有哪些风险和禁忌？")
        
        return questions[:3]
    
    def extract_scenario_tags(self, text: str) -> List[str]:
        """
        提取适用场景标签
        
        Args:
            text: 输入文本
            
        Returns:
            场景标签列表
        """
        scenarios = []
        text_lower = text.lower()
        
        for scenario, patterns in self.scenario_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    scenarios.append(scenario)
                    break
        
        return list(set(scenarios))
    
    def split_into_segments(self, text: str, chunk_size: int = 500, 
                           chunk_overlap: int = 50) -> List[Tuple[int, int, str]]:
        """
        基于语义完整性切分文本
        
        Args:
            text: 输入文本
            chunk_size: 目标块大小
            chunk_overlap: 重叠大小
            
        Returns:
            片段列表 [(start, end, content), ...]
        """
        segments = []
        
        # 按标点符号和换行符分割
        sentences = re.split(r'[。！？!?\n]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        current_segment = ""
        current_start = 0
        current_end = 0
        
        for sentence in sentences:
            if len(current_segment) + len(sentence) <= chunk_size:
                current_segment += sentence + "。"
                current_end += len(sentence) + 1
            else:
                if current_segment:
                    segments.append((current_start, current_end, current_segment))
                
                # 保留重叠
                if chunk_overlap > 0 and len(segments) > 0:
                    prev_content = segments[-1][2]
                    overlap_text = prev_content[-chunk_overlap:] if len(prev_content) > chunk_overlap else prev_content
                    current_segment = overlap_text + sentence + "。"
                    current_start = current_end - len(overlap_text)
                else:
                    current_segment = sentence + "。"
                    current_start = current_end
                
                current_end = current_start + len(current_segment)
        
        if current_segment:
            segments.append((current_start, current_end, current_segment))
        
        return segments


class FeatureEngineer:
    """特征工程与索引构建器"""
    
    def __init__(self, config_instance=None):
        """
        初始化特征工程器
        
        Args:
            config_instance: 配置实例
        """
        self.config = config_instance or config
        self.text_processor = TextProcessor()
        self.file_metas: Dict[str, FileMeta] = {}
        self.segment_metas: Dict[str, SegmentMeta] = {}
        self.file_relations: Dict[str, List[Dict]] = defaultdict(list)
    
    def load_file_content(self, file_path: Path) -> Optional[str]:
        """
        加载文件内容
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件内容
        """
        try:
            if file_path.suffix.lower() in ['.json', '.jsonl']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_path.suffix.lower() == '.md':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_path.suffix.lower() == '.csv':
                # 简单加载CSV前几行作为文本
                import pandas as pd
                df = pd.read_csv(file_path, nrows=20)
                return df.to_string()
            elif file_path.suffix.lower() == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return f.read()
            elif file_path.suffix.lower() == '.pdf':
                # 尝试加载已处理的PDF内容
                processed_file = self.config.paths.processed_data_dir / "clean_guidelines.jsonl"
                if processed_file.exists():
                    with open(processed_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                data = json.loads(line)
                                if file_path.name in data.get('file_name', ''):
                                    return data.get('content', '')
                            except:
                                continue
                return f"PDF文件: {file_path.name}"
            else:
                return f"文件: {file_path.name}"
        except Exception as e:
            print(f"⚠️  加载文件失败 {file_path}: {e}")
            return None
    
    def build_file_index(self, file_info: Dict) -> FileMeta:
        """
        构建文件级索引
        
        Args:
            file_info: 文件信息（来自哈希清单）
            
        Returns:
            文件元数据
        """
        file_path = self.config.paths.raw_data_dir / file_info["file_path"]
        file_name = file_path.name
        
        # 生成文件ID
        file_id = f"file_{hash(str(file_path)) % 100000:05d}"
        
        # 提取内容
        content = self.load_file_content(file_path) or ""
        
        # 提取标签
        primary_tags, secondary_tags, tertiary_tags = self.text_processor.extract_tags(
            content, max_tags=self.config.feature.max_tags_per_file
        )
        
        # 合并文件标签
        file_tags = file_info.get("file_tag", [])
        primary_tags.extend([t for t in file_tags if t not in primary_tags])
        
        # 确定主题领域
        topic_domain = ""
        if "冠心病" in primary_tags:
            topic_domain = "心血管疾病"
        elif "心力衰竭" in primary_tags:
            topic_domain = "心血管疾病"
        elif "康复" in primary_tags:
            topic_domain = "康复医学"
        
        # 确定目标用户
        target_user = ""
        if "患者" in content:
            target_user = "患者/家属"
        if "医生" in content:
            target_user = "医生/康复师" if not target_user else "所有用户"
        
        # 证据等级
        evidence_level = "C级"
        if "指南" in file_name or "共识" in file_name:
            evidence_level = "A级"
        elif "规范" in file_name:
            evidence_level = "B级"
        
        file_meta = FileMeta(
            file_id=file_id,
            file_path=file_info["file_path"],
            file_type=file_info["file_type"],
            file_name=file_name,
            topic_domain=topic_domain,
            target_user=target_user,
            evidence_level=evidence_level,
            update_time=file_info.get("last_modified", ""),
            primary_tags=primary_tags,
            secondary_tags=secondary_tags,
            tertiary_tags=tertiary_tags
        )
        
        self.file_metas[file_id] = file_meta
        return file_meta
    
    def build_segment_index(self, file_meta: FileMeta) -> List[SegmentMeta]:
        """
        构建片段级索引
        
        Args:
            file_meta: 文件元数据
            
        Returns:
            片段元数据列表
        """
        file_path = self.config.paths.raw_data_dir / file_meta.file_path
        content = self.load_file_content(file_path) or ""
        
        if not content:
            return []
        
        # 切分片段
        segments = self.text_processor.split_into_segments(
            content,
            chunk_size=self.config.feature.chunk_size,
            chunk_overlap=self.config.feature.chunk_overlap
        )
        
        segment_metas = []
        
        for idx, (start, end, seg_content) in enumerate(segments):
            segment_id = f"{file_meta.file_id}_seg_{idx:04d}"
            
            # 提取核心问题
            core_questions = self.text_processor.extract_core_questions(seg_content)
            
            # 提取细粒度标签
            _, fine_tags, _ = self.text_processor.extract_tags(
                seg_content, max_tags=self.config.feature.max_tags_per_segment
            )
            
            # 继承文件标签
            fine_tags.extend(file_meta.secondary_tags)
            fine_tags.extend(file_meta.tertiary_tags)
            
            # 提取场景标签
            scenario_tags = self.text_processor.extract_scenario_tags(seg_content)
            
            segment_meta = SegmentMeta(
                segment_id=segment_id,
                file_id=file_meta.file_id,
                parent_file_path=file_meta.file_path,
                start_position=start,
                end_position=end,
                content=seg_content,
                core_questions=core_questions,
                fine_grained_tags=list(set(fine_tags)),
                scenario_tags=scenario_tags,
                evidence_level=file_meta.evidence_level
            )
            
            segment_metas.append(segment_meta)
            self.segment_metas[segment_id] = segment_meta
        
        return segment_metas
    
    def build_file_relations(self):
        """构建文件间关联关系"""
        print("\n🔗 构建文件关联关系...")
        
        file_list = list(self.file_metas.values())
        
        for i, file1 in enumerate(file_list):
            for file2 in file_list[i+1:]:
                # 计算标签重合度
                tags1 = set(file1.primary_tags + file1.secondary_tags + file1.tertiary_tags)
                tags2 = set(file2.primary_tags + file2.secondary_tags + file2.tertiary_tags)
                
                if tags1 and tags2:
                    intersection = tags1 & tags2
                    union = tags1 | tags2
                    similarity = len(intersection) / len(union)
                    
                    if similarity >= self.config.feature.relation_threshold:
                        # 添加双向关联
                        self.file_relations[file1.file_id].append({
                            "file_id": file2.file_id,
                            "file_path": file2.file_path,
                            "similarity": round(similarity, 3)
                        })
                        self.file_relations[file2.file_id].append({
                            "file_id": file1.file_id,
                            "file_path": file1.file_path,
                            "similarity": round(similarity, 3)
                        })
        
        print(f"✓ 构建了 {sum(len(rels) for rels in self.file_relations.values()) // 2} 对文件关联")
    
    def save_file_relation_index(self):
        """保存文件关联索引"""
        index_data = {
            "version": "v2.0.0",
            "last_updated": "",
            "files": {}
        }
        
        for file_id, file_meta in self.file_metas.items():
            file_dict = asdict(file_meta)
            file_dict["related_files"] = self.file_relations.get(file_id, [])
            index_data["files"][file_id] = file_dict
        
        # 更新时间
        from datetime import datetime
        index_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(self.config.paths.kb_file_relation_index, 'w', encoding='utf-8') as f:
            yaml.dump(index_data, f, allow_unicode=True, default_flow_style=False)
        
        print(f"✓ 文件关联索引已保存到 {self.config.paths.kb_file_relation_index}")
    
    def save_segment_feature_index(self):
        """保存片段特征索引"""
        index_data = {
            "version": "v2.0.0",
            "last_updated": "",
            "segments": {},
            "tag_to_segments": defaultdict(list),
            "question_to_segments": defaultdict(list)
        }
        
        for seg_id, seg_meta in self.segment_metas.items():
            seg_dict = asdict(seg_meta)
            index_data["segments"][seg_id] = seg_dict
            
            # 建立标签到片段的映射
            for tag in seg_meta.fine_grained_tags:
                index_data["tag_to_segments"][tag].append(seg_id)
            
            # 建立问题到片段的映射
            for question in seg_meta.core_questions:
                index_data["question_to_segments"][question].append(seg_id)
        
        # 更新时间
        from datetime import datetime
        index_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 转换defaultdict为普通dict
        index_data["tag_to_segments"] = dict(index_data["tag_to_segments"])
        index_data["question_to_segments"] = dict(index_data["question_to_segments"])
        
        with open(self.config.paths.kb_segment_feature_index, 'w', encoding='utf-8') as f:
            yaml.dump(index_data, f, allow_unicode=True, default_flow_style=False)
        
        print(f"✓ 片段特征索引已保存到 {self.config.paths.kb_segment_feature_index}")
    
    def run_feature_engineering(self, file_list: List[Dict]) -> Dict:
        """
        执行完整的特征工程流程
        
        Args:
            file_list: 文件列表（来自哈希清单）
            
        Returns:
            特征工程结果
        """
        print("\n" + "=" * 70)
        print("🔧 知识库特征工程")
        print("=" * 70)
        
        # 1. 构建文件级索引
        print("\n📄 步骤 1: 构建文件级索引")
        for file_info in tqdm(file_list, desc="处理文件"):
            self.build_file_index(file_info)
        
        print(f"✓ 构建了 {len(self.file_metas)} 个文件索引")
        
        # 2. 构建片段级索引
        print("\n✂️  步骤 2: 构建片段级索引")
        total_segments = 0
        for file_meta in tqdm(list(self.file_metas.values()), desc="切分片段"):
            segments = self.build_segment_index(file_meta)
            total_segments += len(segments)
        
        print(f"✓ 构建了 {total_segments} 个片段索引")
        
        # 3. 构建文件关联
        self.build_file_relations()
        
        # 4. 保存索引
        print("\n💾 步骤 3: 保存索引文件")
        self.save_file_relation_index()
        self.save_segment_feature_index()
        
        print("\n" + "=" * 70)
        print("✅ 特征工程完成!")
        print("=" * 70)
        
        return {
            "file_count": len(self.file_metas),
            "segment_count": total_segments,
            "relation_count": sum(len(rels) for rels in self.file_relations.values()) // 2
        }


def main():
    """测试特征工程"""
    from MyKnownlege.knowledge_base_v2.src.hash_checker import HashChecker
    
    # 先检测变更
    checker = HashChecker()
    change_result = checker.check_changes()
    
    # 如果有变更，执行特征工程
    if change_result["need_rebuild"]:
        engineer = FeatureEngineer()
        engineer.run_feature_engineering(change_result["current_manifest"]["file_list"])
        checker.save_current_manifest()


if __name__ == "__main__":
    main()
