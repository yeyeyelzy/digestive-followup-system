"""
冠心病PCI术后康复管理多智能体系统V2.0
系统启动入口
"""
from pathlib import Path
import sys

project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from MyAgentSystem.multi_agent_system_v2.agent_cluster.agent_orchestrator import AgentOrchestrator
from MyAgentSystem.multi_agent_system_v2.knowledge_base.rag_knowledge_base import RAGKnowledgeBaseInitializer


class MultiAgentSystem:
    """多智能体系统主类"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        
        # 初始化知识库
        self.kb_initializer = RAGKnowledgeBaseInitializer()
        self.knowledge_base = None
        
        # 初始化智能体编排器
        config = {
            "memory_path": str(self.base_dir / "memory"),
            "message_bus": {
                "max_tasks": 100,
                "queue_timeout": 30
            }
        }
        self.agent_orchestrator = AgentOrchestrator(config)
    
    def initialize(self):
        """系统初始化"""
        print("\n" + "=" * 80)
        print("冠心病PCI术后康复管理多智能体系统V2.0")
        print("=" * 80)
        
        # 1. 初始化知识库
        self.knowledge_base = self.kb_initializer.initialize()
        
        # 2. 初始化智能体集群
        print("\n" + "=" * 80)
        print("初始化智能体集群")
        print("=" * 80)
        
        if self.agent_orchestrator.initialize():
            print("=" * 80)
            print(f"智能体集群初始化完成，共 {len(self.agent_orchestrator.agents)} 个智能体")
            print("=" * 80)
        else:
            print("=" * 80)
            print("智能体集群初始化失败")
            print("=" * 80)
            return False
        
        # 3. 启动消息总线
        self.agent_orchestrator.message_bus.start()
        
        print("\n✅ 系统初始化完成！")
        print("=" * 80)
        return True
    
    def process_user_request(self, user_input: str, patient_id: str = "P_001", 
                            end_type: str = "patient") -> dict:
        """
        处理用户请求
        
        Args:
            user_input: 用户输入
            patient_id: 患者ID
            end_type: 端类型 (patient/family/doctor)
            
        Returns:
            处理结果
        """
        print(f"\n📝 处理用户请求: {user_input}")
        
        result = self.agent_orchestrator.process_user_request(
            user_input=user_input,
            patient_id=patient_id,
            end_type=end_type
        )
        
        return result
    
    def shutdown(self):
        """关闭系统"""
        print("\n" + "=" * 80)
        print("关闭系统...")
        print("=" * 80)
        
        # 停止消息总线和清理资源
        self.agent_orchestrator.shutdown()
        
        print("\n✅ 系统已关闭")
        print("=" * 80)


def main():
    """主函数"""
    # 创建系统
    system = MultiAgentSystem()
    
    try:
        # 初始化系统
        system.initialize()
        
        # 简单示例
        print("\n" + "=" * 80)
        print("系统演示")
        print("=" * 80)
        
        # 处理所有三个患者的数据
        patients = ["P_001", "P_002", "P_003"]
        end_types = ["patient", "family", "doctor"]
        
        for patient_id in patients:
            print(f"\n" + "-" * 80)
            print(f"处理患者 {patient_id} 的数据")
            print("-" * 80)
            
            for end_type in end_types:
                print(f"\n📝 处理 {end_type} 端请求")
                try:
                    result = system.process_user_request(
                        user_input="我的心率正常吗？",
                        patient_id=patient_id,
                        end_type=end_type
                    )
                    print(f"处理结果: {result}")
                except Exception as e:
                    print(f"处理 {end_type} 端请求失败，继续执行报告生成: {e}")
        
        # 生成时间周期报告
        print("\n" + "=" * 80)
        print("生成时间周期报告")
        print("=" * 80)
        
        from MyAgentSystem.multi_agent_system_v2.api.services.health_services import HealthReportService
        report_service = HealthReportService()
        
        for patient_id in patients:
            print(f"\n" + "-" * 80)
            print(f"生成患者 {patient_id} 的时间周期报告")
            print("-" * 80)
            
            for end_type in end_types:
                print(f"\n📦 生成 {end_type} 端完整产物")
                daily_report = report_service.get_report(patient_id, "daily", end_type)
                weekly_report = report_service.get_report(patient_id, "weekly", end_type)
                monthly_report = report_service.get_report(patient_id, "monthly", end_type)

                print(
                    f"日报产物: json={daily_report.get('artifacts', {}).get('json')}, "
                    f"image={daily_report.get('artifacts', {}).get('image')}, "
                    f"pdf={daily_report.get('artifacts', {}).get('pdf')}"
                )
                print(
                    f"周报产物: json={weekly_report.get('artifacts', {}).get('json')}, "
                    f"image={weekly_report.get('artifacts', {}).get('image')}, "
                    f"pdf={weekly_report.get('artifacts', {}).get('pdf')}"
                )
                print(
                    f"月报产物: json={monthly_report.get('artifacts', {}).get('json')}, "
                    f"image={monthly_report.get('artifacts', {}).get('image')}, "
                    f"pdf={monthly_report.get('artifacts', {}).get('pdf')}"
                )

                print(
                    f"额外模块输出: heart_3d={daily_report.get('artifacts', {}).get('module_files', {}).get('heart_3d')}, "
                    f"rehab_achievement={daily_report.get('artifacts', {}).get('module_files', {}).get('rehab_achievement')}"
                )
        
    except KeyboardInterrupt:
        print("\n\n检测到用户中断，正在关闭系统...")
    finally:
        # 关闭系统
        system.shutdown()


if __name__ == "__main__":
    main()
