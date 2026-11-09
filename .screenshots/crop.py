from PIL import Image
import sys

src = r"C:\Users\Lenovo\.dsh\attachments\v1\objects\a3\a37ebaa6d57451c1c320f52e6b8fffbc67ea5309121823cc435e13a739875f65"
im = Image.open(src).convert("RGB")

regions = {
    "p1_home": (0, 0, 760, 425),
    "p2_publish": (765, 0, 1536, 425),
    "p3_myposts": (10, 435, 760, 795),
    "p4_dashboard": (765, 435, 1536, 795),
    "p5_users": (370, 800, 1165, 1024),
}
for name, box in regions.items():
    crop = im.crop(box)
    w, h = crop.size
    crop = crop.resize((int(w * 2.2), int(h * 2.2)), Image.LANCZOS)
    crop.save(rf"E:\Project\trae_team\.screenshots\{name}.png")
    print(name, crop.size)

# color probes
def px(x, y):
    return im.getpixel((x, y))

print("page bg", px(400, 250))
print("sidebar bg", px(60, 300))
print("active nav bg", px(100, 88))
print("active nav text", px(88, 88))
print("btn dark", px(240, 171))
print("submit btn", px(1215, 380))
print("card border", px(180, 250))
