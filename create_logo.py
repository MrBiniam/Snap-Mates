from PIL import Image, ImageDraw, ImageFont
import os

# Create a new image with a white background
size = (200, 200)
image = Image.new('RGB', size, 'white')
draw = ImageDraw.Draw(image)

# Draw a colored circle
circle_color = (52, 152, 219)  # Nice blue color
circle_center = (100, 100)
circle_radius = 80
draw.ellipse([
    circle_center[0] - circle_radius,
    circle_center[1] - circle_radius,
    circle_center[0] + circle_radius,
    circle_center[1] + circle_radius
], fill=circle_color)

# Draw text
text = "F"
text_color = (255, 255, 255)  # White color
try:
    # Try to use a nice font, fall back to default if not available
    font = ImageFont.truetype("arial.ttf", 120)
except:
    font = ImageFont.load_default()

# Get text size
text_bbox = draw.textbbox((0, 0), text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]

# Center text
text_position = (
    circle_center[0] - text_width // 2,
    circle_center[1] - text_height // 2
)

# Draw the text
draw.text(text_position, text, font=font, fill=text_color)

# Save the image
logo_path = os.path.join("test-images", "icon.png")
image.save(logo_path)
print(f"Logo created at {logo_path}") 