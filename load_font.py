import os
import json
from PIL import Image
import typing

class Font:
    """ class representing bitmap font """
    def __init__(self, name: str) -> None:
        font_dir = os.path.join('fonts', name)
        description_name = os.path.join(font_dir, 'description.json')

        with open(description_name, 'r') as json_file:
            description = json.load(json_file)

            legal_chars = description['legal_chars']
            self.spacing = description['spacing']
            self.chars = {}

            max_height = 0

            for char in legal_chars:
                """ TODO: support other image formats """
                char_name = os.path.join(font_dir, f'{char}.png')
                image = Image.open(char_name)
                self.chars[char] = image
                if image.height > max_height:
                    max_height = image.height
            
            self.font_height = max_height
            
            for char in self.chars:
                if self.chars[char].height < max_height:
                    new_image = Image.new('RGBA', (self.chars[char].width, max_height), (255, 255, 255, 0))
                    upper = (max_height - self.chars[char].height) // 2
                    new_image.paste(self.chars[char], (0, upper))
                    self.chars[char].close()
                    self.chars[char] = new_image

    def render_string(self, string: str) -> Image.Image:
        total_width = self.spacing * (len(string) - 1)
        for char in string:
            total_width += self.chars[char].width
        
        new_image = Image.new('RGBA', (total_width, self.font_height), (255, 255, 255, 0))
        x_coord = 0
        for char in string:
            new_image.paste(self.chars[char], (x_coord, 0))
            x_coord += self.chars[char].width + self.spacing

        return new_image
    
    def legal_characters(self) -> list[str]:
        return list(self.chars.keys())