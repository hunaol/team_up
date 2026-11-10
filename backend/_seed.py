"""开发/演示数据种子脚本（幂等，可重复执行）。

用法：python _seed.py
说明：清空 posts / favorites / applications / messages，并补齐演示用户、
带结构化字段（比赛 / 位置 / 年级 / 阶段）的招募帖、申请与私信，
方便本地预览与截图。
"""

from datetime import datetime, timedelta

from database import SessionLocal
from models import Application, Favorite, Message, Post, User

NOW = datetime.utcnow()

USERS = [
    {
        "student_id": "2024413435",
        "name": "韩涛",
        "grade": "sophomore",
        "major": "统计学",
        "skills": "data,ppt,research",
        "interests": "全国大学生市场调查与分析大赛,全国大学生统计建模大赛",
        "bio": "擅长问卷设计、SPSS/Python 数据分析，带过两年市调校赛。",
        "resume": "2025 正大杯市调省一等奖（数据分析）\n2024 统计建模校赛二等奖\n技能：SPSS、Python(pandas)、Tableau",
        "contact_type": "wechat",
        "contact": "han_tao_stat",
    },
    {
        "student_id": "2024411108",
        "name": "李思远",
        "grade": "junior",
        "major": "计算机科学与技术",
        "skills": "frontend,backend",
        "interests": "中国国际大学生创新大赛,蓝桥杯全国软件和信息技术专业人才大赛",
        "bio": "做过两个 Vue 项目，负责过社团官网改版，前后端都能顶。",
        "resume": "校园二手交易平台（Vue3 + FastAPI，日活 300+）\n蓝桥杯 C++ 省二\n技能：Vue/React、Python、MySQL",
        "contact_type": "wechat",
        "contact": "lisiyuan_dev",
    },
    {
        "student_id": "2024412276",
        "name": "王雨桐",
        "grade": "sophomore",
        "major": "电子信息工程",
        "skills": "hardware,algorithm",
        "interests": "全国大学生电子设计竞赛,全国大学生智能汽车竞赛",
        "bio": "会画 PCB、调 STM32，实验室常驻选手。",
        "resume": "2024 电赛省二（电源组）\n智能车校赛一等奖（硬件）\n技能：Altium Designer、STM32、C",
        "contact_type": "qq",
        "contact": "2288116633",
    },
    {
        "student_id": "2024410934",
        "name": "陈可欣",
        "grade": "freshman",
        "major": "工商管理",
        "skills": "writing,product,ppt",
        "interests": "“挑战杯”中国大学生创业计划竞赛,全国大学生电子商务“创新、创意及创业”挑战赛",
        "bio": "文笔好，能做商业计划书和答辩 PPT，想把大创项目跑通。",
        "resume": "高中创业社负责人\n擅长商业计划书撰写、路演 PPT 制作",
        "contact_type": "wechat",
        "contact": "chenkexin_bp",
    },
    {
        "student_id": "2024415521",
        "name": "赵一鸣",
        "grade": "senior",
        "major": "视觉传达设计",
        "skills": "design,art,video",
        "interests": "全国大学生广告艺术大赛,米兰设计周-中国高校设计学科师生优秀作品展",
        "bio": "平面 + 动效都能做，作品集有 3 个获奖项目。",
        "resume": "大广赛国家三等奖\n米兰设计周省二\n技能：Figma、AE、Blender",
        "contact_type": "wechat",
        "contact": "zhao_design",
    },
    {
        "student_id": "2024416612",
        "name": "周若曦",
        "grade": "junior",
        "major": "数学与应用数学",
        "skills": "algorithm,data",
        "interests": "全国大学生数学建模竞赛,美国大学生数学建模竞赛",
        "bio": "数学建模老选手，负责建模与论文，LaTeX 排版熟练。",
        "resume": "2024 数模国赛省一\n2025 美赛 M 奖\n技能：MATLAB、LaTeX、Python",
        "contact_type": "phone",
        "contact": "13823361088",
    },
]

