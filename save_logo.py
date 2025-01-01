from PIL import Image, ImageDraw, ImageFont
import os

# Create a new image with a dark background
size = (400, 400)
image = Image.new('RGB', size, (20, 20, 30))  # Dark background
draw = ImageDraw.Draw(image)

# Create gradient background
for y in range(size[1]):
    for x in range(size[0]):
        # Create a cyber/tech gradient effect
        gradient = (
            int(20 + (x / size[0]) * 30),  # Dark blue base
            int(20 + (y / size[1]) * 40),
            int(50 + ((x + y) / (size[0] + size[1])) * 100)
        )
        draw.point((x, y), fill=gradient)

# Draw circuit board lines
for i in range(0, size[0], 20):
    color = (0, 255, 255) if i % 40 == 0 else (0, 150, 255)  # Alternate between cyan and light blue
    draw.line([(i, 0), (i, size[1])], fill=color, width=1)

# Draw text with glow effect
text = "GREAT"
text2 = "MATES"
subtitle = "GROUP 2"

try:
    # Try to use a modern font, fall back to default if not available
    font = ImageFont.truetype("arial.ttf", 80)
    subtitle_font = ImageFont.truetype("arial.ttf", 30)
except:
    font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()

# Get text sizes
text_bbox = draw.textbbox((0, 0), text, font=font)
text2_bbox = draw.textbbox((0, 0), text2, font=font)
subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)

# Center text positions
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]
text2_width = text2_bbox[2] - text2_bbox[0]
subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]

# Draw glow effect
glow_colors = [
    (0, 255, 255, 50),  # Cyan with alpha
    (255, 0, 255, 50)   # Magenta with alpha
]

# Create text layer
text_layer = Image.new('RGBA', size, (0, 0, 0, 0))
text_draw = ImageDraw.Draw(text_layer)

# Draw text with glow
x = (size[0] - text_width) // 2
y = (size[1] - text_height * 3) // 2

for offset in range(5, 0, -1):
    text_draw.text((x-offset, y), text, font=font, fill=(0, 255, 255, 50))  # Cyan glow
    text_draw.text((x+offset, y), text, font=font, fill=(255, 0, 255, 50))  # Magenta glow

text_draw.text((x, y), text, font=font, fill=(255, 255, 255))  # Main text

# Draw second text
y2 = y + text_height + 10
x2 = (size[0] - text2_width) // 2

for offset in range(5, 0, -1):
    text_draw.text((x2-offset, y2), text2, font=font, fill=(255, 0, 255, 50))  # Magenta glow
    text_draw.text((x2+offset, y2), text2, font=font, fill=(0, 255, 255, 50))  # Cyan glow

text_draw.text((x2, y2), text2, font=font, fill=(255, 255, 255))  # Main text

# Draw subtitle
y3 = y2 + text_height + 20
x3 = (size[0] - subtitle_width) // 2
text_draw.text((x3, y3), subtitle, font=subtitle_font, fill=(200, 200, 200))

# Composite the text layer onto the background
image = Image.alpha_composite(image.convert('RGBA'), text_layer)

# Save the image
logo_path = os.path.join("test-images", "greatmates_logo.png")
image = image.convert('RGB')
image.save(logo_path)
print(f"Logo created at {logo_path}") 