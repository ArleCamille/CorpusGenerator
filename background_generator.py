import cv2
import numpy as np
import random
import math
from PIL import Image
import os

IMAGE_DIRECTORY = './bgimages'

# original source: https://github.com/Belval/TextRecognitionDataGenerator/blob/173d4572199854943d19dbb5607992331d459c73/trdg/background_generator.py

def gaussian_noise(width: int, height: int) -> Image.Image:
    """ Create background based on gaussian noise"""

    """ Create white canvas """
    image_arr = np.ones((height, width)) * 255

    """ Add Gaussian noise """
    cv2.randn(image_arr, 235, 10)

    return Image.fromarray(image_arr).convert("RGBA")

def plain_white(width: int, height: int) -> Image.Image:
    """ Create a plain white background """
    return Image.new("L", (width, height), 255).convert("RGBA")

def quasicrystal(width: int, height: int) -> Image.Image:
    """ Create a background with quasicrystal """

    with Image.new("L", (width, height)) as image:
        pixels = image.load()

        freq = random.random() * 30 + 20
        phase = random.random() * 2 * math.pi
        rotation_count = random.randint(10, 20)

        for kw in range(width):
            y = float(kw) / (width - 1) * 4 * math.pi - 2 * math.pi
            for kh in range(height):
                x = float(kh) / (height - 1) * 4 * math.pi - 2 * math.pi
                z = 0.0
                for i in range(rotation_count):
                    r = math.hypot(x, y)
                    a = math.atan2(y, x) + i * math.pi * 2.0 / rotation_count
                    z += math.cos(r * math.sin(a) * freq + phase)
                c = int(255 - round(255 * z / rotation_count))
                pixels[kw, kh] = c
        
        return image.convert("RGBA")

def image(width: int, height: int, image_directory: str = IMAGE_DIRECTORY) -> Image.Image:
    """ Crop a stock image """
    images = os.listdir(image_directory)

    if not images:
        raise Exception('Stock image directory is empty!')
    random_image_path = os.path.join(image_directory, random.choice(images))

    with Image.open(random_image_path) as pic:
        if pic.width < width or pic.height < height:
            resize_ratio = max(width / pic.width, height / pic.height)
            with pic.resize((round(pic.width * resize_ratio), round(pic.height * resize_ratio)), Image.Resampling.LANCZOS) as resized_pic:
                return resized_pic.crop((0, 0, width, height))
        else:
            x = random.randint(0, width - pic.width)
            y = random.randint(0, height - pic.height)

            return pic.crop((x, y, x + width, y + height))

def generate_background(width: int, height: int, background_type: int) -> Image.Image:
    match background_type:
        case 0:
            return gaussian_noise(width, height)
        case 1:
            return plain_white(width, height)
        case 2:
            return quasicrystal(width, height)
        case 3:
            return image(width, height)
        case _:
            raise ValueError('invalid type for background')