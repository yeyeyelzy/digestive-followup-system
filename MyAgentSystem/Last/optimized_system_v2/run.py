"""
冠心病PCI术后康复管理多智能体系统V2.0 - 主程序入口
整合多智能体处理、RAG知识库、Fitabase数据处理
"""
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from optimized_system_v2.core.utils.config import config
from optimized_system_v2.core.rag_system.kb_manager import KnowledgeBaseManager
from optimized_system_v2.core.multi_agent.mas_manager import MultiAgentSystemManager


class PCIRehabSystem:
    """冠心病PCI术后康复管理系统主类"""
    
    def __init__(self):
        self.kb_manager = KnowledgeBaseManager()
        self.mas_manager = MultiAgentSystemManager()
        self.system_check_log = []
        
    def _log(self, message: str):
        """记录日志"""
        print(message)
        self.system_check_log.append(message)
        
    def initialize(self, force_rebuild_kb: bool = False) -> bool:
        """
        初始化整个系统
        
        Args:
            force_rebuild_kb: 是否强制重建知识库索引
            
        Returns:
            是否初始化成功
        """
        print("\n" + "="*80)
        print("🏥 冠心病PCI术后康复管理多智能体系统 V2.0")
        print("="*80)
        
        # 初始化知识库
        self._log("\n[1/2] 初始化知识库系统")
        kb_result = self.kb_manager.initialize(force_rebuild=force_rebuild_kb)
        
        # 初始化多智能体系统
        self._log("\n[2/2] 初始化多智能体系统")
        mas_result = self.mas_manager.initialize()
        
        overall_success = kb_result.get("success", False) and mas_result.get("success", False)
        
        print("\n" + "="*80)
        if overall_success:
            print("🎉 系统初始化完成！")
        else:
            print("⚠️  系统部分初始化失败，请检查日志")
        print("="*80)
        
        return overall_success
    
    def test_knowledge_base_search(self, test_queries: List[str] = None):
        """测试知识库检索"""
        if test_queries is None:
            test_queries = [
                "PCI术后患者的目标心率范围是多少？",
                "冠心病患者如何进行运动康复？",
                "PCI术后需要服用什么药物？"
            ]
        
        self._log("\n" + "="*80)
        self._log("🔍 知识库检索测试")
        self._log("="*80)
        
        all_results = {}
        for i, query in enumerate(test_queries, 1):
            self._log(f"\n--- 测试 {i}: {query} ---")
            results = self.kb_manager.search(query)
            all_results[query] = results
        
        return all_results
    
    def process_patients(self, patient_ids: List[str] = None):
        """
        处理患者数据，生成报告
        
        Args:
            patient_ids: 患者ID列表，默认处理所有患者
        """
        if patient_ids is None:
            patient_ids = ["P_001", "P_002", "P_003"]
        
        self._log("\n" + "="*80)
        self._log("👥 处理患者数据")
        self._log("="*80)
        
        all_results = {}
        for patient_id in patient_ids:
            result = self.mas_manager.process_patient(patient_id)
            all_results[patient_id] = result
        
        return all_results
    
    def save_system_check_report(self):
        """保存系统自检报告"""
        report_path = config.paths.system_check_output / f"系统自检报告_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        
        report_content = f"""# 系统自检报告

## 基本信息
- 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
- 系统版本: V2.0

## 详细日志

"""
        for line in self.system_check_log:
            report_content += f"{line}\n"
        
        # 添加知识库日志
        report_content += "\n\n## 知识库系统日志\n\n"
        for line in self.kb_manager.get_system_check_log():
            report_content += f"{line}\n"
        
        # 添加多智能体系统日志
        report_content += "\n\n## 多智能体系统日志\n\n"
        for line in self.mas_manager.get_system_check_log():
            report_content += f"{line}\n"
        
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self._log(f"\n📄 系统自检报告已保存: {report_path}")
        return report_path
    
    def run_full_flow(self, force_rebuild_kb: bool = False):
        """
        运行完整流程
        
        Args:
            force_rebuild_kb: 是否强制重建知识库索引
        """
        print("\n" + "="*80)
        print("🚀 运行完整系统流程")
        print("="*80)
        
        # 1. 初始化系统
        success = self.initialize(force_rebuild_kb=force_rebuild_kb)
        if not success:
            self._log("\n❌ 系统初始化失败，终止流程")
            return False
        
        # 2. 测试知识库检索
        self._log("\n" + "="*80)
        self._log("📚 测试知识库检索")
        self.test_knowledge_base_search()
        
        # 3. 处理患者数据
        self._log("\n" + "="*80)
        self._log("👤 处理患者数据")
        self.process_patients()
        
        # 4. 保存系统自检报告
        self.save_system_check_report()
        
        # 同时保存知识库单独的自检报告
        self.kb_manager.save_system_check_report()
        
        print("\n" + "="*80)
        print("✅ 完整流程执行完成！")
        print("="*80)
        print("\n📁 输出文件位置:")
        print(f"   - 患者端报告: {config.paths.patient_output}")
        print(f"   - 家属端报告: {config.paths.family_output}")
        print(f"   - 医生端报告: {config.paths.doctor_output}")
        print(f"   - 系统自检: {config.paths.system_check_output}")
        
        return True


def main():
    """主函数"""
    print("\n" + "="*80)
    print("🏥 冠心病PCI术后康复管理多智能体系统 V2.0")
    print("="*80)
    print("\n请选择操作:")
    print("  1. 运行完整流程（推荐）")
    print("  2. 仅初始化系统")
    print("  3. 仅测试知识库检索")
    print("  4. 仅处理患者数据")
    print("  5. 强制重建知识库索引并运行完整流程")
    
    try:
        choice = input("\n请输入选项 (1-5，默认1): ").strip() or "1"
        
        system = PCIRehabSystem()
        
        if choice == "1":
            system.run_full_flow(force_rebuild_kb=False)
        elif choice == "2":
            system.initialize(force_rebuild_kb=False)
            system.save_system_check_report()
        elif choice == "3":
            system.initialize(force_rebuild_kb=False)
            system.test_knowledge_base_search()
            system.save_system_check_report()
        elif choice == "4":
            system.initialize(force_rebuild_kb=False)
            system.process_patients()
            system.save_system_check_report()
        elif choice == "5":
            system.run_full_flow(force_rebuild_kb=True)
        else:
            print("❌ 无效选项")
            
    except KeyboardInterrupt:
        print("\n\n👋 用户中断，正在退出...")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
