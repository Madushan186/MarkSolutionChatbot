from PIL import Image, ImageDraw, ImageFont, ImageOps
import os

# Settings
BG_COLOR = "#D32F2F" # Company Red
TEXT_COLOR = "white"
SIZES = {
    "favicon.ico": (64, 64), # High qual ico
    "logo192.png": (192, 192),
    "logo512.png": (512, 512)
}
OUTPUT_DIR = "frontend/public"

def generate_logo(filename, size):
    # Create valid image
    img = Image.new('RGB', size, color=BG_COLOR)
    draw = ImageDraw.Draw(img)
    
    # Text
    # Load default font or fallback
    try:
        # Try to load a nicer font if available on linux/mac
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", int(size[0]*0.5))
    except:
        try:
             font = ImageFont.truetype("arial.ttf", int(size[0]*0.5))
        except:
            font = ImageFont.load_default() 

    text = "MS"
    
    # Calculate text position (rough centering)
    # PIL's text centering is tricky without specific font metrics, using rough estimate
    # For simple default font, it might be small.
    # Drawing simple rectangle + text
    
    # Let's simple draw text in center.
    draw.text((size[0]/2, size[1]/2), text, font=font, fill=TEXT_COLOR, anchor="mm")
    
    # Save
    path = os.path.join(OUTPUT_DIR, filename)
    if filename.endswith(".ico"):
        img.save(path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64)])
    else:
        img.save(path)
    print(f"Generated {path}")

# Run
for name, dim in SIZES.items():
    generate_logo(name, dim)
