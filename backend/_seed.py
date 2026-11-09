"""开发/演示数据种子脚本（幂等，可重复执行）。

用法：python _seed.py
说明：清空 posts / favorites，并补齐演示用户与招募帖，方便本地预览与截图。
"""

from datetime import datetime, timedelta

from database import SessionLocal
from models import Favorite, Post, User

NOW = datetime.utcnow()

USERS = [
    ("2024413435", "韩涛"),
    ("2024411108", "李思远"),
    ("2024412276", "王雨桐"),
    ("2024410934", "陈可欣"),
]

POSTS = [
    {
        "author": "2024413435",
        "type": "team",
        "title": "全国大学生数学建模竞赛 队伍招募",
        "description": (
            "<b>目标：</b>冲击省一等奖，已有两人，缺一名擅长<b>编程实现</b>或"
            "<b>论文写作</b>的同学。<br>"
            "训练安排：每周三、周六晚线上讨论，暑假集中培训两周。<br>"
            "希望你：熟悉 Python / MATLAB 任一，能坚持完整赛程。"
        ),
        "need_num": 2,
        "contact_type": "wechat",
        "contact": "han_tao_mcm",
        "deadline": (NOW + timedelta(days=18)).strftime("%Y-%m-%d"),
        "status": "open",
        "views": 128,
        "days_ago": 1,
    },
    {
        "author": "2024411108",
        "type": "join",
        "title": "大二前端，想加入互联网+创业团队",
        "description": (
            "做过两个 Vue 项目，负责过学校社团官网的改版，熟悉组件化开发与接口联调。<br>"
            "希望加入一支有明确赛道的队伍，前端 / 产品岗位都可以，"
            "能保证每周 10 小时以上投入。"
        ),
        "need_num": None,
        "contact_type": "wechat",
        "contact": "lisiyuan_dev",
        "deadline": (NOW + timedelta(days=12)).strftime("%Y-%m-%d"),
        "status": "open",
        "views": 86,
        "days_ago": 2,
    },
    {
        "author": "2024412276",
        "type": "team",
        "title": "电子设计竞赛 硬件方向组队",
        "description": (
            "选题方向为<b>嵌入式系统</b>，已有电源与结构方案，缺一名熟悉 STM32 的同学。<br>"
            "实验室在工科楼 B302，器材齐全，可随时调试。<br>"
            "要求：会画 PCB、能读数据手册，愿意在赛前熬夜调板。"
        ),
        "need_num": 2,
        "contact_type": "qq",
        "contact": "2288116633",
        "deadline": (NOW + timedelta(days=6)).strftime("%Y-%m-%d"),
        "status": "full",
        "views": 213,
        "days_ago": 4,
    },
    {
        "author": "2024410934",
        "type": "team",
        "title": "蓝桥杯程序设计大赛 组队练习",
        "description": (
            "计划参加明年春季的蓝桥杯 C++ 组，想找两位同学一起刷题打卡。<br>"
            "每周日晚上做一场模拟赛，赛后一起补题、整理题解。"
        ),
        "need_num": 3,
        "contact_type": "wechat",
        "contact": "chenkexin_acm",
        "deadline": (NOW + timedelta(days=25)).strftime("%Y-%m-%d"),
        "status": "down",
        "views": 41,
        "days_ago": 6,
    },
    {
        "author": "2024411108",
        "type": "join",
        "title": "数学建模美赛 MCM/ICM 找队伍",
        "description": (
            "去年参加过校赛，负责建模与论文排版，熟悉 LaTeX。<br>"
            "希望加入一支有英文写作能力的队伍，一起准备美赛。"
        ),
        "need_num": None,
        "contact_type": "phone",
        "contact": "13823361088",
        "deadline": (NOW + timedelta(days=3)).strftime("%Y-%m-%d"),
        "status": "open",
        "views": 64,
        "days_ago": 35,
    },
    {
        "author": "2024412276",
        "type": "team",
        "title": "挑战杯课外学术作品竞赛 招募搭档",
        "description": (
            "课题方向为<b>校园共享空间运营优化</b>，已完成问卷与初步数据清洗。<br>"
            "缺一名擅长统计分析与可视化的同学，一起完成调研报告与答辩 PPT。"
        ),
        "need_num": 1,
        "contact_type": "wechat",
        "contact": "wangyutong_tzb",
        "deadline": None,
        "status": "open",
        "views": 19,
        "days_ago": 9,
    },
]

FAVORITES = [("2024413435", "互联网+创业团队"), ("2024413435", "电子设计竞赛")]


def main() -> None:
    db = SessionLocal()
    try:
        by_sid = {}
        for student_id, name in USERS:
            user = db.query(User).filter(User.student_id == student_id).first()
            if not user:
                user = User(student_id=student_id, name=name, active=True, created_at=NOW)
                db.add(user)
                db.flush()
            by_sid[student_id] = user

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
                created_at=NOW - timedelta(days=item["days_ago"]),
            )
            db.add(post)
            db.flush()
            created[item["title"]] = post

        for sid, keyword in FAVORITES:
            post = next((p for t, p in created.items() if keyword in t), None)
            if post:
                db.add(Favorite(user_id=by_sid[sid].id, post_id=post.id, created_at=NOW))

        db.commit()
        print("seeded users:", len(USERS), "posts:", len(POSTS))
    finally:
        db.close()


if __name__ == "__main__":
    main()
