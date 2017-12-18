# -*- coding: utf-8 -*-：

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans
from style import readDrawingSetting

# 读取五环内的交互
def readData(filename, rows, columns, minSpeed=2, maxSpeed=150):
    data = np.zeros((rows**2, columns**2), dtype=np.uint32)
    with open(filename, 'r') as f:
        f.readline()
        while True:
            line1 = f.readline().strip()
            line2 = f.readline().strip()
            if line1 and line2:
                sl1 = line1.split(',')
                sl2 = line2.split(',')
                if int(sl1[1]) == 0 or int(sl2[1]) == 0:
                    continue
                if float(sl1[-2]) < minSpeed or float(sl1[-2]) > maxSpeed:
                    continue

                ogid = int(sl1[-1])
                dgid = int(sl2[-1])
                orow = rows - ogid // columns - 1
                ocolumn = ogid % columns
                drow = rows - dgid // columns - 1
                dcolumn = dgid % columns
                ridx = orow * rows + drow
                cidx = ocolumn * columns + dcolumn

                data[ridx, cidx] += 1
            else:
                break
    return data

# kmeans classifier
def kmeans(dn, cNum):
    X = np.sort(dn).reshape((-1,1))
    k = KMeans(n_clusters = cNum, random_state = 0).fit(X)
    labels = []
    for l in k.labels_:
        if l not in labels:
            labels.append(l)
    return k, labels


def drawODMap(file_name, save_file_name, ia):
    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)

    data = readData(file_name, ia['rows'], ia['columns'])
    nk, nl = kmeans(data.flatten(), ia['class_number'])
    gridWidth = ia['gridWidth']

    for r in range(ia['rows']**2):
        top = ia['oy'] + (r - ia['yoffset']) * gridWidth
        for c in range(ia['columns']**2):
            left = ia['ox'] + (c - ia['xoffset']) * gridWidth
            color = ia['color_scheme'][nl.index(nk.predict(data[r, c]))]
            draw.rectangle([(left, top), (left + gridWidth, top + gridWidth)], fill = color)

    for r in range(ia['rows']):
        top = ia['oy'] + (r - ia['yoffset'])*gridWidth*ia['rows']
        for c in range(ia['columns']):
            left = ia['ox'] + (c - ia['xoffset'])*gridWidth*ia['columns']
            draw.rectangle([(left, top), (left+gridWidth*ia['columns'], top+gridWidth*ia['rows'])], outline=ia['border_color'])

    left = (ia['width'] - ia['legend_width']*ia['class_number']) // 2
    bottom = ia['height'] - 10
    for i, c in enumerate(ia['color_scheme']):
        draw.rectangle([(left+i*ia['legend_width'], bottom-ia['legend_height']), (left+(i+1)*ia['legend_width'], bottom)],
                       fill=c)

    imageTitlefont = ImageFont.truetype('./font/times.ttf', 58)
    draw.text((left - 50, bottom - ia['legend_height']), '0', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left + ia['legend_width']*ia['class_number'] + 20, bottom - ia['legend_height']), 'max magnitude', font=imageTitlefont, fill=(0, 0, 0))

    image.save(save_file_name, quality=ia['quality'], dpi=ia['dpi'])


if __name__ == '__main__':
    file_name = './data/sj_1600msq_051316_1721.csv'
    ia = readDrawingSetting()
    drawODMap(file_name, './figure/odmap_1600msq_051316_1721.jpg', ia)

