# -*- coding: utf-8 -*-：

from PIL import Image, ImageDraw, ImageFont
from LL2UTM import LL2UTM_USGS
from draw import kmeans, computeCen, computeCo
import numpy as np
from grid import Grid
import style


# 读取五环内的交互
def readData_Inside(filename, dnum, minSpeed=2, maxSpeed=150):
    flows_co = {}
    grids = {}

    with open(filename, 'r') as f:
        f.readline()
        while True:
            line1 = f.readline().strip()
            if line1:
                line2 = f.readline().strip()
                sl1 = line1.split(',')
                sl2 = line2.split(',')
                if int(sl1[1]) == 0 or int(sl2[1]) == 0:
                    continue
                if float(sl1[-2]) < minSpeed or float(sl1[-2]) > maxSpeed:
                    continue

                ogid = int(sl1[-1])
                dgid = int(sl2[-1])
                if ogid not in grids:
                    grids[ogid] = Grid(ogid, dnum)
                if dgid not in grids:
                    grids[dgid] = Grid(dgid, dnum)

                ox, oy = LL2UTM_USGS(float(sl1[-5]), float(sl1[-6]))
                dx, dy = LL2UTM_USGS(float(sl2[-5]), float(sl2[-6]))
                if np.sqrt((dx-ox)**2+(dy-oy)**2) <= 500:
                    grids[ogid].round_flow_num += 1
                    continue

                fid = int(sl1[-4])
                flows_co[fid] = [(ox, oy), (dx, dy)]

                grids[ogid].addOutFlow(fid)
                grids[dgid].addInFlow(fid)
            else:
                break

    return grids, flows_co

def statistic(data_file, dis_class_num, dnum):
    grids, flows = readData_Inside(data_file, dnum)

    dis = []
    for gid in grids:
        grids[gid].calcOutList(flows)
        for ld in grids[gid].ld:
            dis.extend(ld)
    dk, dl = kmeans(dis, dis_class_num)

    grid_sta = {}
    round_flow = {}
    maxmag = 0
    for gid in grids:
        grid_sta[gid] = []
        for i in range(dnum):
            grid_sta[gid].append([0, 0, 0])
        for j, ld in enumerate(grids[gid].ld):
            for d in ld:
                idx = dl.index(dk.predict(d))
                grid_sta[gid][j][idx] += 1
        for maglist in grid_sta[gid]:
            for num in maglist:
                if num > maxmag:
                    maxmag = num
        if grids[gid].round_flow_num > maxmag:
            maxmag = grids[gid].round_flow_num
        round_flow[gid] = grids[gid].round_flow_num

    return grid_sta, round_flow, maxmag