POSTS = [
    {
        "author": "2024413435",
        "type": "team",
        "title": "正大杯市调 招募数据分析与答辩",
        "competition": "全国大学生市场调查与分析大赛",
        "roles": "data,ppt,research",
        "grade_req": "sophomore,junior",
        "major_req": "经管类",
        "stage": "school",
        "description": (
            "<b>选题：</b>高校周边咖啡消费行为调研，已完成 300 份问卷回收。<br>"
            "现在缺一位能跑<b>交叉分析</b>、做可视化图表的同学，以及一位负责"
            "<b>答辩 PPT</b> 的同学。<br>"
            "节奏：每周一次线上同步，校赛 11 月中旬提交。"
        ),
        "need_num": 2,
        "contact_type": "wechat",
        "contact": "han_tao_stat",
        "deadline": (NOW + timedelta(days=12)).strftime("%Y-%m-%d"),
        "status": "open",
        "views": 186,
        "days_ago": 1,
    },
    {
        "author": "2024411108",
        "type": "join",
        "title": "计算机大三 前后端都能做 求带互联网+",
        "competition": "中国国际大学生创新大赛",
        "roles": "frontend,backend",
        "grade_req": "junior,senior",
        "major_req": "计算机类",
        "stage": "forming",
        "description": (
            "做过两个 Vue 项目，负责过学校社团官网改版，熟悉组件化开发与接口联调。<br>"
            "希望加入一支有明确赛道的队伍，前端 / 后端都可以，"
            "能保证每周 10 小时以上投入。"
        ),
        "need_num": None,
        "contact_type": "wechat",
        "contact": "lisiyuan_dev",
        "deadline": (NOW + timedelta(days=20)).strftime("%Y-%m-%d"),
        "status": "open",
        "views": 92,
        "days_ago": 2,
    },
    {
        "author": "2024412276",
        "type": "team",
        "title": "电子设计竞赛 硬件方向找搭档",
        "competition": "全国大学生电子设计竞赛",
        "roles": "hardware,algorithm",
        "grade_req": "sophomore,junior",
        "major_req": "电子信息类",
        "stage": "province",
        "description": (
            "选题方向为<b>嵌入式系统</b>，已有电源与结构方案，缺一位熟悉 STM32 的同学。<br>"
            "实验室在工科楼 B302，器材齐全，可随时调试。<br>"
            "要求：会画 PCB、能读数据手册，愿意在赛前熬夜调板。"
        ),
        "need_num": 1,
        "contact_type": "qq",
        "contact": "2288116633",
        "deadline": (NOW + timedelta(days=6)).strftime("%Y-%m-%d"),
        "status": "open",
        "views": 213,
        "days_ago": 3,
    },
    {
        "author": "2024415521",
        "type": "team",
        "title": "大广赛平面组 缺文案与策划",
        "competition": "全国大学生广告艺术大赛",
        "roles": "writing,product",
        "grade_req": "",
        "major_req": "",
        "stage": "national",
        "description": (
            "视觉部分我来，已经有两套 KV 初稿。<br>"
            "缺一位<b>文案</b>同学打磨 slogan 与品牌故事，再找一位懂<b>策划</b>的同学"
            "把洞察写扎实。国赛 12 月截稿，现在开始正合适。"
        ),
        "need_num": 2,
        "contact_type": "wechat",
        "contact": "zhao_design",
        "deadline": (NOW + timedelta(days=28)).strftime("%Y-%m-%d"),
        "status": "open",
        "views": 64,
        "days_ago": 4,
    },
    {
        "author": "2024416612",
        "type": "join",
        "title": "数模国赛老选手 找队 可负责建模与论文",
        "competition": "全国大学生数学建模竞赛",
        "roles": "algorithm,writing",
        "grade_req": "junior,senior",
        "major_req": "数学类",
        "stage": "school",
        "description": (
            "去年国赛省一，今年想冲国奖。<br>"
            "我负责<b>建模与论文撰写</b>，希望找一位编程实现强的同学和一位"
            "能一起熬夜打磨摘要的同学。"
        ),
        "need_num": None,
        "contact_type": "phone",
        "contact": "13823361088",
        "deadline": (NOW + timedelta(days=9)).strftime("%Y-%m-%d"),
        "status": "open",
        "views": 141,
        "days_ago": 5,
    },
    {
        "author": "2024410934",
        "type": "team",
        "title": "三创赛 校园二手循环 招募技术与运营",
        "competition": "全国大学生电子商务“创新、创意及创业”挑战赛",
        "roles": "frontend,ops,product",
        "grade_req": "freshman,sophomore",
        "major_req": "",
        "stage": "forming",
        "description": (
            "项目叫「旧物新生」，做校园闲置物品循环。商业计划书框架已搭好。<br>"
            "缺一位能把小程序 demo 跑起来的同学，和一位愿意跑社团做地推的运营。<br>"
            "校赛 12 月初，团队氛围轻松但想拿奖。"
        ),
        "need_num": 2,
        "contact_type": "wechat",
        "contact": "chenkexin_bp",
        "deadline": (NOW + timedelta(days=16)).strftime("%Y-%m-%d"),
        "status": "open",
        "views": 77,
        "days_ago": 6,
    },
    {
        "author": "2024413435",
        "type": "team",
        "title": "统计建模大赛 已两人 缺编程实现",
        "competition": "全国大学生统计建模大赛",
        "roles": "data,algorithm",
        "grade_req": "sophomore,junior,senior",
        "major_req": "统计类",
        "stage": "national",
        "description": (
            "题目方向是<b>城市夜经济活力测度</b>，数据已拿到。<br>"
            "我负责指标体系，队友负责文献综述，缺一位把模型跑通、"
            "能出图的同学。R / Python 都行。"
        ),
        "need_num": 1,
        "contact_type": "wechat",
        "contact": "han_tao_stat",
        "deadline": (NOW + timedelta(days=21)).strftime("%Y-%m-%d"),
        "status": "full",
        "views": 58,
        "days_ago": 8,
    },
    {
        "author": "2024411108",
        "type": "team",
        "title": "蓝桥杯 C++ 组 组队刷题打卡",
        "competition": "蓝桥杯全国软件和信息技术专业人才大赛",
        "roles": "algorithm",
        "grade_req": "freshman,sophomore",
        "major_req": "计算机类",
        "stage": "school",
        "description": (
            "计划参加明年春季的蓝桥杯 C++ 组，想找两位同学一起刷题打卡。<br>"
            "每周日晚上做一场模拟赛，赛后一起补题、整理题解。"
        ),
        "need_num": 2,
        "contact_type": "wechat",
        "contact": "lisiyuan_dev",
        "deadline": (NOW + timedelta(days=30)).strftime("%Y-%m-%d"),
        "status": "down",
        "views": 41,
        "days_ago": 10,
    },
]

