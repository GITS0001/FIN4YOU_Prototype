import os
from PIL import Image

image_dir = r"data/media/images"
files = sorted(os.listdir(image_dir))
for f in files:
    if f.endswith('.png'):
        p = os.path.join(image_dir, f)
        img = Image.open(p)
        print(f"{f}: size={img.size}, mode={img.mode}")
