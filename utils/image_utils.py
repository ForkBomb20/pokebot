import os
from PIL import Image
import discord

def merge_images_vert(file1, file2):
    """Merge two images into one, displayed side by side
    :param file1: path to first image file
    :param file2: path to second image file
    :return: the merged Image object
    """
    image1 = Image.open(file1)
    image2 = Image.open(file2)

    (width1, height1) = image1.size
    (width2, height2) = image2.size

    result_width = max(width1, width2)
    result_height = height1 + height2

    result = Image.new('RGB', (result_width, result_height))

    result.paste(im=image1, box=(0, 0))
    result.paste(im=image2, box=(0, height1))
    result = result.resize(
        (round(result.size[0] * 2), round(result.size[1] * 2)))
    return result

def create_type_image(types):
    output_dir = "assets/generated"
    os.makedirs(output_dir, exist_ok=True)

    if len(types) == 2:
        img = merge_images_vert(f"./assets/type_panels/{types[0]}.gif", f"./assets/type_panels/{types[1]}.gif")
        filename = f"{types[0]}_{types[1]}.png"
    else:
        img = Image.open(f"./assets/type_panels/{types[0]}.gif").resize((256, 128))
        filename = f"{types[0]}.png"

    output_path = os.path.join(output_dir, filename)
    img.save(output_path)

    return discord.File(fp=output_path)
