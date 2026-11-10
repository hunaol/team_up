# -*- coding: utf-8 -*-
"""高水平竞赛名录 + 结构化选项。

统一的比赛名称是检索的基础：同一场比赛在同学口中常有多个叫法
（例如「市调」「正大杯」「市场调查大赛」其实都是同一场），
名录里把标准名和别名放在一起，检索时按别名归一，避免漏帖。
"""

COMPETITIONS = [
    # 创新创业类
    {
        "name": "中国国际大学生创新大赛",
        "aliases": ["互联网+", "互联网＋", "中国国际互联网+大学生创新创业大赛", "互联网+大赛", "互联网加大赛", "国创赛", "创新大赛"],
        "level": "国家级 A 类",
        "category": "创新创业",
    },
    {
        "name": "“挑战杯”全国大学生课外学术科技作品竞赛",
        "aliases": ["挑战杯", "大挑", "课外学术科技作品竞赛", "挑战杯科技作品"],
        "level": "国家级 A 类",
        "category": "创新创业",
    },
    {
        "name": "“挑战杯”中国大学生创业计划竞赛",
        "aliases": [
            "小挑",
            "创青春",
            "创业计划竞赛",
            "挑战杯创业",
            "挑战杯小挑",
            "挑战杯创业计划竞赛",
            "挑战杯创业计划大赛",
        ],
        "level": "国家级 A 类",
        "category": "创新创业",
    },
    {
        "name": "全国大学生电子商务“创新、创意及创业”挑战赛",
        "aliases": ["三创赛", "电子商务三创赛", "电商三创"],
        "level": "国家级 A 类",
        "category": "创新创业",
    },
    {
        "name": "中国大学生服务外包创新创业大赛",
        "aliases": ["服创", "服务外包大赛", "服创赛"],
        "level": "国家级",
        "category": "创新创业",
    },
    {
        "name": "“学创杯”全国大学生创业综合模拟大赛",
        "aliases": ["学创杯", "创业综合模拟"],
        "level": "国家级",
        "category": "创新创业",
    },
    {
        "name": "全国大学生创新创业训练计划",
        "aliases": ["大创", "国创", "创新创业训练计划"],
        "level": "国家级项目",
        "category": "创新创业",
    },
    # 数理统计类
    {
        "name": "全国大学生数学建模竞赛",
        "aliases": [
            "数模国赛",
            "国赛数模",
            "数学建模",
            "数学建模竞赛",
            "全国大学生数学建模",
            "CUMCM",
            "数模",
        ],
        "level": "国家级 A 类",
        "category": "数理统计",
    },
    {
        "name": "美国大学生数学建模竞赛",
        "aliases": ["美赛", "MCM", "ICM", "MCM/ICM", "美国数模"],
        "level": "国际级",
        "category": "数理统计",
    },
    {
        "name": "“华为杯”中国研究生数学建模竞赛",
        "aliases": ["研赛", "研究生数模", "华为杯数模"],
        "level": "国家级",
        "category": "数理统计",
    },
    {
        "name": "全国大学生统计建模大赛",
        "aliases": ["统计建模", "统模", "统计建模大赛"],
        "level": "国家级",
        "category": "数理统计",
    },
    {
        "name": "全国大学生市场调查与分析大赛",
        "aliases": ["市调", "正大杯", "市场调查", "市调大赛", "市场调查与分析大赛", "正大杯市调"],
        "level": "国家级 A 类",
        "category": "数理统计",
    },
    {
        "name": "全国大学生数学竞赛",
        "aliases": ["数学竞赛", "CMC", "高数竞赛"],
        "level": "国家级",
        "category": "数理统计",
    },
    # 计算机类
    {
        "name": "中国大学生计算机设计大赛",
        "aliases": ["计设赛", "计算机设计", "4C", "计设"],
        "level": "国家级 A 类",
        "category": "计算机",
    },
    {
        "name": "中国高校计算机大赛-团体程序设计天梯赛",
        "aliases": ["天梯赛", "团体程序设计", "GPLT"],
        "level": "国家级",
        "category": "计算机",
    },
    {
        "name": "蓝桥杯全国软件和信息技术专业人才大赛",
        "aliases": ["蓝桥杯", "蓝桥", "Lanqiao"],
        "level": "国家级",
        "category": "计算机",
    },
    {
        "name": "ACM-ICPC 国际大学生程序设计竞赛",
        "aliases": ["ACM", "ICPC", "程序设计竞赛", "区域赛"],
        "level": "国际级",
        "category": "计算机",
    },
    {
        "name": "中国大学生程序设计竞赛",
        "aliases": ["CCPC", "程序设计竞赛国赛"],
        "level": "国家级",
        "category": "计算机",
    },
    {
        "name": "全国大学生信息安全竞赛",
        "aliases": ["信安赛", "信息安全竞赛", "CTF"],
        "level": "国家级",
        "category": "计算机",
    },
    {
        "name": "中国高校计算机大赛-人工智能创意赛",
        "aliases": ["AI创意赛", "人工智能创意", "百度飞桨"],
        "level": "国家级",
        "category": "计算机",
    },
    {
        "name": "全国大学生集成电路创新创业大赛",
        "aliases": ["集创赛", "集成电路", "IC大赛"],
        "level": "国家级",
        "category": "计算机",
    },
    # 电子与工程类
    {
        "name": "全国大学生电子设计竞赛",
        "aliases": ["电赛", "电子设计", "TI杯"],
        "level": "国家级 A 类",
        "category": "电子工程",
    },
    {
        "name": "全国大学生智能汽车竞赛",
        "aliases": ["智能车", "智能汽车竞赛", "恩智浦杯"],
        "level": "国家级 A 类",
        "category": "电子工程",
    },
    {
        "name": "全国大学生机器人大赛 RoboMaster",
        "aliases": ["机甲大师", "RoboMaster", "RM", "机器人大赛"],
        "level": "国家级",
        "category": "电子工程",
    },
    {
        "name": "中国机器人大赛暨 RoboCup 机器人世界杯中国赛",
        "aliases": ["中国机器人大赛", "RoboCup", "机器人世界杯"],
        "level": "国家级",
        "category": "电子工程",
    },
    {
        "name": "“西门子杯”中国智能制造挑战赛",
        "aliases": ["西门子杯", "智能制造挑战赛"],
        "level": "国家级",
        "category": "电子工程",
    },
    {
        "name": "全国大学生机械创新设计大赛",
        "aliases": ["机创", "机械创新", "机创赛"],
        "level": "国家级 A 类",
        "category": "机械制造",
    },
    {
        "name": "中国大学生机械工程创新创意大赛",
        "aliases": ["机械工程创新", "机工赛"],
        "level": "国家级",
        "category": "机械制造",
    },
    {
        "name": "全国大学生先进成图技术与产品信息建模创新大赛",
        "aliases": ["成图大赛", "先进成图", "制图大赛"],
        "level": "国家级",
        "category": "机械制造",
    },
    {
        "name": "全国大学生结构设计竞赛",
        "aliases": ["结构赛", "结构设计", "结构设计竞赛"],
        "level": "国家级 A 类",
        "category": "土木建筑",
    },
    {
        "name": "全国大学生节能减排社会实践与科技竞赛",
        "aliases": ["节能减排", "节能减排大赛"],
        "level": "国家级",
        "category": "能源环境",
    },
    {
        "name": "全国大学生化工设计竞赛",
        "aliases": ["化工设计", "化工赛"],
        "level": "国家级",
        "category": "能源环境",
    },
    {
        "name": "全国大学生水利创新设计大赛",
        "aliases": ["水利创新", "水利赛"],
        "level": "国家级",
        "category": "能源环境",
    },
    {
        "name": "全国大学生 GIS 应用技能大赛",
        "aliases": ["GIS大赛", "GIS应用", "地理信息"],
        "level": "国家级",
        "category": "地球科学",
    },
    {
        "name": "全国大学生测绘学科创新创业智能大赛",
        "aliases": ["测绘大赛", "测绘学科"],
        "level": "国家级",
        "category": "地球科学",
    },
    # 经管商科类
    {
        "name": "全国大学生金融精英挑战赛",
        "aliases": ["金融精英", "金融挑战赛"],
        "level": "国家级",
        "category": "经管商科",
    },
    {
        "name": "全国大学生人力资源管理知识技能竞赛",
        "aliases": ["人资赛", "人力资源管理竞赛", "HR大赛"],
        "level": "国家级",
        "category": "经管商科",
    },
    {
        "name": "全国大学生能源经济学术创意大赛",
        "aliases": ["能源经济", "能源经济大赛"],
        "level": "国家级",
        "category": "经管商科",
    },
    {
        "name": "全国大学生物流设计大赛",
        "aliases": ["物流设计", "物流大赛"],
        "level": "国家级",
        "category": "经管商科",
    },
    # 设计传媒类
    {
        "name": "全国大学生广告艺术大赛",
        "aliases": ["大广赛", "广告艺术大赛", "广赛"],
        "level": "国家级 A 类",
        "category": "设计传媒",
    },
    {
        "name": "中国好创意暨全国数字艺术设计大赛",
        "aliases": ["中国好创意", "好创意", "数字艺术设计"],
        "level": "国家级",
        "category": "设计传媒",
    },
    {
        "name": "全国大学生数字媒体科技作品及创意竞赛",
        "aliases": ["数媒赛", "数字媒体竞赛", "数媒科技"],
        "level": "国家级",
        "category": "设计传媒",
    },
    {
        "name": "全国三维数字化创新设计大赛",
        "aliases": ["3D大赛", "三维数字化", "全国3D"],
        "level": "国家级",
        "category": "设计传媒",
    },
    {
        "name": "全国大学生工业设计大赛",
        "aliases": ["工业设计", "工设大赛"],
        "level": "国家级",
        "category": "设计传媒",
    },
    {
        "name": "米兰设计周-中国高校设计学科师生优秀作品展",
        "aliases": ["米兰设计周", "米兰展"],
        "level": "国际级",
        "category": "设计传媒",
    },
    # 外语与人文类
    {
        "name": "“外研社·国才杯”全国英语演讲·写作·阅读大赛",
        "aliases": ["外研社杯", "国才杯", "外研社", "英语演讲大赛"],
        "level": "国家级",
        "category": "外语人文",
    },
    {
        "name": "全国大学生英语竞赛",
        "aliases": ["NECCS", "英语竞赛", "大英赛"],
        "level": "国家级",
        "category": "外语人文",
    },
    {
        "name": "“21 世纪杯”全国英语演讲比赛",
        "aliases": ["21世纪杯", "21世纪英语演讲"],
        "level": "国家级",
        "category": "外语人文",
    },
    # 其他综合
    {
        "name": "全国大学生职业规划大赛",
        "aliases": ["职业规划大赛", "职规赛"],
        "level": "国家级",
        "category": "综合",
    },
    {
        "name": "全国大学生生命科学竞赛",
        "aliases": ["生命科学竞赛", "生科赛"],
        "level": "国家级",
        "category": "生命科学",
    },
    {
        "name": "全国大学生物理实验竞赛",
        "aliases": ["物理实验竞赛", "物实赛"],
        "level": "国家级",
        "category": "数理统计",
    },
    {
        "name": "全国大学生化学实验创新设计大赛",
        "aliases": ["化学实验竞赛", "化实赛"],
        "level": "国家级",
        "category": "生命科学",
    },
    # —— 以下补充自「小犁竞赛时间表」名录，补齐工科 / 设计类常打比赛 ——
    {
        "name": "全国周培源大学生力学竞赛",
        "aliases": ["周培源力学竞赛", "力学竞赛", "周培源"],
        "level": "国家级",
        "category": "数理统计",
    },
    {
        "name": "中国软件杯大学生软件设计大赛",
        "aliases": ["中国软件杯", "软件杯"],
        "level": "国家级",
        "category": "计算机",
    },
    {
        "name": "全国大学生金相技能大赛",
        "aliases": ["金相技能大赛", "金相大赛", "金相"],
        "level": "国家级",
        "category": "机械制造",
    },
    {
        "name": "中美青年创客大赛",
        "aliases": ["中美创客", "青年创客大赛", "中美青年创客"],
        "level": "国家级",
        "category": "创新创业",
    },
    {
        "name": "全国大学生光电设计竞赛",
        "aliases": ["光电设计竞赛", "光电赛", "光电设计"],
        "level": "国家级",
        "category": "电子工程",
    },
    {
        "name": "中国大学生工程实践与创新能力大赛",
        "aliases": ["工程训练综合能力竞赛", "工训赛", "工程训练竞赛", "工程实践与创新能力大赛"],
        "level": "国家级",
        "category": "机械制造",
    },
    {
        "name": "全国大学生地质技能竞赛",
        "aliases": ["地质技能竞赛", "地质赛"],
        "level": "国家级",
        "category": "地球科学",
    },
    {
        "name": "华灿奖",
        "aliases": ["华灿", "华灿设计奖"],
        "level": "国家级",
        "category": "设计传媒",
    },
    {
        "name": "未来设计师·全国高校数字艺术设计大赛",
        "aliases": ["未来设计师", "NCDA", "数字艺术设计大赛", "高校数字艺术设计大赛"],
        "level": "国家级",
        "category": "设计传媒",
    },
    {
        "name": "中国高校计算机大赛",
        "aliases": ["高校计算机大赛", "4C大赛", "中国高校计算机"],
        "level": "国家级",
        "category": "计算机",
    },
    # —— 以下补充自《全国84项大学生竞赛》名录 ——
    {
        "name": "百度之星·程序设计大赛",
        "aliases": ["百度之星", "百度之星程序设计大赛"],
        "level": "企业级",
        "category": "计算机",
    },
    {
        "name": "码蹄杯全国职业院校程序设计大赛",
        "aliases": ["码蹄杯", "码蹄杯程序设计大赛"],
        "level": "国家级",
        "category": "计算机",
    },
    {
        "name": "全球校园人工智能算法精英大赛",
        "aliases": ["人工智能算法精英大赛", "AI算法精英大赛", "算法精英大赛"],
        "level": "国家级",
        "category": "计算机",
    },
    {
        "name": "华为ICT大赛",
        "aliases": ["华为ICT", "ICT大赛"],
        "level": "企业级",
        "category": "计算机",
    },
    {
        "name": "全国大学生计算机系统能力大赛",
        "aliases": ["计算机系统能力大赛", "系统能力大赛", "OS大赛"],
        "level": "国家级",
        "category": "计算机",
    },
    {
        "name": "全国大学生信息安全与对抗技术竞赛",
        "aliases": ["信息安全与对抗技术竞赛", "信息安全对抗赛", "ISCC"],
        "level": "国家级",
        "category": "计算机",
    },
    {
        "name": "全国大学生物联网设计竞赛",
        "aliases": ["物联网设计竞赛", "物联网大赛"],
        "level": "国家级",
        "category": "电子工程",
    },
    {
        "name": "“大唐杯”全国大学生新一代信息通信技术大赛",
        "aliases": ["大唐杯", "大唐杯通信大赛", "信息通信技术大赛"],
        "level": "国家级",
        "category": "电子工程",
    },
    {
        "name": "全国大学生嵌入式芯片与系统设计竞赛",
        "aliases": ["嵌入式芯片与系统设计竞赛", "嵌入式竞赛", "嵌入式大赛"],
        "level": "国家级",
        "category": "电子工程",
    },
    {
        "name": "睿抗机器人开发者大赛",
        "aliases": ["睿抗", "RAICOM", "睿抗机器人"],
        "level": "国家级",
        "category": "机械制造",
    },
    {
        "name": "中国高校智能机器人创意大赛",
        "aliases": ["智能机器人创意大赛", "机器人创意大赛"],
        "level": "国家级",
        "category": "机械制造",
    },
    {
        "name": "中国机器人及人工智能大赛",
        "aliases": ["机器人及人工智能大赛", "机器人人工智能大赛"],
        "level": "国家级",
        "category": "机械制造",
    },
    {
        "name": "全国大学生花园设计建造竞赛",
        "aliases": ["花园设计建造竞赛", "花园设计竞赛", "花园建造竞赛"],
        "level": "国家级",
        "category": "土木建筑",
    },
    {
        "name": "全国数字建筑创新应用大赛",
        "aliases": ["数字建筑创新应用大赛", "数字建筑大赛"],
        "level": "国家级",
        "category": "土木建筑",
    },
    {
        "name": "iCAN大学生创新创业大赛",
        "aliases": ["iCAN", "iCAN大赛", "ican创新创业大赛"],
        "level": "国家级",
        "category": "创新创业",
    },
    {
        "name": "全国高校商业精英挑战赛",
        "aliases": [
            "商业精英挑战赛",
            "品牌策划竞赛",
            "会展专业创新创业实践竞赛",
            "国际贸易竞赛",
            "会计与商业管理案例竞赛",
        ],
        "level": "国家级",
        "category": "经管商科",
    },
    {
        "name": "全国本科院校税收风险管控案例大赛",
        "aliases": ["税收风险管控案例大赛", "税收风险管控大赛", "税务案例大赛"],
        "level": "国家级",
        "category": "经管商科",
    },
    {
        "name": "全国企业竞争模拟大赛",
        "aliases": ["企业竞争模拟大赛", "企模大赛", "企业竞争模拟"],
        "level": "国家级",
        "category": "经管商科",
    },
    {
        "name": "全国高等院校数智化企业经营沙盘大赛",
        "aliases": ["数智化企业经营沙盘大赛", "沙盘大赛", "ERP沙盘大赛"],
        "level": "国家级",
        "category": "经管商科",
    },
    {
        "name": "“科云杯”全国大学生财会职业能力大赛",
        "aliases": ["科云杯", "财会职业能力大赛"],
        "level": "国家级",
        "category": "经管商科",
    },
    {
        "name": "全国大学生化工实验大赛",
        "aliases": ["化工实验大赛", "化工实验竞赛"],
        "level": "国家级",
        "category": "能源环境",
    },
    {
        "name": "中国大学生医学技术技能大赛",
        "aliases": ["医学技术技能大赛", "医学技能大赛"],
        "level": "国家级",
        "category": "生命科学",
    },
    {
        "name": "全国大学生基础医学创新研究暨实验设计论坛",
        "aliases": ["基础医学创新研究暨实验设计论坛", "基础医学创新论坛", "基础医学大赛"],
        "level": "国家级",
        "category": "生命科学",
    },
    {
        "name": "全国职业院校技能大赛",
        "aliases": ["职业院校技能大赛", "国赛技能大赛"],
        "level": "国家级",
        "category": "综合",
    },
    {
        "name": "世界技能大赛",
        "aliases": ["世赛", "WorldSkills"],
        "level": "国际级",
        "category": "综合",
    },
    {
        "name": "世界技能大赛中国选拔赛",
        "aliases": ["世赛中国选拔赛", "世赛选拔赛"],
        "level": "国家级",
        "category": "综合",
    },
    {
        "name": "中华经典诵写讲大赛",
        "aliases": ["诵写讲大赛", "经典诵写讲"],
        "level": "国家级",
        "category": "外语人文",
    },
    {
        "name": "“外教社杯”全国高校学生跨文化能力大赛",
        "aliases": ["外教社杯", "跨文化能力大赛"],
        "level": "国家级",
        "category": "外语人文",
    },
]

