# SPDX-License-Identifier: MIT

from load_font import Font
from PIL import Image, ImageFilter
import argparse
import random
import background_generator
import os

OUTPUT_DIR = './output'

class CopyFilter(ImageFilter.Filter):
    def __init__(self) -> None:
        pass

    def filter(self, image: Image.Image):
        return image.copy()

def random_string(legal_characters: list[str], min_length: int, max_length: int) -> str:
    random_length = random.randint(min_length, max_length)
    return ''.join(random.choices(legal_characters, k=random_length))

def print_params(opt: argparse.Namespace) -> None:
    print(f'Font: {opt.font}')
    print(f'Will generate {opt.count} image files')
    print(f'Output image height: {opt.format}')
    if opt.random_skew:
        print(f'Skew randomly in between {-opt.skew_angle} ~ {opt.skew_angle} degrees')
    elif opt.skew_angle % 360 == 0:
        print('Don\'t skew')
    else:
        print(f'Skew by {opt.skew_angle % 360} degrees')
    print(f'Output file would be (filename).{opt.extension}')
    if opt.blur < 0:
        raise ValueError('Negative value for Gaussian blur radius')
    elif opt.blur == 0:
        print('Blur: no')
    elif opt.random_blur:
        print(f'Blur: random in between 0 ~ {opt.blur} px')
    else:
        print(f'Blur: fixed {opt.blur} px Gaussian')
    background_type = ''
    match opt.background:
        case 0:
            background_type = 'Gaussian noise'
        case 1:
            background_type = 'plain white'
        case 2:
            background_type = 'quasicrystal'
        case 3:
            background_type = 'image'
        case _:
            raise ValueError('Invalid argument for background type')
    print(f'Background: {background_type}')
    if opt.min_length < 0 or opt.max_length <= 0 or opt.min_length > opt.max_length:
        raise ValueError(f'Invalid length parameter: {opt.min_length} ~ {opt.max_length}')
    print(f'Text length: {opt.min_length} ~ {opt.max_length} characters')

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--font', '-F', required=True, type=str, help='font name to generate corpus of')
    arg_parser.add_argument('--count', '-c', nargs='?', default=1000, type=int, help='count of image files to generate')
    arg_parser.add_argument('--format', '-f', nargs='?', default=32, type=int, help='define the height of the produced images')
    arg_parser.add_argument('-k', '--skew-angle', nargs='?', default=0, type=int, help='define the skewing angle of the generated text, in positive degrees')
    arg_parser.add_argument('-rk', '--random-skew', action='store_true', default=False, help='when set, the skew angle will be randomized in between the value set with -k and its opposite')
    arg_parser.add_argument('-e', '--extension', nargs='?', default='jpg', type=str, help='define the extension to save the images with')
    arg_parser.add_argument('-bl', '--blur', nargs='?', type=int, help="apply Gaussian blur to the resulting sample. Should be a positive integer defining the blur radius.", default=0)
    arg_parser.add_argument('-rbl', '--random-blur', action="store_true", default=False, help="when set, blur will be applied in a random value between 0 and -bl argument")
    arg_parser.add_argument('-b', '--background', nargs='?', type=int, help="define what kind of background to use. 0: Gaussian Noise, 1: Plain white, 2: Quasicrystal, 3: Image", default=0)
    arg_parser.add_argument('-m', '--min-length', nargs='?',  type=int, default=8, help='minimum length of text. (default: 8)')
    arg_parser.add_argument('-M', '--max-length', nargs='?',  type=int, default=16, help='maximum length of text. (default: 8)')
    arg_parser.add_argument('-s', '--start-index', nargs='?', type=int, default=0, help='filename starts from this number')

    opt = arg_parser.parse_args()

    print_params(opt)

    """ 0. load raster font """
    font = Font(opt.font)

    """ 1. generate string """
    strings = []
    legal_characters = font.legal_characters()
    for i in range(opt.count):
        strings.append(random_string(legal_characters, opt.min_length, opt.max_length))

    """ 1.5. make output folder if not existent """
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    print()
    
    index = opt.start_index
    
    filters = []
    if opt.random_blur:
        filters.append(CopyFilter())
        for i in range(1, opt.blur + 1):
            filters.append(ImageFilter.GaussianBlur(radius=i))
    elif opt.blur > 0:
        filters = [ImageFilter.GaussianBlur(radius=opt.blur)]
    else:
        filters = [CopyFilter()]
    for string in strings:
        """ 2. generate plain text, resize and rotate it """
        with font.render_string(string) as raw_image:
            new_width = round(raw_image.width * (opt.format / raw_image.height))
            rotation_angle = random.randint(-opt.skew_angle, opt.skew_angle) if opt.random_skew else opt.skew_angle
            with raw_image.resize((new_width, opt.format), Image.Resampling.LANCZOS) as resized_raw_image, resized_raw_image.rotate(rotation_angle, expand=1) as rotated_raw_image:
                """ 3. apply background """
                bg_width = rotated_raw_image.width + font.font_height
                bg_height = rotated_raw_image.height + font.font_height
                with background_generator.generate_background(bg_width, bg_height, opt.background) as bg, Image.new('RGBA', (bg_width, bg_height), (255, 255, 255, 0)) as composite_fg:
                    composite_fg.paste(rotated_raw_image, (font.font_height // 2, font.font_height // 2))
                    bg.alpha_composite(composite_fg)
                    """ 4. apply gaussian blur if applicable """
                    current_filter = random.choice(filters)
                    with bg.filter(current_filter) as final:
                        filename = str(index).rjust(len(str(len(strings))), '0')
                        image_path = os.path.join(OUTPUT_DIR, f'{filename}.{opt.extension}')
                        try:
                            final.save(image_path)
                        except OSError:
                            with final.convert('RGB') as rgb:
                                rgb.save(image_path)
                        
                        print(f'Saved file {image_path}')

                    index += 1