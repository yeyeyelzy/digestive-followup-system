import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.patches import FancyBboxPatch

# 全局绘图配置
plt.rcParams["font.sans-serif"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 120

# ====================== 图1：多智能体设计与协作关系流程图 ======================
def draw_agent_collaboration():
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_title("冠心病PCI术后康复系统-多智能体设计与协作关系", fontsize=14, fontweight="bold", pad=20)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 12)
    ax.axis("off")

    # 定义节点层级与位置
    nodes = {
        # 输入层
        "user_input": {"pos": (1, 11), "label": "用户请求/时序数据", "color": "#e8f4f8", "type": "input"},
        # 编排中枢层
        "orchestrator": {"pos": (3, 11), "label": "AgentOrchestrator\n智能体编排器", "color": "#d1e7dd", "type": "core"},
        "message_bus": {"pos": (3, 9), "label": "MessageBus\n消息总线", "color": "#f8d7da", "type": "infra"},
        "memory_system": {"pos": (3, 7), "label": "MemorySystem\n四层记忆体系", "color": "#f8d7da", "type": "infra"},
        # 核心智能体层
        "global_orchestrator": {"pos": (5, 11), "label": "全局调度智能体\n(意图识别/流程控制)", "color": "#cfe2ff", "type": "agent"},
        "patient_profile": {"pos": (5, 9.5), "label": "患者画像智能体\n(全周期画像管理)", "color": "#cfe2ff", "type": "agent"},
        "data_fusion": {"pos": (5, 8), "label": "数据融合智能体\n(多模态数据解析)", "color": "#cfe2ff", "type": "agent"},
        "rehab_decision": {"pos": (5, 6.5), "label": "康复决策智能体\n(个性化方案生成)", "color": "#cfe2ff", "type": "agent"},
        "evidence_validation": {"pos": (5, 5), "label": "循证校验智能体\n(医学合规性校验)", "color": "#cfe2ff", "type": "agent"},
        "emotional_empathy": {"pos": (5, 3.5), "label": "情感共情智能体\n(情绪识别/共情输出)", "color": "#cfe2ff", "type": "agent"},
        "doctor_report": {"pos": (5, 2), "label": "医生报告智能体\n(临床结构化报告)", "color": "#cfe2ff", "type": "agent"},
        "incremental_learner": {"pos": (5, 0.5), "label": "增量学习智能体\n(反馈/数据迭代优化)", "color": "#cfe2ff", "type": "agent"},
        # 输出层
        "nlg_generator": {"pos": (8, 6), "label": "MultiEndNLG\n多端差异化内容生成", "color": "#fff3cd", "type": "output"},
        "final_response": {"pos": (10, 6), "label": "最终响应\n(患者/家属/医生端)", "color": "#e8f4f8", "type": "output"},
    }

    # 绘制节点
    for node, info in nodes.items():
        x, y = info["pos"]
        # 绘制圆角矩形
        bbox = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, boxstyle="round,pad=0.1",
                              facecolor=info["color"], edgecolor="#333", linewidth=1, zorder=2)
        ax.add_patch(bbox)
        # 绘制文本
        ax.text(x, y, info["label"], ha="center", va="center", fontsize=9, zorder=3)

    # 定义数据流箭头（主流程+协作关系）
    arrows = [
        # 主流程链路
        ("user_input", "orchestrator", "用户请求输入", "->"),
        ("orchestrator", "global_orchestrator", "任务分发", "->"),
        ("global_orchestrator", "patient_profile", "获取患者画像", "->"),
        ("patient_profile", "data_fusion", "患者基线数据", "->"),
        ("data_fusion", "rehab_decision", "多模态融合数据", "->"),
        ("rehab_decision", "evidence_validation", "初步康复方案", "->"),
        ("evidence_validation", "rehab_decision", "校验不通过/回退优化", "<->"),
        ("evidence_validation", "emotional_empathy", "校验通过方案", "->"),
        ("emotional_empathy", "doctor_report", "情绪特征+方案", "->"),
        ("doctor_report", "nlg_generator", "结构化数据", "->"),
        ("nlg_generator", "final_response", "分端内容输出", "->"),
        # 基础设施联动
        ("orchestrator", "message_bus", "智能体通信注册", "->"),
        ("orchestrator", "memory_system", "记忆读写管理", "->"),
        ("message_bus", "global_orchestrator", "任务消息分发", "<->"),
        ("message_bus", "patient_profile", "任务消息分发", "<->"),
        ("message_bus", "data_fusion", "任务消息分发", "<->"),
        ("message_bus", "rehab_decision", "任务消息分发", "<->"),
        ("message_bus", "evidence_validation", "任务消息分发", "<->"),
        ("message_bus", "emotional_empathy", "任务消息分发", "<->"),
        ("message_bus", "doctor_report", "任务消息分发", "<->"),
        ("message_bus", "incremental_learner", "任务消息分发", "<->"),
        ("memory_system", "global_orchestrator", "会话/患者记忆读写", "<->"),
        ("memory_system", "patient_profile", "患者长期记忆读写", "<->"),
        ("memory_system", "incremental_learner", "学习数据持久化", "<->"),
        # 增量学习闭环
        ("final_response", "incremental_learner", "用户反馈/执行数据", "->"),
        ("incremental_learner", "memory_system", "优化规则更新", "->"),
    ]

    # 绘制箭头与标注
    for start, end, label, arrow_type in arrows:
        x1, y1 = nodes[start]["pos"]
        x2, y2 = nodes[end]["pos"]
        # 箭头样式
        if arrow_type == "<->":
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="<->", color="#2c3e50", lw=1.2, zorder=1))
        else:
            ax.annotate("", xy=(x2-0.8, y2), xytext=(x1+0.8, y1),
                        arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1.2, zorder=1))
        # 标注文本位置
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2 + 0.2
        ax.text(mid_x, mid_y, label, ha="center", va="center", fontsize=7, color="#c0392b", zorder=3)

    # 绘制层级分隔线
    ax.axvline(x=2, ymin=0, ymax=1, color="#999", linestyle="--", lw=0.8)
    ax.axvline(x=4, ymin=0, ymax=1, color="#999", linestyle="--", lw=0.8)
    ax.axvline(x=7, ymin=0, ymax=1, color="#999", linestyle="--", lw=0.8)
    ax.axvline(x=9, ymin=0, ymax=1, color="#999", linestyle="--", lw=0.8)

    # 层级标注
    ax.text(1, 11.8, "输入层", ha="center", va="center", fontsize=10, fontweight="bold", color="#2c3e50")
    ax.text(3, 11.8, "编排中枢层", ha="center", va="center", fontsize=10, fontweight="bold", color="#2c3e50")
    ax.text(5, 11.8, "核心智能体集群", ha="center", va="center", fontsize=10, fontweight="bold", color="#2c3e50")
    ax.text(8, 11.8, "输出层", ha="center", va="center", fontsize=10, fontweight="bold", color="#2c3e50")

    plt.tight_layout()
    return fig

