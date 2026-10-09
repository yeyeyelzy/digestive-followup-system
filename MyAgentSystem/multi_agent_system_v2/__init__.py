"""
冠心病PCI术后康复管理多智能体系统 V2.0
"""

__version__ = "2.0.0"
__all__ = []


def __getattr__(name):
    """延迟导入以避免循环导入问题"""
    if name == "PCIRehabSystemV2":
        from .main_v2 import PCIRehabSystemV2
        return PCIRehabSystemV2
    raise AttributeError(f"module {__name__} has no attribute {name}")
