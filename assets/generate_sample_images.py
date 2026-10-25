"""
Generates realistic standalone sample test images for PPE and Concrete Crack diagnostics.
Runs once to populate assets/ directory for offline/demo zero-dependency evaluation.
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_sample_ppe_image(filepath: str):
    """Draws a synthetic high-resolution construction site scene."""
    width, height = 800, 600
    img = Image.new("RGB", (width, height), color=(40, 48, 62))
    draw = ImageDraw.Draw(img)

    # Sky gradient / background
    for y in range(250):
        r = int(100 + (y / 250) * 40)
        g = int(140 + (y / 250) * 40)
        b = int(190 + (y / 250) * 40)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # High rise tower framing in background
    for x in range(80, 720, 100):
        draw.rectangle([x, 60, x + 70, 450], outline=(80, 90, 105), width=3)
        for floor_y in range(90, 450, 40):
            draw.line([(x, floor_y), (x + 70, floor_y)], fill=(90, 100, 115), width=2)
            draw.line([(x, floor_y), (x + 70, floor_y + 40)], fill=(70, 80, 95), width=1)

    # Tower Crane
    crane_x = 550
    draw.rectangle([crane_x, 30, crane_x + 16, 420], fill=(234, 179, 8), outline=(180, 130, 0))
    draw.line([(crane_x - 180, 50), (crane_x + 140, 50)], fill=(234, 179, 8), width=5)
    draw.line([(crane_x - 180, 50), (crane_x, 25)], fill=(200, 150, 0), width=2)
    draw.line([(crane_x, 25), (crane_x + 80, 50)], fill=(200, 150, 0), width=2)

    # Ground level concrete slab
    draw.rectangle([0, 420, width, height], fill=(130, 135, 142))
    for i in range(0, width, 50):
        draw.line([(i, 420), (i + 40, height)], fill=(110, 115, 122), width=1)

    # Impalement Rebar Hazard (Starter bars protruding)
    rebar_x_start = 120
    for r_idx in range(6):
        rx = rebar_x_start + (r_idx * 22)
        draw.line([(rx, 420), (rx, 350)], fill=(140, 80, 45), width=4)
        # Warning label
        if r_idx == 2:
            draw.text((rx - 30, 330), "! UNCAPPED REBAR !", fill=(239, 68, 68))

    # Worker 1: Fully Compliant (Hard hat, High-vis vest, Boots, Gloves)
    w1_x = 340
    w1_y = 360
    # Head & Yellow Hard Hat
    draw.ellipse([w1_x + 8, w1_y, w1_x + 28, w1_y + 20], fill=(220, 175, 140))
    draw.arc([w1_x + 4, w1_y - 4, w1_x + 32, w1_y + 12], start=180, end=360, fill=(250, 204, 21), width=6)
    draw.line([(w1_x + 3, w1_y + 8), (w1_x + 33, w1_y + 8)], fill=(234, 179, 8), width=4)
    # Body with High-Vis Orange Vest & Silver reflective stripes
    draw.rectangle([w1_x + 4, w1_y + 20, w1_x + 32, w1_y + 65], fill=(249, 115, 22))
    draw.line([(w1_x + 4, w1_y + 35), (w1_x + 32, w1_y + 35)], fill=(241, 245, 249), width=4)
    draw.line([(w1_x + 4, w1_y + 50), (w1_x + 32, w1_y + 50)], fill=(241, 245, 249), width=4)
    # Legs & Steel Toe Boots
    draw.rectangle([w1_x + 6, w1_y + 65, w1_x + 16, w1_y + 105], fill=(30, 41, 59))
    draw.rectangle([w1_x + 20, w1_y + 65, w1_x + 30, w1_y + 105], fill=(30, 41, 59))
    draw.rectangle([w1_x + 4, w1_y + 102, w1_x + 18, w1_y + 112], fill=(120, 53, 15))
    draw.rectangle([w1_x + 18, w1_y + 102, w1_x + 32, w1_y + 112], fill=(120, 53, 15))

    # Worker 2: High-Vis Non-Compliant (Wearing black jacket, has hard hat)
    w2_x = 440
    w2_y = 365
    draw.ellipse([w2_x + 8, w2_y, w2_x + 28, w2_y + 20], fill=(210, 165, 130))
    draw.arc([w2_x + 4, w2_y - 4, w2_x + 32, w2_y + 12], start=180, end=360, fill=(255, 255, 255), width=6)
    # Dark jacket (VIOLATION)
    draw.rectangle([w2_x + 4, w2_y + 20, w2_x + 32, w2_y + 65], fill=(30, 41, 59))
    draw.rectangle([w2_x + 6, w2_y + 65, w2_x + 16, w2_y + 105], fill=(71, 85, 105))
    draw.rectangle([w2_x + 20, w2_y + 65, w2_x + 30, w2_y + 105], fill=(71, 85, 105))
    draw.rectangle([w2_x + 4, w2_y + 102, w2_x + 18, w2_y + 112], fill=(120, 53, 15))
    draw.rectangle([w2_x + 18, w2_y + 102, w2_x + 32, w2_y + 112], fill=(120, 53, 15))

    # Overlay Inspection Metadata Bar
    draw.rectangle([15, 15, width - 15, 55], fill=(15, 23, 42, 220), outline=(51, 65, 85))
    draw.text((30, 24), "MULTIMODAL AI INSPECTION GRID • ZONE 4A • OSHA 1926 & IS 13415 PROTOCOL", fill=(248, 250, 252))

    img.save(filepath, "JPEG", quality=90)


def create_sample_crack_image(filepath: str):
    """Draws a synthetic high-resolution forensic concrete shear crack surface."""
    width, height = 800, 600
    img = Image.new("RGB", (width, height), color=(185, 188, 192))
    draw = ImageDraw.Draw(img)

    # Concrete granular aggregate texture
    import random
    rng = random.Random(42)
    for _ in range(6000):
        rx = rng.randint(0, width - 1)
        ry = rng.randint(0, height - 1)
        c_shade = rng.randint(140, 210)
        draw.point((rx, ry), fill=(c_shade, c_shade, c_shade))

    # Formwork tie-rod holes
    draw.ellipse([80, 80, 110, 110], fill=(80, 82, 85), outline=(50, 52, 55), width=2)
    draw.ellipse([690, 80, 720, 110], fill=(80, 82, 85), outline=(50, 52, 55), width=2)
    draw.ellipse([80, 490, 110, 520], fill=(80, 82, 85), outline=(50, 52, 55), width=2)
    draw.ellipse([690, 490, 720, 520], fill=(80, 82, 85), outline=(50, 52, 55), width=2)

    # Diagonal 45-degree Structural Shear Crack propagation path
    crack_points = [
        (220, 140), (250, 175), (285, 210), (320, 245), (345, 270),
        (380, 310), (415, 345), (460, 390), (510, 435), (550, 475), (590, 520)
    ]

    # Draw dark jagged crack line
    for i in range(len(crack_points) - 1):
        p1 = crack_points[i]
        p2 = crack_points[i + 1]
        draw.line([p1, p2], fill=(35, 30, 25), width=5)
        # Minor micro-branching
        if i in [2, 5, 8]:
            branch_end = (p1[0] + rng.randint(20, 45), p1[1] - rng.randint(10, 35))
            draw.line([p1, branch_end], fill=(55, 45, 40), width=2)

    # Calibrated forensic crack scale overlay (ruler & mm calibration)
    draw.rectangle([540, 260, 750, 360], fill=(245, 245, 245), outline=(30, 30, 30), width=2)
    draw.text((555, 270), "METROLOGY CRACK GAUGE", fill=(20, 20, 20))
    draw.text((555, 290), "SCALE: 1 div = 0.5 mm", fill=(20, 20, 20))
    draw.text((555, 310), "EST. WIDTH: 1.45 mm", fill=(220, 38, 38))
    draw.text((555, 330), "SPEC: IS 456 LIMIT = 0.30mm", fill=(20, 20, 20))

    # Draw mm tick lines on gauge
    for t_x in range(560, 730, 10):
        h_len = 10 if (t_x % 20 == 0) else 5
        draw.line([(t_x, 345), (t_x, 345 - h_len)], fill=(0, 0, 0), width=1)

    img.save(filepath, "JPEG", quality=90)


if __name__ == "__main__":
    os.makedirs("assets", exist_ok=True)
    ppe_path = os.path.join("assets", "sample_ppe_site.jpg")
    crack_path = os.path.join("assets", "sample_crack_defect.jpg")
    create_sample_ppe_image(ppe_path)
    create_sample_crack_image(crack_path)
    print(f"Sample test images generated successfully: {ppe_path}, {crack_path}")