# ====================== 图2：多智能体与向量数据库的交互关系 ======================
def draw_agent_vector_relation():
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_title("多智能体系统与向量数据库(知识库RAG)交互关系", fontsize=14, fontweight="bold", pad=20)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # 节点定义
    nodes = {
        "user_request": {"pos": (1, 9), "label": "用户请求", "color": "#e8f4f8"},
        "orchestrator": {"pos": (3, 9), "label": "AgentOrchestrator\n智能体编排器", "color": "#d1e7dd"},
        # 调用RAG的核心智能体
        "rehab_agent": {"pos": (5, 8), "label": "康复决策智能体", "color": "#cfe2ff"},
        "evidence_agent": {"pos": (5, 6.5), "label": "循证校验智能体", "color": "#cfe2ff"},
        "doctor_agent": {"pos": (5, 5), "label": "医生报告智能体", "color": "#cfe2ff"},
        # RAG检索引擎
        "retriever": {"pos": (7, 6.5), "label": "MultiLayerRetriever\n多层级检索引擎", "color": "#fff3cd"},
        # 检索四层架构
        "tag_filter": {"pos": (9, 9), "label": "第一层：标签前置过滤", "color": "#f8d7da"},
        "relation_recall": {"pos": (9, 7.5), "label": "第二层：关联文件召回", "color": "#f8d7da"},
        "vector_search": {"pos": (9, 6), "label": "第三层：向量相似性检索", "color": "#f8d7da"},
        "rerank": {"pos": (9, 4.5), "label": "第四层：结果重排序", "color": "#f8d7da"},
        # 底层存储
        "vector_db": {"pos": (9, 3), "label": "Chroma向量数据库", "color": "#d1e7dd"},
        "feature_index": {"pos": (9, 1.5), "label": "文件/片段级特征索引", "color": "#d1e7dd"},
        "raw_kb": {"pos": (9, 0.5), "label": "原始医学知识库", "color": "#e8f4f8"},
    }

    # 绘制节点
    for node, info in nodes.items():
        x, y = info["pos"]
        bbox = FancyBboxPatch((x-0.8, y-0.3), 1.6, 0.6, boxstyle="round,pad=0.1",
                              facecolor=info["color"], edgecolor="#333", linewidth=1, zorder=2)
        ax.add_patch(bbox)
        ax.text(x, y, info["label"], ha="center", va="center", fontsize=9, zorder=3)

    # 数据流箭头
    arrows = [
        # 请求链路
        ("user_request", "orchestrator", "用户查询输入", "->"),
        ("orchestrator", "rehab_agent", "方案生成任务", "->"),
        ("orchestrator", "evidence_agent", "循证校验任务", "->"),
        ("orchestrator", "doctor_agent", "报告生成任务", "->"),
        # 智能体调用检索引擎
        ("rehab_agent", "retriever", "康复方案知识查询", "->"),
        ("evidence_agent", "retriever", "循证依据检索", "->"),
        ("doctor_agent", "retriever", "临床指南查询", "->"),
        # 检索引擎四层执行流程
        ("retriever", "tag_filter", "查询标签提取", "->"),
        ("tag_filter", "relation_recall", "候选片段过滤", "->"),
        ("relation_recall", "vector_search", "候选集扩展", "->"),
        ("vector_search", "rerank", "语义相似匹配", "->"),
        # 底层数据读取
        ("vector_search", "vector_db", "向量相似度计算", "->"),
        ("tag_filter", "feature_index", "标签匹配", "->"),
        ("relation_recall", "feature_index", "关联关系读取", "->"),
        ("vector_db", "feature_index", "向量-特征映射", "<->"),
        ("feature_index", "raw_kb", "特征来源", "->"),
        # 结果返回链路
        ("rerank", "retriever", "重排序后检索结果", "<-"),
        ("retriever", "rehab_agent", "医学知识支撑", "<-"),
        ("retriever", "evidence_agent", "循证依据结果", "<-"),
        ("retriever", "doctor_agent", "临床指南内容", "<-"),
        ("rehab_agent", "orchestrator", "带循证依据的方案", "<-"),
        ("evidence_agent", "orchestrator", "校验结果+依据", "<-"),
        ("doctor_agent", "orchestrator", "带指南标注的报告", "<-"),
    ]

    # 绘制箭头与标注
    for start, end, label, arrow_type in arrows:
        x1, y1 = nodes[start]["pos"]
        x2, y2 = nodes[end]["pos"]
        if arrow_type == "<-":
            # 反向箭头
            ax.annotate("", xy=(x1+0.8, y1), xytext=(x2-0.8, y2),
                        arrowprops=dict(arrowstyle="->", color="#2980b9", lw=1.2, zorder=1))
        elif arrow_type == "<->":
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="<->", color="#2980b9", lw=1.2, zorder=1))
        else:
            ax.annotate("", xy=(x2-0.8, y2), xytext=(x1+0.8, y1),
                        arrowprops=dict(arrowstyle="->", color="#2980b9", lw=1.2, zorder=1))
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2 + 0.2
        ax.text(mid_x, mid_y, label, ha="center", va="center", fontsize=7, color="#c0392b", zorder=3)

    # 层级标注
    ax.text(1, 9.8, "请求入口", ha="center", va="center", fontsize=10, fontweight="bold")
    ax.text(3, 9.8, "编排层", ha="center", va="center", fontsize=10, fontweight="bold")
    ax.text(5, 9.8, "业务智能体", ha="center", va="center", fontsize=10, fontweight="bold")
    ax.text(7, 9.8, "RAG引擎", ha="center", va="center", fontsize=10, fontweight="bold")
    ax.text(9, 9.8, "检索架构与存储", ha="center", va="center", fontsize=10, fontweight="bold")

    plt.tight_layout()
    return fig

