#!/usr/bin/env python3
"""
冠心病PCI术后康复管理多智能体系统 V2.0
主程序入口 - 简化版
"""

import sys
from pathlib import Path
import asyncio

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from MyAgentSystem.multi_agent_system_v2.agent_cluster.agent_orchestrator import AgentOrchestrator


class PCIRehabSystemV2:
    def __init__(self, base_path: Path = None):
        if base_path is None:
            base_path = Path(__file__).parent.parent.parent
        
        self.base_path = base_path
        self.kb_initialized = False
        self.mas_initialized = False
        
        self.agent_orchestrator = None
    
    def initialize_knowledge_base(self, force_rebuild: bool = False) -> bool:
        try:
            print("=" * 60)
            print("初始化知识库系统 V2.0...(简化版)")
            print("=" * 60)
            
            print("\n知识库加载完成！")
            self.kb_initialized = True
            print("\n✅ 知识库系统初始化完成!")
            return True
            
        except Exception as e:
            print(f"\n❌ 知识库初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def initialize_multi_agent_system(self) -> bool:
        try:
            print("\n" + "=" * 60)
            print("初始化多智能体系统 V2.0...")
            print("=" * 60)
            
            mas_config = {
                "memory_path": str(self.base_path / "MyAgentSystem" / "multi_agent_system_v2" / "data" / "memory"),
                "learning_path": str(self.base_path / "MyAgentSystem" / "multi_agent_system_v2" / "data" / "learning"),
                "profile_path": str(self.base_path / "MyAgentSystem" / "multi_agent_system_v2" / "data" / "profiles"),
                "message_bus": {
                    "queue_max_size": 1000
                },
                "nlg": {
                    "patient_tone": "friendly",
                    "doctor_format": "structured"
                }
            }
            
            print("\n[1/3] 注册智能体...")
            self.agent_orchestrator = AgentOrchestrator(mas_config)
            
            print("\n[2/3] 初始化智能体...")
            success = self.agent_orchestrator.initialize()
            
            if success:
                print("\n[3/3] 系统就绪检查...")
                status = self.agent_orchestrator.get_system_status()
                print(f"已注册智能体: {status['agent_count']} 个")
                print(f"智能体列表: {', '.join(status['agents'])}")
                
                self.mas_initialized = True
                print("\n✅ 多智能体系统初始化完成!")
                return True
            else:
                print("\n❌ 多智能体系统初始化失败!")
                return False
                
        except Exception as e:
            print(f"\n❌ 多智能体系统初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def initialize(self, force_rebuild_kb: bool = False) -> bool:
        print("\n" + "=" * 60)
        print("冠心病PCI术后康复管理多智能体系统 V2.0")
        print("=" * 60)
        
        kb_success = self.initialize_knowledge_base(force_rebuild_kb)
        mas_success = self.initialize_multi_agent_system()
        
        overall_success = kb_success and mas_success
        
        print("\n" + "=" * 60)
        if overall_success:
            print("🎉 系统初始化成功! 可以开始使用。")
        else:
            print("⚠️  系统部分初始化失败，请检查错误信息。")
        print("=" * 60)
        
        return overall_success
    
    async def process_request_async(self, user_input: str, patient_id: str = "P_001", 
                                   end_type: str = "patient") -> dict:
        if not self.mas_initialized:
            return {"success": False, "error": "多智能体系统未初始化"}
        
        result = await self.agent_orchestrator.process_user_request_async(
            user_input, patient_id, end_type
        )
        
        return result
    
    def process_request(self, user_input: str, patient_id: str = "P_001", 
                       end_type: str = "patient") -> dict:
        return asyncio.run(self.process_request_async(user_input, patient_id, end_type))
    
    def submit_feedback(self, feedback: dict) -> dict:
        if not self.mas_initialized:
            return {"success": False, "error": "多智能体系统未初始化"}
        
        return self.agent_orchestrator.submit_feedback(feedback)
    
    def get_status(self) -> dict:
        return {
            "knowledge_base": {
                "initialized": self.kb_initialized
            },
            "multi_agent_system": self.agent_orchestrator.get_system_status() if self.mas_initialized else None
        }
    
    def shutdown(self):
        print("\n正在关闭系统...")
        if self.agent_orchestrator:
            self.agent_orchestrator.shutdown()
        print("系统已关闭。")


async def main_demo():
    system = PCIRehabSystemV2()
    
    try:
        system.initialize(force_rebuild_kb=False)
        
        print("\n" + "=" * 60)
        print("系统演示")
        print("=" * 60)
        
        test_queries = [
            ("我今天感觉有点累，应该怎么做？", "patient"),
            ("请给我一些运动建议", "patient"),
            ("生成一份医生报告", "doctor")
        ]
        
        for i, (query, end_type) in enumerate(test_queries, 1):
            print(f"\n{'─' * 60}")
            print(f"示例 {i} - {end_type.upper()}端:")
            print(f"用户输入: {query}")
            print(f"{'─' * 60}")
            
            result = await system.process_request_async(query, end_type=end_type)
            
            if result.get("success"):
                response = result.get("response", {})
                print(f"\n系统回复:")
                if isinstance(response, dict):
                    if "content" in response:
                        print(response["content"])
                    elif "structured_report" in response:
                        print("【医生端结构化报告】")
                        print(f"报告ID: {response['structured_report'].get('report_id', 'N/A')}")
                else:
                    print(response)
            else:
                print(f"错误: {result.get('error')}")
        
        print("\n" + "=" * 60)
        print("演示完成!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断，正在退出...")
    finally:
        system.shutdown()


if __name__ == "__main__":
    asyncio.run(main_demo())
