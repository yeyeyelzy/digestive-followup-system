"""
多智能体系统V2.0 - 消息总线
实现智能体间的异步消息通信
"""
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from collections import deque, defaultdict
from threading import Lock, Thread, Event
from queue import PriorityQueue, Empty
import time
from datetime import datetime, timedelta

import sys
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from MyAgentSystem.multi_agent_system_v2.agent_base.base_agent import (
    Task, TaskResult, AgentStatus, TaskPriority, BaseAgent
)


class MessageBus:
    """消息总线 - 智能体间通信中枢"""
    
    def __init__(self, max_queue_size: int = 10000):
        """
        初始化消息总线
        
        Args:
            max_queue_size: 最大队列大小
        """
        self.max_queue_size = max_queue_size
        
        # 任务队列（优先级队列）
        self.task_queue: PriorityQueue = PriorityQueue(maxsize=max_queue_size)
        
        # 任务结果存储
        self.task_results: Dict[str, TaskResult] = {}
        
        # 已注册的智能体
        self.registered_agents: Dict[str, BaseAgent] = {}
        
        # 智能体能力映射
        self.capability_to_agents: Dict[str, List[str]] = defaultdict(list)
        
        # 订阅机制（任务类型 -> 智能体ID列表）
        self.subscriptions: Dict[str, List[str]] = defaultdict(list)
        
        # 线程锁
        self.lock = Lock()
        self.result_lock = Lock()
        
        # 控制事件
        self.running = False
        self.worker_thread: Optional[Thread] = None
        self.stop_event = Event()
        
        # 任务等待事件
        self.task_events: Dict[str, Event] = {}
        
        # 统计信息
        self.stats = {
            "tasks_published": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "tasks_in_queue": 0
        }
    
    def register_agent(self, agent: BaseAgent) -> str:
        """
        注册智能体
        
        Args:
            agent: 智能体实例
            
        Returns:
            智能体ID
        """
        with self.lock:
            self.registered_agents[agent.agent_id] = agent
            
            # 注册智能体能力
            for capability in agent.get_capabilities():
                self.capability_to_agents[capability.name].append(agent.agent_id)
            
            print(f"[MessageBus] 智能体已注册: {agent.context.agent_name} ({agent.agent_id})")
            return agent.agent_id
    
    def unregister_agent(self, agent_id: str):
        """
        注销智能体
        
        Args:
            agent_id: 智能体ID
        """
        with self.lock:
            if agent_id in self.registered_agents:
                agent = self.registered_agents[agent_id]
                
                # 移除能力映射
                for capability in agent.get_capabilities():
                    if agent_id in self.capability_to_agents[capability.name]:
                        self.capability_to_agents[capability.name].remove(agent_id)
                
                # 移除订阅
                for task_type in list(self.subscriptions.keys()):
                    if agent_id in self.subscriptions[task_type]:
                        self.subscriptions[task_type].remove(agent_id)
                
                del self.registered_agents[agent_id]
                print(f"[MessageBus] 智能体已注销: {agent_id}")
    
    def subscribe(self, agent_id: str, task_type: str):
        """
        订阅任务类型
        
        Args:
            agent_id: 智能体ID
            task_type: 任务类型
        """
        with self.lock:
            if agent_id not in self.subscriptions[task_type]:
                self.subscriptions[task_type].append(agent_id)
    
    def unsubscribe(self, agent_id: str, task_type: str):
        """
        取消订阅任务类型
        
        Args:
            agent_id: 智能体ID
            task_type: 任务类型
        """
        with self.lock:
            if task_type in self.subscriptions:
                if agent_id in self.subscriptions[task_type]:
                    self.subscriptions[task_type].remove(agent_id)
    
    def publish_task(self, task: Task) -> str:
        """
        发布任务
        
        Args:
            task: 任务对象
            
        Returns:
            任务ID
        """
        try:
            # 优先级队列使用 (priority_value, timestamp, task)
            priority_value = -task.priority.value  # 负数表示高优先级先处理
            timestamp = time.time()
            
            self.task_queue.put((priority_value, timestamp, task), block=False)
            
            with self.lock:
                self.stats["tasks_published"] += 1
                self.stats["tasks_in_queue"] = self.task_queue.qsize()
            
            # 创建任务等待事件
            self.task_events[task.task_id] = Event()
            
            print(f"[MessageBus] 任务已发布: {task.task_type} ({task.task_id})")
            return task.task_id
            
        except Exception as e:
            print(f"[MessageBus] 发布任务失败: {e}")
            raise
    
    def find_agents_for_task(self, task: Task) -> List[str]:
        """
        查找适合处理任务的智能体
        
        Args:
            task: 任务对象
            
        Returns:
            智能体ID列表
        """
        candidate_agents = []
        
        # 1. 如果指定了目标智能体
        if task.target_agent_id and task.target_agent_id in self.registered_agents:
            return [task.target_agent_id]
        
        # 2. 查找订阅了该任务类型的智能体
        if task.task_type in self.subscriptions:
            candidate_agents.extend(self.subscriptions[task.task_type])
        
        # 3. 查找有相关能力的智能体
        # 这里可以根据任务类型推断所需能力
        
        # 去重
        candidate_agents = list(set(candidate_agents))
        
        # 过滤掉非空闲状态的智能体
        available_agents = []
        for agent_id in candidate_agents:
            if agent_id in self.registered_agents:
                agent = self.registered_agents[agent_id]
                if agent.context.status == AgentStatus.IDLE:
                    available_agents.append(agent_id)
        
        return available_agents
    
    def _worker_loop(self):
        """工作线程主循环"""
        print("[MessageBus] 工作线程已启动")
        
        while not self.stop_event.is_set():
            try:
                # 从队列获取任务（超时1秒）
                priority_value, timestamp, task = self.task_queue.get(timeout=1.0)
                
                # 查找处理智能体
                agent_ids = self.find_agents_for_task(task)
                
                if not agent_ids:
                    print(f"[MessageBus] 未找到可用智能体处理任务: {task.task_id}")
                    # 重新入队或标记失败
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        time.sleep(0.5)  # 等待一下再重试
                        self.task_queue.put((priority_value, timestamp, task))
                    else:
                        self._handle_task_failed(task, "未找到可用智能体")
                    continue
                
                # 选择第一个可用智能体
                agent_id = agent_ids[0]
                agent = self.registered_agents[agent_id]
                
                # 处理任务
                try:
                    agent.update_status(AgentStatus.PROCESSING)
                    result = agent.process_task(task)
                    result.executed_by = agent_id
                    
                    self._handle_task_completed(task, result)
                    
                except Exception as e:
                    print(f"[MessageBus] 智能体处理任务异常: {e}")
                    if task.retry_count < task.max_retries:
                        task.retry_count += 1
                        self.task_queue.put((priority_value, timestamp, task))
                    else:
                        self._handle_task_failed(task, str(e))
                finally:
                    agent.update_status(AgentStatus.IDLE)
                
                with self.lock:
                    self.stats["tasks_in_queue"] = self.task_queue.qsize()
                
            except Empty:
                continue
            except Exception as e:
                print(f"[MessageBus] 工作线程异常: {e}")
        
        print("[MessageBus] 工作线程已停止")
    
    def _handle_task_completed(self, task: Task, result: TaskResult):
        """处理任务完成"""
        with self.result_lock:
            self.task_results[task.task_id] = result
            self.stats["tasks_completed"] += 1
        
        # 触发等待事件
        if task.task_id in self.task_events:
            self.task_events[task.task_id].set()
        
        print(f"[MessageBus] 任务完成: {task.task_id}")
    
    def _handle_task_failed(self, task: Task, error_message: str):
        """处理任务失败"""
        result = TaskResult(
            task_id=task.task_id,
            success=False,
            error_message=error_message
        )
        
        with self.result_lock:
            self.task_results[task.task_id] = result
            self.stats["tasks_failed"] += 1
        
        # 触发等待事件
        if task.task_id in self.task_events:
            self.task_events[task.task_id].set()
        
        print(f"[MessageBus] 任务失败: {task.task_id} - {error_message}")
    
    def wait_for_result(self, task_id: str, timeout: float = 30.0) -> Optional[TaskResult]:
        """
        等待任务结果
        
        Args:
            task_id: 任务ID
            timeout: 超时时间（秒）
            
        Returns:
            任务结果
        """
        # 先检查是否已有结果
        with self.result_lock:
            if task_id in self.task_results:
                return self.task_results[task_id]
        
        # 等待事件
        if task_id in self.task_events:
            event = self.task_events[task_id]
            if event.wait(timeout=timeout):
                with self.result_lock:
                    return self.task_results.get(task_id)
        
        return None
    
    def get_result(self, task_id: str) -> Optional[TaskResult]:
        """
        获取任务结果（非阻塞）
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务结果
        """
        with self.result_lock:
            return self.task_results.get(task_id)
    
    def start(self):
        """启动消息总线"""
        if self.running:
            return
        
        self.running = True
        self.stop_event.clear()
        
        # 启动工作线程
        self.worker_thread = Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        
        print("[MessageBus] 消息总线已启动")
    
    def stop(self):
        """停止消息总线"""
        if not self.running:
            return
        
        self.running = False
        self.stop_event.set()
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5.0)
        
        print("[MessageBus] 消息总线已停止")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        with self.lock:
            stats = self.stats.copy()
            stats["registered_agents"] = len(self.registered_agents)
            return stats
    
    def shutdown(self):
        """关闭消息总线"""
        self.stop()
        
        # 注销所有智能体
        with self.lock:
            agent_ids = list(self.registered_agents.keys())
        
        for agent_id in agent_ids:
            self.unregister_agent(agent_id)
        
        print("[MessageBus] 消息总线已关闭")