# 技能 / 角色标签：找队友时勾选「缺什么位置」，找队伍时勾选「我能做什么」
ROLE_OPTIONS = [
    {"code": "frontend", "label": "前端开发"},
    {"code": "backend", "label": "后端开发"},
    {"code": "algorithm", "label": "算法 / 建模"},
    {"code": "data", "label": "数据分析"},
    {"code": "product", "label": "产品 / 策划"},
    {"code": "design", "label": "UI / 视觉设计"},
    {"code": "ppt", "label": "PPT / 答辩"},
    {"code": "writing", "label": "文案 / 撰写"},
    {"code": "video", "label": "视频剪辑"},
    {"code": "research", "label": "市场调研"},
    {"code": "finance", "label": "财务 / 商业分析"},
    {"code": "hardware", "label": "硬件 / 嵌入式"},
    {"code": "art", "label": "美工 / 插画"},
    {"code": "pm", "label": "项目管理 / 队长"},
    {"code": "ops", "label": "运营 / 新媒体"},
    {"code": "english", "label": "英语 / 演讲"},
]

GRADE_OPTIONS = [
    {"code": "freshman", "label": "大一"},
    {"code": "sophomore", "label": "大二"},
    {"code": "junior", "label": "大三"},
    {"code": "senior", "label": "大四"},
    {"code": "graduate", "label": "研究生"},
]

