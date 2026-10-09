from pathlib import Path
import sys
import json
from datetime import datetime
from typing import Dict, List, Any

# 添加当前目录的父目录到Python路径
sys.path.append(str(Path(__file__).parent.parent))

class ControlPanel:
    """控制端面板"""
    
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []
        self.agent_status: Dict[str, Dict[str, Any]] = {}
        self.task_history: List[Dict[str, Any]] = []
        self.rag_interactions: List[Dict[str, Any]] = []
        self.system_metrics: Dict[str, Any] = {
            "start_time": datetime.now().isoformat(),
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "rag_queries": 0
        }
    
    def log_agent_message(self, agent_id: str, message: str, level: str = "info"):
        """记录智能体消息"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "type": "agent_message",
            "agent_id": agent_id,
            "message": message,
            "level": level
        }
        self.logs.append(log_entry)
        print(f"[{level.upper()}] [{agent_id}] {message}")
    
    def log_task_execution(self, task_id: str, agent_id: str, task_type: str, status: str, result: Dict[str, Any] = None):
        """记录任务执行情况"""
        task_entry = {
            "task_id": task_id,
            "agent_id": agent_id,
            "task_type": task_type,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        self.task_history.append(task_entry)
        self.system_metrics["total_tasks"] += 1
        if status == "completed":
            self.system_metrics["completed_tasks"] += 1
        elif status == "failed":
            self.system_metrics["failed_tasks"] += 1
        
        print(f"[TASK] {task_id} - {task_type} - {status} by {agent_id}")
    
    def log_rag_interaction(self, query: str, results: List[Dict[str, Any]]):
        """记录RAG知识库交互"""
        rag_entry = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "results_count": len(results),
            "results": results
        }
        self.rag_interactions.append(rag_entry)
        self.system_metrics["rag_queries"] += 1
        print(f"[RAG] Query: {query} - Results: {len(results)}")
    
    def update_agent_status(self, agent_id: str, status: str, capabilities: List[str] = None):
        """更新智能体状态"""
        self.agent_status[agent_id] = {
            "status": status,
            "last_updated": datetime.now().isoformat(),
            "capabilities": capabilities
        }
    
    def get_agent_status(self, agent_id: str = None) -> Dict[str, Any]:
        """获取智能体状态"""
        if agent_id:
            return self.agent_status.get(agent_id, {})
        return self.agent_status
    
    def get_task_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """获取任务历史"""
        if limit:
            return self.task_history[-limit:]
        return self.task_history
    
    def get_rag_interactions(self, limit: int = None) -> List[Dict[str, Any]]:
        """获取RAG交互历史"""
        if limit:
            return self.rag_interactions[-limit:]
        return self.rag_interactions
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """获取系统指标"""
        return self.system_metrics
    
    def get_logs(self, limit: int = None) -> List[Dict[str, Any]]:
        """获取日志"""
        if limit:
            return self.logs[-limit:]
        return self.logs
    
    def generate_system_report(self) -> Dict[str, Any]:
        """生成系统报告"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "system_metrics": self.system_metrics,
            "agent_status": self.agent_status,
            "recent_tasks": self.get_task_history(10),
            "recent_rag_interactions": self.get_rag_interactions(5),
            "recent_logs": self.get_logs(20)
        }
        return report
    
    def save_report(self, file_path: str):
        """保存报告到文件"""
        report = self.generate_system_report()
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"系统报告已保存到: {file_path}")
    
    def display_dashboard(self):
        """显示控制面板"""
        print("=" * 100)
        print("🧠 多智能体系统控制面板")
        print("=" * 100)
        
        # 系统概览
        print("\n📊 系统概览")
        print("-" * 50)
        print(f"系统运行时间: {self._get_running_time()}")
        print(f"总任务数: {self.system_metrics['total_tasks']}")
        print(f"完成任务: {self.system_metrics['completed_tasks']}")
        print(f"失败任务: {self.system_metrics['failed_tasks']}")
        print(f"RAG查询次数: {self.system_metrics['rag_queries']}")
        
        # 智能体状态
        print("\n🤖 智能体状态")
        print("-" * 50)
        for agent_id, status in self.agent_status.items():
            print(f"{agent_id}: {status['status']} (最后更新: {status['last_updated']})")
        
        # 最近任务
        print("\n📋 最近任务")
        print("-" * 50)
        recent_tasks = self.get_task_history(5)
        for task in recent_tasks:
            print(f"{task['task_id']} - {task['task_type']} - {task['status']} by {task['agent_id']}")
        
        # 最近RAG交互
        print("\n🔍 最近RAG交互")
        print("-" * 50)
        recent_rag = self.get_rag_interactions(3)
        for rag in recent_rag:
            print(f"查询: {rag['query']} (结果: {rag['results_count']})")
        
        print("=" * 100)
    
    def _get_running_time(self) -> str:
        """获取系统运行时间"""
        start_time = datetime.fromisoformat(self.system_metrics['start_time'])
        current_time = datetime.now()
        delta = current_time - start_time
        return str(delta)


# 全局控制端实例
control_panel = ControlPanel()

# 测试代码
if __name__ == "__main__":
    # 模拟一些日志和任务
    control_panel.log_agent_message("agent_1", "初始化完成")
    control_panel.log_agent_message("agent_2", "准备就绪")
    
    control_panel.update_agent_status("agent_1", "idle", ["task_distribution", "loop_control"])
    control_panel.update_agent_status("agent_2", "busy", ["data_analysis", "pattern_recognition"])
    
    control_panel.log_task_execution("task_001", "agent_1", "process_user_input", "completed", {"result": "处理完成"})
    control_panel.log_task_execution("task_002", "agent_2", "analyze_data", "completed", {"result": "分析完成"})
    
    control_panel.log_rag_interaction("心率正常范围", [{"content": "正常成年人的静息心率范围为60-100次/分钟"}])
    
    # 显示控制面板
    control_panel.display_dashboard()
    
    # 保存报告
    report_path = Path(__file__).parent / "system_report.json"
    control_panel.save_report(str(report_path))