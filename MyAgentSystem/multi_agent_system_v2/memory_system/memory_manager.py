"""
多智能体系统V2.0 - 四层记忆体系
实现瞬时会话记忆、患者长期画像记忆、智能体共享协作记忆、全局医学知识记忆
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from pathlib import Path
from datetime import datetime, timedelta
import json
import yaml
from threading import Lock
from collections import defaultdict

import sys
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@dataclass
class MemoryEntry:
    """记忆条目"""
    key: str
    value: Any
    memory_type: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TransientSessionMemory:
    """瞬时会话记忆 (STM) - 会话存续期间"""
    
    def __init__(self, session_timeout: int = 86400):
        """
        初始化瞬时会话记忆
        
        Args:
            session_timeout: 会话超时时间（秒），默认24小时
        """
        self.memories: Dict[str, MemoryEntry] = {}
        self.session_timeout = session_timeout
        self.lock = Lock()
    
    def store(self, session_id: str, key: str, value: Any, 
              metadata: Dict[str, Any] = None):
        """
        存储会话记忆
        
        Args:
            session_id: 会话ID
            key: 记忆键
            value: 记忆值
            metadata: 元数据
        """
        full_key = f"{session_id}:{key}"
        now = datetime.now()
        expires_at = now + timedelta(seconds=self.session_timeout)
        
        with self.lock:
            self.memories[full_key] = MemoryEntry(
                key=full_key,
                value=value,
                memory_type="transient",
                created_at=now,
                updated_at=now,
                expires_at=expires_at,
                metadata=metadata
            )
    
    def retrieve(self, session_id: str, key: str) -> Optional[Any]:
        """
        获取会话记忆
        
        Args:
            session_id: 会话ID
            key: 记忆键
            
        Returns:
            记忆值
        """
        full_key = f"{session_id}:{key}"
        
        with self.lock:
            if full_key in self.memories:
                entry = self.memories[full_key]
                # 检查是否过期
                if entry.expires_at and datetime.now() > entry.expires_at:
                    del self.memories[full_key]
                    return None
                return entry.value
        return None
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """
        获取会话完整上下文
        
        Args:
            session_id: 会话ID
            
        Returns:
            会话上下文
        """
        context = {}
        
        with self.lock:
            for full_key, entry in self.memories.items():
                if full_key.startswith(f"{session_id}:"):
                    # 检查是否过期
                    if entry.expires_at and datetime.now() > entry.expires_at:
                        continue
                    key = full_key.split(":", 1)[1]
                    context[key] = entry.value
        
        return context
    
    def cleanup_expired(self):
        """清理过期的会话记忆"""
        now = datetime.now()
        with self.lock:
            expired_keys = [
                key for key, entry in self.memories.items()
                if entry.expires_at and now > entry.expires_at
            ]
            for key in expired_keys:
                del self.memories[key]
        
        print(f"[STM] 清理了 {len(expired_keys)} 个过期记忆")


class LongTermPatientMemory:
    """患者长期画像记忆 (LTPM) - 患者全周期永久存储"""
    
    def __init__(self, storage_dir: Path):
        """
        初始化患者长期记忆
        
        Args:
            storage_dir: 存储目录
        """
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.lock = Lock()
    
    def _get_patient_file(self, patient_id: str) -> Path:
        """获取患者记忆文件路径"""
        return self.storage_dir / f"patient_{patient_id}.json"
    
    def store(self, patient_id: str, key: str, value: Any):
        """
        存储患者记忆
        
        Args:
            patient_id: 患者ID
            key: 记忆键
            value: 记忆值
        """
        with self.lock:
            # 更新缓存
            if patient_id not in self.cache:
                self.cache[patient_id] = {}
            self.cache[patient_id][key] = value
            
            # 持久化到文件
            patient_file = self._get_patient_file(patient_id)
            data = {}
            
            if patient_file.exists():
                try:
                    with open(patient_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    pass
            
            data[key] = {
                "value": value,
                "updated_at": datetime.now().isoformat()
            }
            
            with open(patient_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
    
    def retrieve(self, patient_id: str, key: str) -> Optional[Any]:
        """
        获取患者记忆
        
        Args:
            patient_id: 患者ID
            key: 记忆键
            
        Returns:
            记忆值
        """
        with self.lock:
            # 先查缓存
            if patient_id in self.cache and key in self.cache[patient_id]:
                return self.cache[patient_id][key]
            
            # 再查文件
            patient_file = self._get_patient_file(patient_id)
            if patient_file.exists():
                try:
                    with open(patient_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    if key in data:
                        value = data[key]["value"]
                        # 更新缓存
                        if patient_id not in self.cache:
                            self.cache[patient_id] = {}
                        self.cache[patient_id][key] = value
                        return value
                except:
                    pass
        
        return None
    
    def get_full_profile(self, patient_id: str) -> Dict[str, Any]:
        """
        获取患者完整画像
        
        Args:
            patient_id: 患者ID
            
        Returns:
            患者完整画像
        """
        patient_file = self._get_patient_file(patient_id)
        if patient_file.exists():
            try:
                with open(patient_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return {k: v["value"] for k, v in data.items()}
            except:
                pass
        return {}


class SharedCollaborationMemory:
    """智能体共享协作记忆 (SCM) - 系统全周期"""
    
    def __init__(self, config_file: Path):
        """
        初始化共享协作记忆
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.memory: Dict[str, Any] = {}
        self.lock = Lock()
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.memory = yaml.safe_load(f) or {}
            except Exception as e:
                print(f"[SCM] 加载配置失败: {e}")
    
    def _save_config(self):
        """保存配置文件"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                yaml.dump(self.memory, f, allow_unicode=True, default_flow_style=False)
        except Exception as e:
            print(f"[SCM] 保存配置失败: {e}")
    
    def store(self, key: str, value: Any):
        """
        存储共享记忆
        
        Args:
            key: 记忆键
            value: 记忆值
        """
        with self.lock:
            self.memory[key] = value
            self._save_config()
    
    def retrieve(self, key: str, default: Any = None) -> Any:
        """
        获取共享记忆
        
        Args:
            key: 记忆键
            default: 默认值
            
        Returns:
            记忆值
        """
        with self.lock:
            return self.memory.get(key, default)
    
    def get_agent_capabilities(self, agent_role: str) -> List[str]:
        """
        获取智能体能力列表
        
        Args:
            agent_role: 智能体角色
            
        Returns:
            能力列表
        """
        capabilities = self.memory.get("agent_capabilities", {})
        return capabilities.get(agent_role, [])
    
    def get_evidence_rules(self) -> Dict[str, Any]:
        """获取循证校验规则库"""
        return self.memory.get("evidence_rules", {})
    
    def get_optimal_solutions(self) -> List[Dict[str, Any]]:
        """获取循环迭代历史最优方案"""
        return self.memory.get("optimal_solutions", [])


class GlobalMedicalKnowledgeMemory:
    """全局医学知识记忆 (GMKM) - 随知识库更新"""
    
    def __init__(self, kb_config_dir: Path):
        """
        初始化全局医学知识记忆
        
        Args:
            kb_config_dir: 知识库配置目录
        """
        self.kb_config_dir = kb_config_dir
        self.kb_config_dir.mkdir(parents=True, exist_ok=True)
        self.file_index: Dict[str, Any] = {}
        self.segment_index: Dict[str, Any] = {}
        self.lock = Lock()
    
    def load_indexes(self):
        """加载索引文件"""
        file_index_path = self.kb_config_dir / "kb_file_relation_index.yaml"
        segment_index_path = self.kb_config_dir / "kb_segment_feature_index.yaml"
        
        with self.lock:
            if file_index_path.exists():
                try:
                    with open(file_index_path, 'r', encoding='utf-8') as f:
                        self.file_index = yaml.safe_load(f) or {}
                except Exception as e:
                    print(f"[GMKM] 加载文件索引失败: {e}")
            
            if segment_index_path.exists():
                try:
                    with open(segment_index_path, 'r', encoding='utf-8') as f:
                        self.segment_index = yaml.safe_load(f) or {}
                except Exception as e:
                    print(f"[GMKM] 加载片段索引失败: {e}")
    
    def retrieve(self, key: str, **kwargs) -> Optional[Any]:
        """
        获取医学知识
        
        Args:
            key: 知识键
            **kwargs: 其他参数
            
        Returns:
            知识内容
        """
        with self.lock:
            if key == "file_index":
                return self.file_index
            elif key == "segment_index":
                return self.segment_index
            elif key.startswith("file:"):
                file_id = key[5:]
                return self.file_index.get("files", {}).get(file_id)
            elif key.startswith("segment:"):
                segment_id = key[8:]
                return self.segment_index.get("segments", {}).get(segment_id)
        
        return None


class MemorySystem:
    """统一记忆系统 - 管理四层记忆"""
    
    def __init__(self, base_dir: Path):
        """
        初始化记忆系统
        
        Args:
            base_dir: 基础目录
        """
        self.base_dir = base_dir
        
        # 初始化各层记忆
        self.stm = TransientSessionMemory()
        self.ltpm = LongTermPatientMemory(base_dir / "patient_memory")
        self.scm = SharedCollaborationMemory(base_dir / "shared_memory" / "scm_config.yaml")
        self.gmkm = GlobalMedicalKnowledgeMemory(base_dir.parent.parent / "MyKnownlege" / "knowledge_base_v2" / "config")
        
        # 加载全局医学知识索引
        self.gmkm.load_indexes()
        
        print("[MemorySystem] 四层记忆体系初始化完成")
    
    def store(self, memory_type: str, key: str, value: Any, **kwargs):
        """
        存储记忆
        
        Args:
            memory_type: 记忆类型 (transient/longterm/shared/global)
            key: 记忆键
            value: 记忆值
            **kwargs: 其他参数
        """
        if memory_type == "transient":
            session_id = kwargs.get("session_id")
            if session_id:
                self.stm.store(session_id, key, value, kwargs.get("metadata"))
        elif memory_type == "longterm":
            patient_id = kwargs.get("patient_id")
            if patient_id:
                self.ltpm.store(patient_id, key, value)
        elif memory_type == "shared":
            self.scm.store(key, value)
        elif memory_type == "global":
            print("[MemorySystem] 全局记忆只读，不可直接存储")
    
    def retrieve(self, memory_type: str, key: str, **kwargs) -> Optional[Any]:
        """
        获取记忆
        
        Args:
            memory_type: 记忆类型
            key: 记忆键
            **kwargs: 其他参数
            
        Returns:
            记忆值
        """
        if memory_type == "transient":
            session_id = kwargs.get("session_id")
            if session_id:
                return self.stm.retrieve(session_id, key)
        elif memory_type == "longterm":
            patient_id = kwargs.get("patient_id")
            if patient_id:
                return self.ltpm.retrieve(patient_id, key)
        elif memory_type == "shared":
            return self.scm.retrieve(key, kwargs.get("default"))
        elif memory_type == "global":
            return self.gmkm.retrieve(key, **kwargs)
        
        return None
    
    def get_session_context(self, session_id: str) -> Dict[str, Any]:
        """获取会话上下文"""
        return self.stm.get_session_context(session_id)
    
    def get_patient_profile(self, patient_id: str) -> Dict[str, Any]:
        """获取患者完整画像"""
        return self.ltpm.get_full_profile(patient_id)
    
    def cleanup(self):
        """清理资源"""
        self.stm.cleanup_expired()
        print("[MemorySystem] 清理完成")