class LoopController:
    """循环流程控制器 - 管理主循环和子循环"""
    
    def __init__(self, message_bus: MessageBus):
        """
        初始化循环控制器
        
        Args:
            message_bus: 消息总线
        """
        self.message_bus = message_bus
        self.max_iterations = {
            "main_loop": 5,
            "evidence_check": 3,
            "nlg_generation": 2
        }
        self.current_iterations: Dict[str, int] = defaultdict(int)
        self.loop_history: List[Dict] = []
    
    def start_loop(self, loop_name: str, max_iterations: int = None) -> bool:
        """
        开始循环
        
        Args:
            loop_name: 循环名称
            max_iterations: 最大迭代次数
            
        Returns:
            是否可以开始
        """
        if max_iterations:
            self.max_iterations[loop_name] = max_iterations
        
        self.current_iterations[loop_name] = 0
        return True
    
    def should_continue(self, loop_name: str) -> bool:
        """
        检查是否应该继续循环
        
        Args:
            loop_name: 循环名称
            
        Returns:
            是否继续
        """
        current = self.current_iterations.get(loop_name, 0)
        max_iter = self.max_iterations.get(loop_name, 3)
        return current < max_iter
    
    def increment_iteration(self, loop_name: str):
        """
        增加迭代计数
        
        Args:
            loop_name: 循环名称
        """
        self.current_iterations[loop_name] = self.current_iterations.get(loop_name, 0) + 1
    
    def record_loop_step(self, loop_name: str, step_data: Dict[str, Any]):
        """
        记录循环步骤
        
        Args:
            loop_name: 循环名称
            step_data: 步骤数据
        """
        self.loop_history.append({
            "loop_name": loop_name,
            "iteration": self.current_iterations.get(loop_name, 0),
            "timestamp": datetime.now().isoformat(),
            "data": step_data
        })
    
    def get_loop_history(self, loop_name: str = None) -> List[Dict]:
        """
        获取循环历史
        
        Args:
            loop_name: 循环名称，None表示获取全部
            
        Returns:
            循环历史
        """
        if loop_name:
            return [h for h in self.loop_history if h["loop_name"] == loop_name]
        return self.loop_history.copy()