# ====================== 图3：向量数据库构建全流程 ======================
def draw_vector_db_build():
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_title("向量数据库(知识库RAG)构建全流程", fontsize=14, fontweight="bold", pad=20)
    ax.set_xlim(0, 8)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # 流程节点（按执行顺序纵向排列）
    steps = [
        {"id": "start", "pos": (4, 9.5), "label": "系统启动/知识库变更触发", "color": "#e8f4f8"},
        {"id": "hash_checker", "pos": (4, 8.5), "label": "HashChecker 哈希变更检测", "color": "#d1e7dd"},
        {"id": "scan_kb", "pos": (4, 7.5), "label": "全量扫描知识库文件", "color": "#cfe2ff"},
        {"id": "hash_compare", "pos": (4, 6.5), "label": "新旧哈希清单比对", "color": "#cfe2ff"},
        {"id": "change_judge", "pos": (4, 5.5), "label": "是否有变更？", "color": "#fff3cd"},
        {"id": "load_index", "pos": (2, 4.5), "label": "加载现有索引与向量库", "color": "#f8d7da"},
        {"id": "feature_engineer", "pos": (6, 4.5), "label": "FeatureEngineer 特征工程", "color": "#f8d7da"},
        {"id": "file_index", "pos": (6, 3.5), "label": "文件级关联索引构建", "color": "#cfe2ff"},
        {"id": "segment_split", "pos": (6, 2.5), "label": "语义块切分+片段级特征索引", "color": "#cfe2ff"},
        {"id": "vector_embedding", "pos": (6, 1.5), "label": "医疗领域向量嵌入生成", "color": "#cfe2ff"},
        {"id": "vector_db_save", "pos": (6, 0.5), "label": "写入Chroma向量库+索引持久化", "color": "#d1e7dd"},
        {"id": "retriever_load", "pos": (4, -0.5), "label": "MultiLayerRetriever 检索引擎加载就绪", "color": "#e8f4f8"},
    ]

    # 绘制节点
    for step in steps:
        x, y = step["pos"]
        bbox = FancyBboxPatch((x-1.2, y-0.3), 2.4, 0.6, boxstyle="round,pad=0.1",
                              facecolor=step["color"], edgecolor="#333", linewidth=1, zorder=2)
        ax.add_patch(bbox)
        ax.text(x, y, step["label"], ha="center", va="center", fontsize=9, zorder=3)

    # 流程箭头
    arrows = [
        ("start", "hash_checker", "", "->"),
        ("hash_checker", "scan_kb", "", "->"),
        ("scan_kb", "hash_compare", "", "->"),
        ("hash_compare", "change_judge", "", "->"),
        ("change_judge", "load_index", "无变更", "->"),
        ("change_judge", "feature_engineer", "有变更/首次启动", "->"),
        ("feature_engineer", "file_index", "", "->"),
        ("file_index", "segment_split", "", "->"),
        ("segment_split", "vector_embedding", "", "->"),
        ("vector_embedding", "vector_db_save", "", "->"),
        ("load_index", "retriever_load", "", "->"),
        ("vector_db_save", "retriever_load", "", "->"),
    ]

    # 绘制箭头
    for start, end, label, arrow_type in arrows:
        # 找到起止节点位置
        start_node = next(s for s in steps if s["id"] == start)
        end_node = next(s for s in steps if s["id"] == end)
        x1, y1 = start_node["pos"]
        x2, y2 = end_node["pos"]

        # 特殊处理分支箭头
        if start == "change_judge" and end == "load_index":
            # 左分支
            ax.annotate("", xy=(x2+1.2, y2), xytext=(x1-1.2, y1),
                        arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1.2, zorder=1))
            ax.text((x1+x2)/2 - 0.5, (y1+y2)/2, label, ha="center", va="center", fontsize=8, color="#c0392b")
        elif start == "change_judge" and end == "feature_engineer":
            # 右分支
            ax.annotate("", xy=(x2-1.2, y2), xytext=(x1+1.2, y1),
                        arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1.2, zorder=1))
            ax.text((x1+x2)/2 + 0.5, (y1+y2)/2, label, ha="center", va="center", fontsize=8, color="#c0392b")
        else:
            # 垂直箭头
            ax.annotate("", xy=(x2, y2+0.3), xytext=(x1, y1-0.3),
                        arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1.2, zorder=1))
            if label:
                ax.text((x1+x2)/2, (y1+y2)/2, label, ha="center", va="center", fontsize=8, color="#c0392b")

    # 增量更新标注
    ax.text(6, 5, "增量更新：仅处理变更文件", ha="center", va="center", fontsize=8, color="#27ae60", fontweight="bold")
    plt.tight_layout()
    return fig

