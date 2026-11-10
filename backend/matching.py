# -*- coding: utf-8 -*-
"""队友匹配度计算。

思路很简单：一条「找队友」帖子列出了缺什么位置、什么比赛、什么年级专业；
个人资料里有技能、意向比赛、年级、专业。两边重合度越高，匹配度越高。
「找队伍」帖子方向相反——帖子说的是「我会什么」，所以要拿它去对照
当前用户自己挂出的招募帖子（我缺什么）。

输出统一为 {score, reasons, missing}，score 为 0–100 的整数。
"""

from __future__ import annotations

from typing import Optional

W_ROLE = 0.45
W_COMP = 0.25
W_GRADE = 0.15
W_MAJOR = 0.15


def _split(value: Optional[str]) -> list[str]:
    if not value:
        return []
    return [x.strip() for x in str(value).replace("，", ",").split(",") if x.strip()]


def _labels(codes, mapping) -> list[str]:
    return [mapping.get(c, c) for c in codes]


def _major_match(req: str, major: str) -> bool:
    req = (req or "").strip()
    if not req or req in ("不限", "不限专业"):
        return True
    major = (major or "").strip()
    if not major:
        return False
    for kw in _split(req.replace("专业", "")):
        kw = kw.strip().rstrip("类")
        if not kw:
            continue
        if kw in major or major in kw:
            return True
    return False


def _profile_fields(profile) -> dict:
    """兼容 User 对象与 dict。"""
    def get(k, default=""):
        if profile is None:
            return default
        if isinstance(profile, dict):
            return profile.get(k, default) or default
        return getattr(profile, k, default) or default

    return {
        "grade": get("grade"),
        "major": get("major"),
        "skills": _split(get("skills")),
        "interests": _split(get("interests")),
    }


def score_for_candidate(profile, post, role_label=None, grade_label=None) -> Optional[dict]:
    """我作为候选人，看这条「team」帖与我有多合。"""
    pf = _profile_fields(profile)
    roles = _split(post.roles)
    needed = set(roles)
    mine = set(pf["skills"])

    # 资料太空就不给分，避免出现有误导性的百分比
    if not mine and not pf["interests"] and not pf["grade"] and not pf["major"]:
        return None

    reasons: list[str] = []

    if needed:
        hits = needed & mine
        role_score = len(hits) / len(needed)
        if hits:
            reasons.append("位置契合：" + "、".join(_labels(hits, role_label or {})))
    else:
        role_score = 0.5

    if post.competition:
        if post.competition in pf["interests"]:
            comp_score = 1.0
            reasons.append("意向比赛一致：" + post.competition)
        elif not pf["interests"]:
            comp_score = 0.55
        else:
            comp_score = 0.25
    else:
        comp_score = 0.55

    wanted_grades = _split(post.grade_req)
    if not wanted_grades:
        grade_score = 0.9
    elif pf["grade"] and pf["grade"] in wanted_grades:
        grade_score = 1.0
        reasons.append("年级符合：" + "、".join(_labels([pf["grade"]], grade_label or {})))
    elif not pf["grade"]:
        grade_score = 0.5
    else:
        grade_score = 0.1

    if _major_match(post.major_req, pf["major"]):
        major_score = 1.0 if (post.major_req and pf["major"]) else 0.8
        if post.major_req and pf["major"]:
            reasons.append("专业符合：" + pf["major"])
    else:
        major_score = 0.15

    total = (
        role_score * W_ROLE
        + comp_score * W_COMP
        + grade_score * W_GRADE
        + major_score * W_MAJOR
    )
    missing = [role_label.get(r, r) if role_label else r for r in (needed - mine)]
    return {
        "score": max(0, min(100, int(round(total * 100)))),
        "reasons": reasons[:4],
        "missing": missing,
    }


def score_for_my_team(join_post, my_team_post) -> Optional[dict]:
    """我是队长，看这条「找队伍」帖（对方会什么）和我缺的位置合不合。"""
    need = set(_split(my_team_post.roles))
    offer = set(_split(join_post.roles))

    reasons: list[str] = []
    if need:
        hits = need & offer
        role_score = len(hits) / len(need)
        missing = need - offer
        if hits:
            reasons.append("能补足位置：" + "、".join(sorted(hits)))
    else:
        role_score = 0.5
        hits, missing = set(), set()

    if my_team_post.competition and join_post.competition:
        comp_score = 1.0 if my_team_post.competition == join_post.competition else 0.3
        if comp_score == 1.0:
            reasons.append("同一场比赛")
    else:
        comp_score = 0.6

    total = role_score * 0.65 + comp_score * 0.35
    return {"score": max(0, min(100, int(round(total * 100)))), "reasons": reasons[:3], "missing": sorted(missing)}


def same_team_match(join_post, team_post) -> dict:
    """两条帖子之间的直接匹配（用于详情页互推）。"""
    need = set(_split(team_post.roles))
    offer = set(_split(join_post.roles))
    hits = need & offer
    role_score = (len(hits) / len(need)) if need else 0.5
    comp_score = 1.0 if (team_post.competition and team_post.competition == join_post.competition) else 0.35
    total = role_score * 0.7 + comp_score * 0.3
    return {
        "score": max(0, min(100, int(round(total * 100)))),
        "missing": sorted(need - offer),
        "hit": sorted(hits),
    }
