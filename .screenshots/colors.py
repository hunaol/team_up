from PIL import Image
from collections import Counter

src = r"C:\Users\Lenovo\.dsh\attachments\v1\objects\a3\a37ebaa6d57451c1c320f52e6b8fffbc67ea5309121823cc435e13a739875f65"
im = Image.open(src).convert("RGB")


def top(box, n=6):
    c = Counter(im.crop(box).getdata())
    return c.most_common(n)


print("submit btn p2", top((1150, 372, 1290, 392)))
print("active pill", top((70, 80, 130, 96)))
print("sidebar bg", top((60, 200, 120, 260)))
print("page bg", top((300, 240, 400, 270)))
print("btn publish hero", top((215, 165, 290, 185)))
print("primary text blue", top((88, 82, 105, 94)))
print("stat card bg", top((200, 215, 240, 240)))
print("icon blue circle", top((196, 225, 215, 250)))