# 比赛阶段
STAGE_OPTIONS = [
    {"code": "forming", "label": "刚组队"},
    {"code": "school", "label": "校赛冲刺"},
    {"code": "province", "label": "省赛备战"},
    {"code": "national", "label": "国赛备战"},
]

MAJOR_SUGGESTIONS = [
    "经管类",
    "计算机类",
    "数学类",
    "统计类",
    "设计类",
    "电子信息类",
    "机械类",
    "土木建筑类",
    "文科类",
    "外语类",
    "法学类",
    "医学类",
    "不限专业",
]

ROLE_LABEL = {r["code"]: r["label"] for r in ROLE_OPTIONS}
GRADE_LABEL = {g["code"]: g["label"] for g in GRADE_OPTIONS}
STAGE_LABEL = {s["code"]: s["label"] for s in STAGE_OPTIONS}


def _norm(text: str) -> str:
    """归一化：去空格 / 标点 / 全角符号，英文转小写。"""
    t = (text or "").strip().lower()
    for a, b in [
        ("（", "("),
        ("）", ")"),
        ("＋", "+"),
        ("·", ""),
        ("・", ""),
        ("—", ""),
        ("–", ""),
        ("-", ""),
        ("_", ""),
        (" ", ""),
        ("\u3000", ""),
        ("“", ""),
        ("”", ""),
        ('"', ""),
        ("'", ""),
        ("、", ""),
    ]:
        t = t.replace(a, b)
    return t


