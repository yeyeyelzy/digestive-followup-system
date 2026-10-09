"""
多智能体系统V2.0 - 智能体基类
所有智能体都继承自此类
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import uuid
from enum import Enum
import logging


class AgentStatus(Enum):
    """智能体状态"""
    IDLE = "idle"
    INITIALIZING = "initializing"
    RUNNING = "running"
    WAITING = "waiting"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"


class TaskPriority(Enum):
    """任务优先级"""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class AgentCapability:
    """智能体能力"""
    name: str
    description: str
    version: str = "1.0.0"
    enabled: bool = True


@dataclass
class AgentContext:
    """智能体上下文"""
    agent_id: str
    agent_name: str
    agent_role: str
    status: AgentStatus = AgentStatus.IDLE
    current_task_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """任务对象"""
    task_id: str
    task_type: str
    priority: TaskPriority = TaskPriority.NORMAL
    source_agent_id: Optional[str] = None
    target_agent_id: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    max_retries: int = 3
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    patient_id: Optional[str] = None
    
    @classmethod
    def create(cls, task_type: str, payload: Dict[str, Any] = None, 
               priority: TaskPriority = TaskPriority.NORMAL,
               source_agent_id: str = None,
               target_agent_id: str = None,
               patient_id: str = None) -> 'Task':
        """创建新任务"""
        return cls(
            task_id=str(uuid.uuid4()),
            task_type=task_type,
            priority=priority,
            source_agent_id=source_agent_id,
            target_agent_id=target_agent_id,
            payload=payload or {},
            patient_id=patient_id
        )


@dataclass
class TaskResult:
    """任务结果"""
    task_id: str
    success: bool
    result: Dict[str, Any] = field(default_factory=dict)
    result_data: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    executed_by: Optional[str] = None
    completed_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """兼容旧代码：result_data 映射到 result"""
        if self.result_data and not self.result:
            self.result = self.result_data
        if self.result and not self.result_data:
            self.result_data = self.result


class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, agent_name: str, agent_role: str, config: Dict[str, Any] = None):
        """
        初始化智能体
        
        Args:
            agent_name: 智能体名称
            agent_role: 智能体角色
            config: 智能体配置
        """
        self.agent_id = f"agent_{uuid.uuid4().hex[:8]}"
        self.context = AgentContext(
            agent_id=self.agent_id,
            agent_name=agent_name,
            agent_role=agent_role
        )
        self.config = config or {}
        self.message_bus = None
        self.memory_system = None
        self._dependencies: List[str] = []
        self.capabilities: List[AgentCapability] = []
        self.logger = self._init_logger()
    
    def _init_logger(self):
        """初始化日志"""
        logger = logging.getLogger(f"Agent.{self.context.agent_name}")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
    
    def register_message_bus(self, message_bus):
        """注册消息总线"""
        self.message_bus = message_bus
    
    def register_memory_system(self, memory_system):
        """注册记忆系统"""
        self.memory_system = memory_system
    
    def add_dependency(self, agent_id: str):
        """添加依赖的智能体"""
        if agent_id not in self._dependencies:
            self._dependencies.append(agent_id)
    
    def add_capability(self, capability):
        """添加智能体能力"""
        if isinstance(capability, str):
            capability = AgentCapability(name=capability, description=capability)
        self.capabilities.append(capability)
    
    def get_capabilities(self) -> List[AgentCapability]:
        """获取智能体能力列表"""
        return self.capabilities.copy()
    
    def update_status(self, status: AgentStatus):
        """更新智能体状态"""
        self.context.status = status
        self.context.last_updated = datetime.now()
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        初始化智能体
        
        Returns:
            初始化是否成功
        """
        pass
    
    @abstractmethod
    def process_task(self, task: Task) -> TaskResult:
        """
        处理任务
        
        Args:
            task: 待处理的任务
            
        Returns:
            任务结果
        """
        pass
    
    def send_message(self, target_agent_id: str, message_type: str, 
                     payload: Dict[str, Any] = None,
                     priority: TaskPriority = TaskPriority.NORMAL,
                     patient_id: str = None) -> str:
        """
        发送消息给其他智能体
        
        Args:
            target_agent_id: 目标智能体ID
            message_type: 消息类型
            payload: 消息载荷
            priority: 优先级
            patient_id: 患者ID
            
        Returns:
            任务ID
        """
        if not self.message_bus:
            raise RuntimeError("Message bus not registered")
        
        task = Task.create(
            task_type=message_type,
            payload=payload,
            priority=priority,
            source_agent_id=self.agent_id,
            target_agent_id=target_agent_id,
            patient_id=patient_id
        )
        
        return self.message_bus.publish_task(task)
    
    def request_memory(self, memory_type: str, key: str, **kwargs) -> Optional[Any]:
        """
        从记忆系统请求数据
        
        Args:
            memory_type: 记忆类型
            key: 记忆键
            **kwargs: 其他参数
            
        Returns:
            记忆数据
        """
        if not self.memory_system:
            return None
        
        return self.memory_system.retrieve(memory_type, key, **kwargs)
    
    def store_memory(self, memory_type: str, key: str, value: Any, **kwargs):
        """
        存储数据到记忆系统
        
        Args:
            memory_type: 记忆类型
            key: 记忆键
            value: 记忆值
            **kwargs: 其他参数
        """
        if self.memory_system:
            self.memory_system.store(memory_type, key, value, **kwargs)
    
    def _update_shared_memory(self, key: str, value: Any, **kwargs):
        """更新共享协作记忆"""
        if self.memory_system:
            self.memory_system.store(
                memory_type="shared_collaboration",
                key=key,
                value=value,
                **kwargs
            )
    
    def shutdown(self):
        """关闭智能体"""
        self.update_status(AgentStatus.IDLE)
        self.logger.info(f"[{self.agent_id}] {self.context.agent_name} 已关闭")


class AgentConfig:
    """智能体配置管理器"""
    
    def __init__(self, config_file: str = None):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.agent_configs: Dict[str, Dict[str, Any]] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置"""
        if self.config_file:
            try:
                import yaml
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                self.agent_configs = config_data.get('agents', {})
            except Exception as e:
                logging.warning(f"加载配置失败: {e}")
    
    def get_agent_config(self, agent_role: str) -> Dict[str, Any]:
        """
        获取智能体配置
        
        Args:
            agent_role: 智能体角色
            
        Returns:
            智能体配置
        """
        return self.agent_configs.get(agent_role, {}).copy()
    
    def register_agent_config(self, agent_role: str, config: Dict[str, Any]):
        """
        注册智能体配置
        
        Args:
            agent_role: 智能体角色
            config: 智能体配置
        """
        self.agent_configs[agent_role] = config.copy()
