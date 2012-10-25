import glob
from PIL import Image
import os

def replace_colors(image, replacemap):
    pixdata = image.load()
    for y in xrange(image.size[1]):
        for x in xrange(image.size[0]):
            pixel = pixdata[x, y]
            r, g, b, a  = pixel
            channel_sum = float(r + g + b)
            ir, ig, ib = r/channel_sum, g/channel_sum, b/channel_sum
            intensities = [ir, ig ,ib]
            new_colors = {}
            for channel, color in replacemap.items():
                new_colors[channel] = [c * intensities[channel] for c in color]
            color = [0,0,0]
            for channel, new_color in new_colors.items():
                for i in range(3):
                    color[i] += new_color[i]
            color = [min(int(c), 255) for c in color]
            pixdata[x, y] = tuple(color + [pixel[3]])


def colorize_images(directory, name, replacemap):
    if not os.path.exists(os.path.join(directory, name)):
        os.makedirs(os.path.join(directory, name))

    for file in glob.glob(os.path.join(directory, '*.png')):
        new_file = os.path.join(directory, name, os.path.basename(file))
        image = Image.open(file)
        replace_colors(image, replacemap)
        image.save(new_file)

#image = Image.open("assets/colorize/Billboard-t.png")
#replace_colors(image, {0: (33, 144, 4), 1: (200,27,100)})
#image.save("assets/colorize/red.png")

replacemap = {0: (33, 144, 4), 1: (200,27,100)}
colorize_images('assets/colorize/', 'test', replacemap)