# 所有可检索的名字（标准名 + 别名）→ 标准名
_INDEX = {}
for _c in COMPETITIONS:
    _INDEX[_norm(_c["name"])] = _c["name"]
    for _a in _c["aliases"]:
        _INDEX[_norm(_a)] = _c["name"]


def canonical_name(text: str) -> str:
    """把一个叫法换成标准名；认不出来就原样返回（保留自由填写的比赛）。"""
    raw = (text or "").strip()
    if not raw:
        return ""
    key = _norm(raw)
    if key in _INDEX:
        return _INDEX[key]
    # 包含式匹配：如「正大杯市调大赛」→ 全国大学生市场调查与分析大赛
    best = None
    for k, name in _INDEX.items():
        if len(k) >= 2 and (k in key or key in k):
            if best is None or len(k) > len(best[0]):
                best = (k, name)
    return best[1] if best else raw


def resolve_list(text: str) -> list[str]:
    """把逗号/空格分隔的一串叫法逐个归一。"""
    import re

    parts = [p for p in re.split(r"[,，;；/\s]+", text or "") if p.strip()]
    out = []
    for p in parts:
        name = canonical_name(p)
        if name and name not in out:
            out.append(name)
    return out


def match_competition(query: str) -> list[dict]:
    """按关键词检索名录：标准名或任一别名包含关键词即命中。"""
    q = _norm(query)
    if not q:
        return [{"name": c["name"], "level": c["level"], "category": c["category"], "aliases": c["aliases"]} for c in COMPETITIONS]
    hit = []
    for c in COMPETITIONS:
        names = [_norm(c["name"])] + [_norm(a) for a in c["aliases"]]
        if any(q in n for n in names):
            hit.append(
                {
                    "name": c["name"],
                    "level": c["level"],
                    "category": c["category"],
                    "aliases": c["aliases"],
                }
            )
    return hit


def catalog() -> list[dict]:
    return [
        {"name": c["name"], "aliases": c["aliases"], "level": c["level"], "category": c["category"]}
        for c in COMPETITIONS
    ]


def meta() -> dict:
    return {
        "competitions": catalog(),
        "roles": ROLE_OPTIONS,
        "grades": GRADE_OPTIONS,
        "stages": STAGE_OPTIONS,
        "majors": MAJOR_SUGGESTIONS,
    }