# (申请人, 帖子关键词, 自荐语, 状态)
APPLICATIONS = [
    ("2024410934", "正大杯市调", "我是工商管理大一，做过班级问卷调研，PPT 和文案都可以，想跟着学长学数据分析。", "pending"),
    ("2024416612", "正大杯市调", "统计专业大三，SPSS 和 Python 都熟，可以帮跑交叉分析和显著性检验。", "accepted"),
]

MESSAGES = [
    ("2024416612", "2024413435", "学长好，看到你在招市调的数据分析，我这边时间比较充裕。", 3),
    ("2024413435", "2024416612", "太好了，方便的话周三晚上一起过一下问卷结构？", 2),
]


def main() -> None:
    db = SessionLocal()
    try:
        by_sid = {}
        for item in USERS:
            user = db.query(User).filter(User.student_id == item["student_id"]).first()
            if not user:
                user = User(
                    student_id=item["student_id"],
                    name=item["name"],
                    active=True,
                    created_at=NOW - timedelta(days=40),
                )
                db.add(user)
                db.flush()
            user.grade = item["grade"]
            user.major = item["major"]
            user.skills = item["skills"]
            user.interests = item["interests"]
            user.bio = item["bio"]
            user.resume = item["resume"]
            user.contact_type = item["contact_type"]
            user.contact = item["contact"]
            user.open_to_match = True
            by_sid[item["student_id"]] = user
        db.flush()

        db.query(Application).delete()
        db.query(Message).delete()
        db.query(Favorite).delete()
        db.query(Post).delete()
        db.flush()

        created = {}
        for item in POSTS:
            author = by_sid[item["author"]]
            post = Post(
                user_id=author.id,
                type=item["type"],
                title=item["title"],
                description=item["description"],
                need_num=item["need_num"],
                contact_type=item["contact_type"],
                contact=item["contact"],
                deadline=item["deadline"],
                status=item["status"],
                views=item["views"],
                competition=item["competition"],
                roles=item["roles"],
                grade_req=item["grade_req"],
                major_req=item["major_req"],
                stage=item["stage"],
                created_at=NOW - timedelta(days=item["days_ago"]),
            )
            db.add(post)
            db.flush()
            created[item["title"]] = post

        for sid, keyword, message, status in APPLICATIONS:
            post = next((p for t, p in created.items() if keyword in t), None)
            if not post:
                continue
            db.add(
                Application(
                    post_id=post.id,
                    user_id=by_sid[sid].id,
                    message=message,
                    resume=by_sid[sid].resume,
                    match_score=82,
                    status=status,
                    created_at=NOW - timedelta(hours=6),
                )
            )

        for from_sid, to_sid, body, hours in MESSAGES:
            db.add(
                Message(
                    from_id=by_sid[from_sid].id,
                    to_id=by_sid[to_sid].id,
                    body=body,
                    is_read=hours > 2,
                    created_at=NOW - timedelta(hours=hours),
                )
            )

        for sid, keyword in [("2024413435", "电子设计"), ("2024413435", "三创赛")]:
            post = next((p for t, p in created.items() if keyword in t), None)
            if post:
                db.add(Favorite(user_id=by_sid[sid].id, post_id=post.id, created_at=NOW))

        db.commit()
        print("seeded users:", len(USERS), "posts:", len(POSTS))
    finally:
        db.close()


if __name__ == "__main__":
    main()