# ====================== 图4：多智能体系统与若依框架的集成关系 ======================
def draw_ruoyi_integration():
    fig, ax = plt.subplots(figsize=(14, 9))
    ax.set_title("多智能体系统与若依(RuoYi)框架集成关系", fontsize=14, fontweight="bold", pad=20)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # 分层节点定义
    layers = {
        "front_end": {"y": 9, "nodes": [
            {"id": "patient_web", "pos": (2, 9), "label": "患者端Web/小程序", "color": "#e8f4f8"},
            {"id": "doctor_web", "pos": (5, 9), "label": "医生端管理页面", "color": "#e8f4f8"},
            {"id": "admin_web", "pos": (8, 9), "label": "平台管理端页面", "color": "#e8f4f8"},
        ]},
        "ruoyi_controller": {"y": 7.5, "nodes": [
            {"id": "ruoyi_controller", "pos": (5, 7.5), "label": "若依Controller层\n(请求拦截/权限校验/参数解析)", "color": "#d1e7dd"},
        ]},
        "ruoyi_service": {"y": 6, "nodes": [
            {"id": "user_service", "pos": (2, 6), "label": "用户管理服务", "color": "#cfe2ff"},
            {"id": "patient_service", "pos": (4, 6), "label": "患者管理服务", "color": "#cfe2ff"},
            {"id": "rehab_service", "pos": (6, 6), "label": "康复方案管理服务", "color": "#cfe2ff"},
            {"id": "kb_service", "pos": (8, 6), "label": "知识库管理服务", "color": "#cfe2ff"},
        ]},
        "adapter_layer": {"y": 4.5, "nodes": [
            {"id": "system_adapter", "pos": (5, 4.5), "label": "多智能体系统适配层\n(接口封装/数据转换/异常处理)", "color": "#fff3cd"},
        ]},
        "mas_core": {"y": 3, "nodes": [
            {"id": "mas_main", "pos": (5, 3), "label": "PCIRehabSystemV2\n多智能体系统主入口", "color": "#d1e7dd"},
            {"id": "agent_orchestrator", "pos": (5, 2), "label": "AgentOrchestrator\n智能体编排核心", "color": "#f8d7da"},
        ]},
        "data_layer": {"y": 0.5, "nodes": [
            {"id": "mysql_db", "pos": (2, 0.5), "label": "MySQL业务数据库\n(若依核心库/患者业务库)", "color": "#cfe2ff"},
            {"id": "chroma_db", "pos": (5, 0.5), "label": "Chroma向量数据库\n(医学知识库向量)", "color": "#cfe2ff"},
            {"id": "file_storage", "pos": (8, 0.5), "label": "文件存储\n(知识库文件/康复报告)", "color": "#cfe2ff"},
        ]},
    }

    # 绘制所有节点
    for layer in layers.values():
        for node in layer["nodes"]:
            x, y = node["pos"]
            bbox = FancyBboxPatch((x-0.9, y-0.3), 1.8, 0.6, boxstyle="round,pad=0.1",
                                  facecolor=node["color"], edgecolor="#333", linewidth=1, zorder=2)
            ax.add_patch(bbox)
            ax.text(x, y, node["label"], ha="center", va="center", fontsize=9, zorder=3)

    # 数据流箭头
    arrows = [
        # 前端到控制器
        ("patient_web", "ruoyi_controller", "HTTP请求", "->"),
        ("doctor_web", "ruoyi_controller", "HTTP请求", "->"),
        ("admin_web", "ruoyi_controller", "HTTP请求", "->"),
        # 控制器到服务层
        ("ruoyi_controller", "user_service", "用户相关请求", "->"),
        ("ruoyi_controller", "patient_service", "患者数据请求", "->"),
        ("ruoyi_controller", "rehab_service", "康复方案请求", "->"),
        ("ruoyi_controller", "kb_service", "知识库管理请求", "->"),
        # 服务层到适配层
        ("patient_service", "system_adapter", "患者数据/康复请求转发", "->"),
        ("rehab_service", "system_adapter", "方案生成/报告生成请求", "->"),
        ("kb_service", "system_adapter", "知识库更新/检索请求", "->"),
        # 适配层到多智能体核心
        ("system_adapter", "mas_main", "标准化业务请求", "->"),
        ("mas_main", "agent_orchestrator", "任务初始化与编排", "->"),
        # 多智能体到数据层
        ("agent_orchestrator", "mysql_db", "患者数据读写/业务数据持久化", "<->"),
        ("agent_orchestrator", "chroma_db", "知识库向量检索/更新", "<->"),
        ("agent_orchestrator", "file_storage", "报告文件/知识库文件读写", "<->"),
        # 若依框架与数据层的原生交互
        ("user_service", "mysql_db", "用户/权限数据读写", "<->"),
        ("patient_service", "mysql_db", "患者基础数据读写", "<->"),
        ("rehab_service", "mysql_db", "康复方案数据读写", "<->"),
        ("kb_service", "file_storage", "知识库文件管理", "<->"),
        # 结果返回链路
        ("agent_orchestrator", "mas_main", "处理结果返回", "<-"),
        ("mas_main", "system_adapter", "业务结果封装", "<-"),
        ("system_adapter", "patient_service", "康复响应结果", "<-"),
        ("system_adapter", "rehab_service", "方案/报告结果", "<-"),
        ("system_adapter", "kb_service", "检索/更新结果", "<-"),
        ("patient_service", "ruoyi_controller", "响应数据", "<-"),
        ("rehab_service", "ruoyi_controller", "响应数据", "<-"),
        ("kb_service", "ruoyi_controller", "响应数据", "<-"),
        ("user_service", "ruoyi_controller", "响应数据", "<-"),
        ("ruoyi_controller", "patient_web", "HTTP响应", "<-"),
        ("ruoyi_controller", "doctor_web", "HTTP响应", "<-"),
        ("ruoyi_controller", "admin_web", "HTTP响应", "<-"),
    ]

    # 绘制箭头与标注
    for start, end, label, arrow_type in arrows:
        # 查找节点
        start_node = None
        end_node = None
        for layer in layers.values():
            for node in layer["nodes"]:
                if node["id"] == start:
                    start_node = node
                if node["id"] == end:
                    end_node = node
        if not start_node or not end_node:
            continue

        x1, y1 = start_node["pos"]
        x2, y2 = end_node["pos"]

        if arrow_type == "<-":
            ax.annotate("", xy=(x1, y1+0.3), xytext=(x2, y2-0.3),
                        arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1, zorder=1))
        elif arrow_type == "<->":
            ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                        arrowprops=dict(arrowstyle="<->", color="#2c3e50", lw=1, zorder=1))
        else:
            ax.annotate("", xy=(x2, y2+0.3), xytext=(x1, y1-0.3),
                        arrowprops=dict(arrowstyle="->", color="#2c3e50", lw=1, zorder=1))

        # 标注文本
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        if abs(y1 - y2) > 0.5:
            mid_y += 0.1
        ax.text(mid_x, mid_y, label, ha="center", va="center", fontsize=7, color="#c0392b", zorder=3)

    # 层级分隔线与标注
    layer_y = [9.8, 8.5, 7, 5.2, 3.8, 2.5, 1.2]
    layer_names = ["前端应用层", "若依控制层", "若依业务服务层", "多智能体适配层", "多智能体核心层", "智能体编排层", "数据持久化层"]
    for y, name in zip(layer_y, layer_names):
        ax.axhline(y=y, xmin=0, xmax=1, color="#999", linestyle="--", lw=0.8)
        ax.text(0.2, y+0.1, name, ha="left", va="center", fontsize=10, fontweight="bold", color="#2c3e50")

    # 若依核心能力标注
    ax.text(5, 8, "若依框架原生能力：权限管理、用户认证、菜单管理、操作日志、定时任务",
            ha="center", va="center", fontsize=9, color="#27ae60", fontweight="bold")

    plt.tight_layout()
    return fig

# ====================== 主函数：执行绘图 ======================
if __name__ == "__main__":
    # 生成4张核心流程图
    fig1 = draw_agent_collaboration()
    fig2 = draw_agent_vector_relation()
    fig3 = draw_vector_db_build()
    fig4 = draw_ruoyi_integration()

    fig1.savefig("agent_collaboration.png")
    fig2.savefig("agent_vector_relation.png")
    fig3.savefig("vector_db_build0.png")
    fig4.savefig("vector_db_build.png")

    # 显示所有图表
    plt.show()