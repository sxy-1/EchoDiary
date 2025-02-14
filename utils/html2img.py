from PIL import Image, ImageDraw, ImageFont


def html_to_image(html):
    # Set up image parameters
    width, height = 800, 600  # You can adjust the size as needed
    background_color = (255, 255, 255)
    # font = ImageFont.load_default()

    # Create a new image with white background
    image = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # Draw text on the image
    draw.text((10, 10), html, fill=(0, 0, 0))

    return image