def drawDiagramMap_RO1_old(data_file, ia, save_file, dnum=6):
    grid_sta, round_flow, maxmag = statistic(data_file, ia['class_num'], dnum)

    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    if dnum == 6:
        angle = [(300, 0), (240, 300), (180, 240), (120, 180), (60, 120), (0, 60)]
    radius = ia['radius']

    '''
    xs, ys = computeCo(ia['gridWidth'], dnum//6)
    for gid in grid_sta:
        cenx, ceny = computeCen(gid, ia)
        border = []
        for i in range(dnum):
            border.append(cenx + xs[i])
            border.append(ceny + ys[i])
        draw.polygon(border, outline = ia['border_color'])
    '''

    for gid in grid_sta:
        cenx, ceny = computeCen(gid, ia)
        for i in range(dnum):
            r = np.cumsum(np.array(grid_sta[gid][i])*radius/maxmag)
            for j in range(ia['class_num']-1, -1, -1):
                draw.pieslice([cenx-r[j], ceny-r[j], cenx+r[j], ceny+r[j]], angle[i][0], angle[i][1],
                              fill=ia['color_scheme'][j], outline='#fe0000')
        r = round_flow[gid]*radius/maxmag
        draw.arc([cenx-r, ceny-r, cenx+r, ceny+r], 0, 360, fill='#323232')

    x = ia['width'] - 700
    y = ia['height'] - 200
    legend_size = 200
    for j in range(ia['class_num'] - 1, -1, -1):
        r = (j+1)*legend_size/ia['class_num']
        draw.pieslice([x - r, y - r, x + r, y + r], 300, 0, fill=ia['color_scheme'][j], outline='#fe0000')
    draw.pieslice([x - legend_size + 400, y - legend_size, x + legend_size + 400, y + legend_size], 300, 0, fill=None, outline='#fe0000')
    px = x + 400
    draw.line([px, y, px + np.sqrt(3)*legend_size/2, y - legend_size/2], width=1, fill='#000000')
    draw.line([px + np.sqrt(3)*legend_size/2, y-legend_size/2, px + np.sqrt(3)*legend_size/2-20, y-legend_size/2], width=1, fill='#000000')
    draw.line([px + np.sqrt(3)*legend_size/2, y-legend_size/2, px + np.sqrt(3)*legend_size/2-12, y-legend_size/2+19], width=1, fill='#000000')

    imagescalefont = ImageFont.truetype('./font/times.ttf', 40)
    draw.text((x - 110, y - 40), 'Short', font=imagescalefont, fill=(0, 0, 0))
    draw.text((x - 110, y - 130), 'Medium', font=imagescalefont, fill=(0, 0, 0))
    draw.text((x - 20, y - 200), 'Long', font=imagescalefont, fill=(0, 0, 0))
    draw.text((px - 50, y + 10), 'Low', font=imagescalefont, fill=(0, 0, 0))
    draw.text((px + 180, y + 10), 'High', font=imagescalefont, fill=(0, 0, 0))

    imageTitlefont = ImageFont.truetype('./font/times.ttf', 50)
    draw.text((x, y + 60), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((px, y + 60), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))

    image.save(save_file, quality=ia['quality'], dpi=ia['dpi'])

def drawDiagramMap_AJ1(data_file, ia, save_file, dnum=6):
    grid_sta, round_flow, maxmag = statistic(data_file, ia['class_num'], dnum)

    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    angle = [330, 270, 210, 150, 90, 30]
    radii = ia['radii']

    for gid in grid_sta:
        cenx, ceny = computeCen(gid, ia)
        for i in range(dnum):
            r = np.array(grid_sta[gid][i])*60/maxmag
            for j in range(ia['class_num']-1,-1,-1):
                draw.pieslice([cenx-radii[j], ceny-radii[j], cenx+radii[j], ceny+radii[j]], angle[i]-r[j], angle[i]+r[j],
                              fill=ia['color_scheme'][j], outline='#fe0000')
        #r = round_flow[gid]*radius/maxmag
        #draw.arc([cenx-r, ceny-r, cenx+r, ceny+r], 0, 360, fill='#323232')

    image.save(save_file, quality=ia['quality'], dpi=ia['dpi'])

def readZones(file_name):
    zones = {}
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for line in lines[1:]:
            sl = line.strip().split(',')
            zones[int(sl[0])] = (float(sl[1]), float(sl[2]))
    return zones

def drawRingRoad(draw, file_name, xoff, yoff):
    with open(file_name, 'r') as f:
        lines = f.readlines()
        tag = 0
        pts = []
        for line in lines[1:]:
            sl = line.strip().split(',')
            x, y = LL2UTM_USGS(float(sl[3]), float(sl[2]))
            x = (x - xoff) / 10
            y = ia['height'] - (y - yoff) / 10
            if int(sl[1]) == tag:
                pts.append((x, y))
            else:
                draw.line(pts, fill='#000000', width=2)
                tag = int(sl[1])
                pts = [(x, y)]
        draw.line(pts, fill='#000000', width=2)

def drawRoundTrip(draw, cenx, ceny, r):
    a = np.arange(0, 360, 10) * 2 * np.pi / 360
    xs = cenx + r * np.cos(a)
    ys = ceny + r * np.sin(a)
    for x, y in zip(xs, ys):
        draw.ellipse([x-1,y-1,x+1,y+1], fill='#323232')

