import random, os
import string
from PIL import Image
from captcha.image import ImageCaptcha
script_path = os.path.dirname(os.path.abspath(__file__))


def gen_captcha(size):
    """ loading captcha settings """
    fonts = ['Roboto-Black.ttf', 'RobotoCondensed-Bold.ttf']
    path_fonts = [os.path.join(script_path, "ttf", f) for f in fonts]
    image = ImageCaptcha(fonts=path_fonts)
    """ Generating captcha text and id """
    text = random_string(6)
    data = image.generate(text)
    # image.write(text, f'{text}.png')
    return text, data


def random_string(size):
    rndLetters = (random.choice(string.ascii_uppercase) for _ in range(size))
    rndLetters = "".join(rndLetters)
    return rndLetters


def test():
    text, imagen = gen_captcha(6)
    print(text, imagen)

# test()