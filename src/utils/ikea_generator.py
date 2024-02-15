from PIL import Image, ImageEnhance
import requests
from io import BytesIO

# URL of the image to be processed
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Ikea_logo.svg/2560px-Ikea_logo.svg.png"

# Download the image
response = requests.get(image_url)
img = Image.open(BytesIO(response.content))

# Resize the image to 100px wide
width = 100
aspect_ratio = width / img.width
new_height = int(img.height * aspect_ratio)
img_resized = img.resize((width, new_height), Image.BICUBIC)

# Create a white background image of the same size
white_background = Image.new('RGB', img_resized.size, (255, 255, 255))

# Blend the resized image with the white background
# Adjust the alpha parameter to control the 'opacity' effect
alpha = 0.94  # Experiment with this value, closer to 1 makes the image lighter
img_lighter = Image.blend(img_resized, white_background, alpha=alpha)


# Create a new image for the tiled pattern
screen_width, screen_height = 2560, 1440
tiled_img = Image.new('RGB', (screen_width, screen_height))

# Calculate the starting points to center the tiling
start_x = - (screen_width % width) // 2
start_y = - (screen_height % new_height) // 2

# Tile the brighter image
for x in range(start_x, screen_width, width):
    for y in range(start_y, screen_height, new_height):
        tiled_img.paste(img_lighter, (x, y))

# Save the tiled image
tiled_img.save('imgs/tiled_ikea_logo.png')

print("Centered and brighter tiled image saved successfully.")
