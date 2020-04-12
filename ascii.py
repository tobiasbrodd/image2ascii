from getopt import getopt, GetoptError
from PIL import Image
import sys

from enum import Enum


class Scale(Enum):
    TEN = " .:-=+*#%@"
    STANDARD = " .'`^\",:;Il!i><~+_-?][}{1)(|\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
    COLOR = "#%@"


def get_image(path):
    try:
        image = Image.open(path)
        return image
    except Exception as error:
        print(error)
        return None


def resize(image, new_width=100):
    (width, height) = image.size
    aspect_ratio = float(height) / float(width)
    new_height = int(aspect_ratio * new_width / 2)
    dim = (new_width, new_height)

    return image.resize(dim)


def to_greyscale(image):
    return image.convert("L")


def color(s, r, g, b):
    return f"\033[38;2;{r};{g};{b}m{s}\033[0m"


def to_ascii(image, scale=Scale.STANDARD, invert=False):
    ASCII_CHARS = scale.value
    if invert:
        ASCII_CHARS = ASCII_CHARS[::-1]
    pixels = list(image.getdata())
    buckets = (255 // len(ASCII_CHARS)) + 1
    ascii_pixels = [ASCII_CHARS[p // buckets] for p in pixels]

    return "".join(ascii_pixels)


def to_ascii_color(image, image_grey, scale=Scale.COLOR, invert=False):
    ASCII_CHARS = scale.value
    if invert:
        ASCII_CHARS = ASCII_CHARS[::-1]
    colored_pixels = list(image.getdata())
    grey_pixels = list(image_grey.getdata())
    pixel_colors = [(p[0], p[1], p[2]) for p in colored_pixels]

    buckets = (255 // len(ASCII_CHARS)) + 1
    ascii_pixels = [ASCII_CHARS[p // buckets] for p in grey_pixels]

    return "".join(ascii_pixels), pixel_colors


def convert_grey(image, width=100, scale=Scale.STANDARD, invert=False):
    image = resize(image, new_width=width)
    image = to_greyscale(image)

    ascii_pixels = to_ascii(image, scale=scale, invert=invert)
    n = len(ascii_pixels)
    ascii_image = [ascii_pixels[i : i + width] for i in range(0, n, width)]

    return "\n".join(ascii_image)


def convert_color(image, width=100, scale=Scale.COLOR, invert=False):
    image = resize(image, new_width=width)
    image_grey = to_greyscale(image)

    ascii_pixels, pixel_colors = to_ascii_color(
        image, image_grey, scale=scale, invert=invert
    )
    n = len(ascii_pixels)
    colored_ascii_pixels = []
    for (i, pixel) in enumerate(ascii_pixels):
        rgb = pixel_colors[i]
        colored_pixel = color(pixel, rgb[0], rgb[1], rgb[2])
        colored_ascii_pixels.append(colored_pixel)
    colored_ascii_image = [
        colored_ascii_pixels[i : i + width] for i in range(0, n, width)
    ]
    colored_ascii_image = ["".join(row) for row in colored_ascii_image]

    return "\n".join(colored_ascii_image)


def convert(image, width=100, scale=Scale.STANDARD, color=False, invert=False):
    if color:
        return convert_color(image, width=width, scale=scale, invert=invert)
    else:
        return convert_grey(image, width=width, scale=scale, invert=invert)


def main(argv):
    global ASCII_CHARS

    short_options = "h"
    long_options = ["help", "path=", "width=", "scale=", "color", "invert"]
    help_message = """usage: download.py [options]
    options:
        -h, --help          Prints help message.
        --path p            Path to image.
        --width w           Sets ASCII image width to 'w'. Default '100'.
        --scale s           Sets ASCII scale to 's' <STANDARD | TEN | COLOR>. Default 'STANDARD'.
        --color             Enables colored ASCII image.
        --invert            Inverts ASCII greyscale."""

    try:
        opts, args = getopt(argv, shortopts=short_options, longopts=long_options)
    except GetoptError:
        print(help_message)
        return

    path = None
    width = 100
    scale = Scale.STANDARD
    color = False
    invert = False

    for opt, arg in opts:
        if opt in ["-h", "--help"]:
            print(help_message)
            return
        elif opt == "--path":
            path = arg
        elif opt == "--width":
            width = int(arg)
        elif opt == "--scale":
            scale = Scale[arg.upper()]
        elif opt == "--color":
            color = True
        elif opt == "--invert":
            invert = True

    image = get_image(path)

    if image is None:
        print(help_message)
        return

    ascii_image = convert(image, width=width, scale=scale, color=color, invert=invert)

    print(ascii_image)


if __name__ == "__main__":
    main(sys.argv[1:])