def drawDiagramMap_RO1(data_file, zone_file, ia, save_file, dnum=6):
    grid_sta, round_flow, maxmag = statistic(data_file, ia['class_num'], dnum)
    zones = readZones(zone_file)

    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)
    if dnum == 6:
        angle = [(300, 0), (240, 300), (180, 240), (120, 180), (60, 120), (0, 60)]
    radius = ia['radius']
    xoff = 431500
    yoff = 4400700

    drawRingRoad(draw, './data/ringroad_pt.csv', xoff, yoff)

    for gid in grid_sta:
        cenx, ceny = zones[gid]
        cenx = (cenx - xoff) / 10
        ceny = ia['height'] - (ceny - yoff) / 10
        for i in range(dnum):
            r = np.cumsum(np.array(grid_sta[gid][i])*radius/maxmag)
            for j in range(ia['class_num']-1, -1, -1):
                draw.pieslice([cenx-r[j], ceny-r[j], cenx+r[j], ceny+r[j]], angle[i][0], angle[i][1],
                              fill=ia['color_scheme'][j], outline='#fe0000')
        r = round_flow[gid]*radius/maxmag
        drawRoundTrip(draw, cenx, ceny, r)

    labelfont = ImageFont.truetype('./font/calibril.ttf', 110)
    draw.text((930, 1480), 'A', font=labelfont, fill=(0, 0, 0))
    draw.text((2310, 1560), 'B', font=labelfont, fill=(0, 0, 0))
    draw.text((1570, 550), 'C', font=labelfont, fill=(0, 0, 0))
    left = 650
    right = 1230
    top = 380
    bottom = 920
    draw.line([left, top, right, top, right, bottom, left, bottom, left, top], fill='#0000ff', width=4)
    draw.text((left+20, top+20), 'D', font=labelfont, fill=(0, 0, 0))

    x = ia['width'] - 700
    y = ia['height'] - 200
    legend_size = 200
    for j in range(ia['class_num'] - 1, -1, -1):
        r = (j+1)*legend_size/ia['class_num']
        draw.pieslice([x - r, y - r, x + r, y + r], 300, 0, fill=ia['color_scheme'][j], outline='#fe0000')
    draw.pieslice([x - legend_size + 400, y - legend_size, x + legend_size + 400, y + legend_size], 300, 0, fill=None, outline='#fe0000')
    #draw.arc([x + 500 - legend_size/3, y - 400 - legend_size/3, x + 500 + legend_size/3, y - 400 + legend_size/3], 0, 360, fill='#323232')
    drawRoundTrip(draw, x + 500, y - 400, legend_size/3)
    px = x + 400
    draw.line([px, y, px + np.sqrt(3)*legend_size/2, y - legend_size/2], width=1, fill='#000000')
    draw.line([px + np.sqrt(3)*legend_size/2, y-legend_size/2, px + np.sqrt(3)*legend_size/2-20, y-legend_size/2], width=1, fill='#000000')
    draw.line([px + np.sqrt(3)*legend_size/2, y-legend_size/2, px + np.sqrt(3)*legend_size/2-12, y-legend_size/2+19], width=1, fill='#000000')

    imagescalefont = ImageFont.truetype('./font/times.ttf', 40)
    draw.text((x - 110, y - 40), 'Short', font=imagescalefont, fill=(0, 0, 0))
    draw.text((x - 110, y - 130), 'Medium', font=imagescalefont, fill=(0, 0, 0))
    draw.text((x - 20, y - 200), 'Long', font=imagescalefont, fill=(0, 0, 0))
    draw.text((px - 50, y + 10), 'Low', font=imagescalefont, fill=(0, 0, 0))
    draw.text((px + 180, y + 10), 'High', font=imagescalefont, fill=(0, 0, 0))

    imageTitlefont = ImageFont.truetype('./font/times.ttf', 50)
    draw.text((x, y + 60), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((px, y + 60), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((x + 380, y - 310), 'Round trips', font=imageTitlefont, fill=(0, 0, 0))

    image.save(save_file, quality=ia['quality'], dpi=ia['dpi'])



if __name__ == '__main__':
    data_file = './data/sj_051316_1721_5rr_gp.csv'
    save_file = './figure/dm_051316_1721_1km_5rr_RO1.jpg'
    ia = style.readDrawingSetting('dm')

    drawDiagramMap_RO1(data_file, './data/group_051316_1721_r3km.csv', ia, save_file)

