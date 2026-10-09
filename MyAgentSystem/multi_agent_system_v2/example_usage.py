#!/usr/bin/env python3
"""
V2.0系统使用示例
"""

import sys
from pathlib import Path
import asyncio

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from MyAgentSystem.multi_agent_system_v2 import PCIRehabSystemV2


async def simple_example():
    """简单使用示例"""
    
    print("=" * 60)
    print("冠心病PCI术后康复管理多智能体系统 V2.0 - 示例")
    print("=" * 60)
    
    system = PCIRehabSystemV2()
    
    try:
        print("\n[1/3] 初始化系统...")
        success = system.initialize(force_rebuild_kb=False)
        
        if not success:
            print("系统初始化失败，请检查错误信息")
            return
        
        print("\n[2/3] 系统状态检查...")
        status = system.get_status()
        print(f"知识库初始化: {status['knowledge_base']['initialized']}")
        print(f"多智能体系统初始化: {status['multi_agent_system']['initialized']}")
        if status['multi_agent_system']['initialized']:
            print(f"已注册智能体: {status['multi_agent_system']['agent_count']} 个")
        
        print("\n[3/3] 测试请求处理...")
        
        test_cases = [
            {
                "query": "我今天感觉有点胸痛，应该怎么办？",
                "patient_id": "P_001",
                "end_type": "patient"
            },
            {
                "query": "请给我制定一个本周的运动计划",
                "patient_id": "P_001",
                "end_type": "patient"
            },
            {
                "query": "生成患者P_001的医生报告",
                "patient_id": "P_001",
                "end_type": "doctor"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'─' * 60}")
            print(f"测试用例 {i}:")
            print(f"患者ID: {test_case['patient_id']}")
            print(f"端类型: {test_case['end_type']}")
            print(f"用户输入: {test_case['query']}")
            print(f"{'─' * 60}")
            
            result = await system.process_request_async(
                test_case["query"],
                test_case["patient_id"],
                test_case["end_type"]
            )
            
            if result.get("success"):
                print("\n✅ 请求成功!")
                response = result.get("response", {})
                
                if isinstance(response, dict):
                    if "content" in response:
                        print(f"\n回复内容:\n{response['content']}")
                    elif "structured_report" in response:
                        print("\n【医生端结构化报告】")
                        report = response["structured_report"]
                        print(f"报告ID: {report.get('report_id', 'N/A')}")
                        print(f"生成时间: {report.get('generated_at', 'N/A')}")
                        print(f"总体风险等级: {report.get('risk_assessment', {}).get('overall_risk_level', 'N/A')}")
                else:
                    print(f"\n回复:\n{response}")
            else:
                print(f"\n❌ 请求失败: {result.get('error')}")
        
        print("\n" + "=" * 60)
        print("测试反馈提交...")
        
        feedback = {
            "patient_id": "P_001",
            "feedback_type": "rehab_plan",
            "content": "运动计划很有帮助，但强度可以稍微降低一点",
            "rating": 4,
            "context": {
                "plan_id": "test_plan_001",
                "session_id": "test_session_001"
            }
        }
        
        feedback_result = system.submit_feedback(feedback)
        if feedback_result.get("success"):
            print("✅ 反馈提交成功!")
            print(f"反馈ID: {feedback_result.get('result', {}).get('feedback_id', 'N/A')}")
        else:
            print(f"❌ 反馈提交失败: {feedback_result.get('error')}")
        
        print("\n" + "=" * 60)
        print("示例运行完成!")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\n\n用户中断，正在退出...")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        system.shutdown()


async def interactive_mode():
    """交互式模式"""
    
    print("=" * 60)
    print("冠心病PCI术后康复管理多智能体系统 V2.0 - 交互模式")
    print("=" * 60)
    print("\n提示:")
    print("  - 输入 'quit' 或 'exit' 退出")
    print("  - 输入 'status' 查看系统状态")
    print("  - 输入 'switch <patient_id>' 切换患者")
    print("  - 输入 'end <type>' 切换端类型 (patient/family/doctor)")
    print("=" * 60)
    
    system = PCIRehabSystemV2()
    
    try:
        if not system.initialize(force_rebuild_kb=False):
            print("系统初始化失败!")
            return
        
        current_patient = "P_001"
        current_end = "patient"
        
        while True:
            try:
                print(f"\n[{current_patient} - {current_end}] ", end="")
                user_input = input().strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit"]:
                    print("再见!")
                    break
                
                if user_input.lower() == "status":
                    status = system.get_status()
                    print(f"\n系统状态:")
                    print(f"  知识库: {'✅' if status['knowledge_base']['initialized'] else '❌'}")
                    print(f"  多智能体: {'✅' if status['multi_agent_system']['initialized'] else '❌'}")
                    continue
                
                if user_input.lower().startswith("switch "):
                    parts = user_input.split(maxsplit=1)
                    if len(parts) > 1:
                        current_patient = parts[1]
                        print(f"已切换到患者: {current_patient}")
                    continue
                
                if user_input.lower().startswith("end "):
                    parts = user_input.split(maxsplit=1)
                    if len(parts) > 1:
                        new_end = parts[1].lower()
                        if new_end in ["patient", "family", "doctor"]:
                            current_end = new_end
                            print(f"已切换到端类型: {current_end}")
                        else:
                            print("无效的端类型，请使用 patient/family/doctor")
                    continue
                
                print(f"\n正在处理...")
                result = await system.process_request_async(
                    user_input, current_patient, current_end
                )
                
                if result.get("success"):
                    response = result.get("response", {})
                    if isinstance(response, dict) and "content" in response:
                        print(f"\n{response['content']}")
                    elif isinstance(response, dict) and "structured_report" in response:
                        print("\n【医生端结构化报告】")
                        print(f"报告ID: {response['structured_report'].get('report_id', 'N/A')}")
                    else:
                        print(f"\n{response}")
                else:
                    print(f"\n错误: {result.get('error')}")
                    
            except KeyboardInterrupt:
                print("\n\n输入 'quit' 退出")
            except Exception as e:
                print(f"\n处理错误: {e}")
                
    except Exception as e:
        print(f"系统错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        system.shutdown()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="冠心病PCI术后康复管理多智能体系统 V2.0")
    parser.add_argument("--mode", choices=["demo", "interactive"], default="demo",
                       help="运行模式: demo(演示) 或 interactive(交互)")
    
    args = parser.parse_args()
    
    if args.mode == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(simple_example())
