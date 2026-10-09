#!/usr/bin/env python3
"""
测试和调试V2.0系统的导入问题
"""

import sys
from pathlib import Path

print("=" * 80)
print("V2.0系统导入调试工具")
print("=" * 80)

base_path = Path(__file__).parent
print(f"\n工作目录: {base_path}")
print(f"Python路径: {sys.executable}")
print(f"Python版本: {sys.version}")

print("\n" + "=" * 80)
print("检查目录结构...")
print("=" * 80)

required_dirs = [
    "MyKnownlege/knowledge_base_v2",
    "MyAgentSystem/multi_agent_system_v2"
]

for dir_path in required_dirs:
    full_path = base_path / dir_path
    if full_path.exists():
        print(f"✓ 找到目录: {dir_path}")
    else:
        print(f"✗ 目录不存在: {dir_path}")

print("\n" + "=" * 80)
print("添加路径到sys.path...")
print("=" * 80)

sys.path.insert(0, str(base_path))
print(f"已添加: {base_path}")

print("\n" + "=" * 80)
print("测试1: 检查MyKnownlege和MyAgentSystem是否可导入...")
print("=" * 80)

try:
    import MyKnownlege
    print("✓ MyKnownlege 导入成功")
except Exception as e:
    print(f"✗ MyKnownlege 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    import MyAgentSystem
    print("✓ MyAgentSystem 导入成功")
except Exception as e:
    print(f"✗ MyAgentSystem 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试2: 检查知识库V2.0模块...")
print("=" * 80)

try:
    from MyKnownlege.knowledge_base_v2.config import settings
    print("✓ MyKnownlege.knowledge_base_v2.config.settings 导入成功")
except Exception as e:
    print(f"✗ MyKnownlege.knowledge_base_v2.config.settings 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from MyKnownlege.knowledge_base_v2.src import hash_checker
    print("✓ MyKnownlege.knowledge_base_v2.src.hash_checker 导入成功")
except Exception as e:
    print(f"✗ MyKnownlege.knowledge_base_v2.src.hash_checker 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试3: 检查多智能体系统V2.0模块...")
print("=" * 80)

try:
    from MyAgentSystem.multi_agent_system_v2.agent_base import base_agent
    print("✓ MyAgentSystem.multi_agent_system_v2.agent_base.base_agent 导入成功")
except Exception as e:
    print(f"✗ MyAgentSystem.multi_agent_system_v2.agent_base.base_agent 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from MyAgentSystem.multi_agent_system_v2.message_bus import message_queue
    print("✓ MyAgentSystem.multi_agent_system_v2.message_bus.message_queue 导入成功")
except Exception as e:
    print(f"✗ MyAgentSystem.multi_agent_system_v2.message_bus.message_queue 导入失败: {e}")
    import traceback
    traceback.print_exc()

try:
    from MyAgentSystem.multi_agent_system_v2.memory_system import memory_manager
    print("✓ MyAgentSystem.multi_agent_system_v2.memory_system.memory_manager 导入成功")
except Exception as e:
    print(f"✗ MyAgentSystem.multi_agent_system_v2.memory_system.memory_manager 导入失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试4: 检查app_v2.py和main_v2.py中的具体导入...")
print("=" * 80)

print("\n--- 检查app_v2.py的导入 ---")
try:
    with open(base_path / "MyAgentSystem/multi_agent_system_v2/app_v2.py", encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        import_lines = [l for l in lines if l.strip().startswith('from ') or l.strip().startswith('import ')]
        print("app_v2.py中的导入语句:")
        for line in import_lines:
            print(f"  {line}")
except Exception as e:
    print(f"读取app_v2.py失败: {e}")

print("\n--- 检查main_v2.py的导入 ---")
try:
    with open(base_path / "MyAgentSystem/multi_agent_system_v2/main_v2.py", encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        import_lines = [l for l in lines if l.strip().startswith('from ') or l.strip().startswith('import ')]
        print("main_v2.py中的导入语句:")
        for line in import_lines:
            print(f"  {line}")
except Exception as e:
    print(f"读取main_v2.py失败: {e}")

print("\n" + "=" * 80)
print("调试完成!")
print("=" * 80)
