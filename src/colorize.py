from PIL import Image

def replace(image, replace):
    pixdata = image.load()
    for y in xrange(image.size[1]):
        for x in xrange(image.size[0]):
            for channel, color in replace.items():
                pixel = pixdata[x, y]
                zeroes =  set((0,1,2))-set((channel,))
                if any (pixel[i] for i in zeroes if pixel[i] != 0):
                    continue
                intensity = pixel[channel] / 255.0
                replacement = tuple([int(round(c * intensity)) for c in color] + [pixel[3]])
                pixdata[x, y] = replacement
                break
            else:
                print pixdata[x, y]
    return image

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

image = Image.open("assets/colorize/Billboard-t.png")
#image.convert('RGBA')
replace_colors(image, {0: (33, 144, 4), 1: (200,27,100)})
image.save("assets/colorize/red.png")