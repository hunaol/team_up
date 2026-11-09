import html
import re
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

CONTACT_TYPES = Literal["wechat", "qq", "phone"]
DATE_PATTERN = r"^\d{4}-\d{2}-\d{2}$"

# 招募描述允许的轻量富文本标签：加粗 / 斜体 / 下划线 / 换行 / 本站上传的图片
DESC_MAX_HTML = 2000
DESC_MIN_TEXT = 10
DESC_MAX_TEXT = 500
_TAG_RE = re.compile(r"<[^>]*>")
_TAG_TOKEN_RE = re.compile(r"</?[a-zA-Z][a-zA-Z0-9]*[^>]*>")
_TAG_NAME_RE = re.compile(r"^</?\s*([a-zA-Z][a-zA-Z0-9]*)")
_ATTR_RE = re.compile(
    r"""([a-zA-Z_:][-a-zA-Z0-9_:.]*)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>]+))"""
)
_SIMPLE_TAGS = {"b", "i", "u"}
_UPLOAD_SRC_RE = re.compile(r"^/api/uploads/[A-Za-z0-9][A-Za-z0-9._-]*$")


def _clean_tag(raw: str) -> str:
    """把单个标签重建成白名单形式；不在白名单内的一律丢弃。"""
    inner = raw.strip()
    inner = inner[1:-1] if inner.startswith("<") else inner
    closing = inner.lstrip().startswith("/")
    name_match = _TAG_NAME_RE.match(raw)
    if not name_match:
        return ""
    name = name_match.group(1).lower()
    if name in _SIMPLE_TAGS:
        return f"</{name}>" if closing else f"<{name}>"
    if closing:
        return ""
    if name == "br":
        return "<br>"
    if name == "img":
        for attr in _ATTR_RE.finditer(inner):
            if attr.group(1).lower() != "src":
                continue
            src = (attr.group(2) or attr.group(3) or attr.group(4) or "").strip()
            if _UPLOAD_SRC_RE.match(src):
                return f'<img src="{src}" alt="">'
            return ""
    return ""


def sanitize_description(raw: str) -> str:
    """转义全部文本，仅保留白名单标签，避免 XSS。"""
    text = (raw or "").strip()
    out = []
    pos = 0
    for match in _TAG_TOKEN_RE.finditer(text):
        out.append(html.escape(text[pos : match.start()], quote=False))
        out.append(_clean_tag(match.group(0)))
        pos = match.end()
    out.append(html.escape(text[pos:], quote=False))
    return "".join(out)


def description_text(raw: str) -> str:
    """提取描述中的纯文本，用于长度校验与摘要。"""
    text = html.unescape(_TAG_RE.sub("", raw or ""))
    return text.replace("\xa0", " ").replace("\r", "").strip()


def normalize_description(raw: str) -> str:
    value = sanitize_description(raw)
    size = len(re.sub(r"\s+", "", description_text(value)))
    if size < DESC_MIN_TEXT or size > DESC_MAX_TEXT:
        raise ValueError(f"描述需为 {DESC_MIN_TEXT}–{DESC_MAX_TEXT} 字")
    return value


def check_contact_format(contact_type: str, contact: str) -> str:
    contact = contact.strip()
    if len(contact) < 5:
        raise ValueError("联系方式至少 5 个字符")
    if contact_type == "qq" and not re.fullmatch(r"\d{5,12}", contact):
        raise ValueError("QQ 号需为 5–12 位数字")
    if contact_type == "phone" and not re.fullmatch(r"1[3-9]\d{9}", contact):
        raise ValueError("手机号格式不正确")
    return contact


class RegisterIn(BaseModel):
    student_id: str = Field(min_length=5, max_length=20, pattern=r"^[A-Za-z0-9]+$")
    name: str = Field(min_length=2, max_length=20)


class LoginIn(BaseModel):
    student_id: str = Field(min_length=1, max_length=20)
    name: str = Field(min_length=1, max_length=20)


class PostIn(BaseModel):
    type: Literal["team", "join"]
    title: str = Field(min_length=2, max_length=50)
    description: str = Field(min_length=1, max_length=DESC_MAX_HTML)
    need_num: Optional[int] = Field(default=None, ge=1, le=99)
    contact_type: CONTACT_TYPES = "wechat"
    contact: str = Field(min_length=5, max_length=100)
    deadline: Optional[str] = Field(default=None, pattern=DATE_PATTERN)
    image: Optional[str] = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def check_contact(self):
        self.title = self.title.strip()
        self.description = normalize_description(self.description)
        self.contact = check_contact_format(self.contact_type, self.contact)
        return self


class PostUpdateIn(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=50)
    description: Optional[str] = Field(default=None, min_length=1, max_length=DESC_MAX_HTML)
    need_num: Optional[int] = Field(default=None, ge=1, le=99)
    contact_type: Optional[CONTACT_TYPES] = None
    contact: Optional[str] = Field(default=None, min_length=5, max_length=100)
    deadline: Optional[str] = Field(default=None, pattern=DATE_PATTERN)
    image: Optional[str] = Field(default=None, max_length=200)

    @model_validator(mode="after")
    def check_description(self):
        if self.description is not None:
            self.description = normalize_description(self.description)
        return self


class UserUpdateIn(BaseModel):
    name: str = Field(min_length=2, max_length=20)


class AdminLoginIn(BaseModel):
    username: str = Field(min_length=1, max_length=30)
    password: str = Field(min_length=1, max_length=64)
