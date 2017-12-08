# -*- coding: utf-8 -*-：

from PIL import Image, ImageDraw, ImageFont
from sklearn.cluster import KMeans
import operator
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# kmeans classifier
def kmeans(dn, cNum):
    X = np.sort(dn).reshape((-1,1))
    k = KMeans(n_clusters = cNum, random_state = 0).fit(X)
    labels = []
    for l in k.labels_:
        if l not in labels:
            labels.append(l)
    return k, labels

def computeRC(gid, hexParm):
    if gid < hexParm[1]:
        y = int(gid/hexParm[0])*2
        x = (gid % hexParm[0])*2 + 1
    else:
        y = int((gid-hexParm[1])/hexParm[0])*2 + 1
        x = ((gid-hexParm[1]) % hexParm[0])*2
    return y, x

# compute central point coordinates
def computeCen(gid, ia):
    hexParm = ia['hexParm']
    totalY = computeRC(hexParm[1]-1, hexParm)[0] + 2
    y, x = computeRC(gid, hexParm)

    a = (ia['gridWidth'] + ia['margin']) * 3 / 2
    b = (ia['gridWidth'] + ia['margin']) * np.sqrt(3) / 2
    cenx = ia['ox'] + (x - ia['xoffset'] + 1) * a
    ceny = ia['oy'] + (totalY - y - ia['yoffset'] + 1) * b
    return cenx, ceny

# compute edge point coordinates of a regular octagon
def computeCo_hexagon(cenx, ceny, gridWidth):
    dx = gridWidth*np.cos(np.pi/3)
    dy = gridWidth*np.sin(np.pi/3)
    p = [(cenx+gridWidth, ceny), (cenx+dx, ceny-dy), (cenx-dx, ceny-dy), (cenx-gridWidth, ceny),
         (cenx-dx, ceny+dy), (cenx+dx, ceny+dy), (cenx+gridWidth, ceny)]

    co = []
    for i in range(6):
        co.append([cenx, ceny, p[i][0], p[i][1], p[i+1][0], p[i+1][1]])
    return co

def computeCo(gridWidth, n):
    dx = gridWidth * np.cos(np.pi / 3)
    dy = gridWidth * np.sin(np.pi / 3)
    a = np.array(range(0, n))*np.pi/(3*n)
    x = dx - gridWidth * np.sin(a) / np.sin(2*np.pi/3 - a)
    y = np.array([-dy] * len(a))
    xs = []
    ys = []
    for rotate in [np.pi/3, 0, 5*np.pi/3, 4*np.pi/3, np.pi, 2*np.pi/3]:
        xs.extend(np.round(x * np.cos(rotate) - y * np.sin(rotate)))
        ys.extend(np.round(x * np.sin(rotate) + y * np.cos(rotate)))

    xs.append(xs[0])
    ys.append(ys[0])
    return xs, ys

def drawGridSymbol_hexagon(cs):
    iwidth = iheight = 670*2
    gridWidth = 300*2
    gridBorderWidth = 20*2

    image = Image.new("RGB", (iwidth, iheight), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    cenx = iwidth/2
    ceny = iheight/2

    xs, ys = computeCo(gridWidth, 1)
    cs.append(cs[2])
    for i in range(6):
        c = '#%02X%02X%02X' % (int(float(i+1)/7 * 255), int(float(i+1)/7 * 255), int(float(i+1)/7 * 255))
        draw.polygon([cenx,ceny,cenx+xs[i], ceny+ys[i], cenx+xs[i+1], ceny+ys[i+1]], fill=c, outline=c)
        draw.line([cenx + xs[i], ceny + ys[i], cenx + xs[i + 1], ceny + ys[i + 1]], width=gridBorderWidth, fill=cs[i])


    image.save('./figure/grid symbol.jpg', quality=1000, dpi=(1200,1200))

def drawPattern(grids, flows, dnum, ia, saveFileName):
    # -------------------------------classify data----------------------------------
    mag = []
    dis = []
    for g in grids:
        grids[g].calcOutAggregation(flows)
        for tm in grids[g].wm:
            mag.append(tm)
        for td in grids[g].wd:
            dis.append(td)

    nk, nl = kmeans(mag, ia['mag_class_number'])
    dk, dl = kmeans(dis, ia['dis_class_number'])

    # -----------------------------draw visual glyphs-------------------------------
    image = Image.new('RGB', (ia['width'], ia['height']), '#ffffff')
    draw = ImageDraw.Draw(image)

    gridWidth = ia['gridWidth']
    xs, ys = computeCo(gridWidth, dnum//6)
    for gid in grids:
        cenx, ceny = computeCen(gid, ia)
        border = []
        for i in range(dnum):
            border.append(cenx + xs[i])
            border.append(ceny + ys[i])
            j = nl.index(nk.predict(grids[gid].wm[i]))
            k = dl.index(dk.predict(grids[gid].wd[i]))
            nc = ia['color_scheme'][j][k]
            draw.polygon([cenx,ceny,cenx+xs[i], ceny+ys[i], cenx+xs[i+1], ceny+ys[i+1]], fill=nc, outline=nc)
        draw.polygon(border, outline = ia['border_color'])

    # ----------------------------mark locations------------------------------
    indicatorfont = ImageFont.truetype('./font/times.ttf', 90)
    if False:
        cenx, ceny = computeCen(128, ia)
        draw.line([cenx, ceny, 2850, 750], width=2, fill='#000000')
        draw.text((2870, 700), 'B', font=indicatorfont, fill='#000000')
        cenx, ceny = computeCen(100, ia)
        draw.line([cenx, ceny, 300, 2500], width=2, fill='#000000')
        draw.text((230, 2460), 'A', font=indicatorfont, fill='#000000')
    '''
    labelfont = ImageFont.truetype('./font/times.ttf', 50)
    labelColor = '#0000ff'#'#003371'
    textColor = '#871F78'
    if '1km' in saveFileName:
        if '0105' in saveFileName:
            cenx, ceny = computeCen(150, ia)
            draw.text((cenx-24, ceny+30), 'A', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(164, ia)
            draw.text((cenx-87, ceny+10), 'B', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(437, ia)
            draw.text((cenx-20, ceny+45), 'C', font=indicatorfont, fill=labelColor)

            draw.text((30, ia['height']-180), 'A: The Forbidden City', font=labelfont, fill=textColor)
            draw.text((30, ia['height']-120), 'B: Sanlitun', font=labelfont, fill=textColor)
            draw.text((30, ia['height']-60), 'C: Wudaokou', font=labelfont, fill=textColor)
        elif '0509' in saveFileName:
            cenx, ceny = computeCen(150, ia)
            draw.text((cenx - 24, ceny + 30), 'A', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(176, ia)
            draw.text((cenx - 105, ceny - 40), 'B', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(124, ia)
            draw.text((cenx + 10, ceny - 115), 'C', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(356, ia)
            draw.text((cenx + 50, ceny - 85), 'D', font=indicatorfont, fill=labelColor)

            draw.text((30, ia['height'] - 180), 'A: The Forbidden City', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 120), 'B: Sanyuanqiao (A transfer station)', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 60), 'C: Beijing West Railway Station', font=labelfont, fill=textColor)
            draw.text((800, ia['height'] - 60), 'D: Shuangjin', font=labelfont, fill=textColor)
    elif '500m' in saveFileName:
        if '0509' in saveFileName:
            cenx, ceny = computeCen(563, ia)
            draw.text((cenx - 24, ceny), 'A', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(1647, ia)
            draw.text((cenx - 65, ceny - 40), 'B', font=indicatorfont, fill=labelColor)
            cenx, ceny = computeCen(487, ia)
            draw.text((cenx + 5, ceny - 70), 'C', font=indicatorfont, fill=labelColor)

            draw.text((30, ia['height'] - 180), 'A: The Forbidden City', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 120), 'B: Sanyuanqiao', font=labelfont, fill=textColor)
            draw.text((30, ia['height'] - 60), 'C: Beijing West Railway Station', font=labelfont, fill=textColor)
    '''

    # -----------------------------draw legends-------------------------------

    imageTitlefont = ImageFont.truetype('./font/times.ttf', 52)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 48)
    ls = ia['legend_size']
    bottom = ia['height'] - ia['legend_yoffset']
    left = ia['width'] - ia['dis_class_number']*ls - ia['legend_xoffset']

    for j in range(ia['mag_class_number']):
        for k in range(ia['dis_class_number']):
            draw.rectangle([(left+k*ls, bottom-j*ls),(left+(k+1)*ls, bottom-(j+1)*ls)], fill = ia['color_scheme'][j][k])

    draw.text((left - 300, bottom - ia['mag_class_number'] * ls / 2 - 30), 'Magnitude', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left - 120, bottom - 30), 'Low', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((left - 120, bottom - ia['mag_class_number'] * ls - 10), 'High', font=imageMeasureFont, fill=(0, 0, 0))

    draw.text((left + ia['dis_class_number'] * ls / 2 - 90, bottom + 60), 'Distance', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((left - 80, bottom + 20), 'Short', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((left + ia['dis_class_number'] * ls - 40, bottom + 20), 'Long', font=imageMeasureFont, fill=(0, 0, 0))

    # -----------------------------save figure-------------------------------
    iquality = ia['quality']
    idpi = ia['dpi']
    image.save(saveFileName, quality=iquality, dpi=idpi)

# magnitude difference
def mdif(m1, m2):
    if operator.eq(m1, m2):
        return 0
    n = 0
    for n1, n2 in zip(m1, m2):
        n += abs(n2-n1)
    return n

# distance difference
def ddif(d1, d2, m1, m2):
    if operator.eq(d1, d2):
        return 0
    n = []
    w = []
    for i in range(len(d1)):
        w.append(abs(m2[i]-m1[i]))
        n.append(abs(d2[i]-d1[i]))
    if sum(w)==0:
        return sum(n)
    else:
        s = 0
        for i, tw in enumerate(w):
            s += tw*n[i]
        return float(s)/sum(w)

# comprehensive difference between two patterns
def cdif(grids1, grids2, flows1, flows2, alpha):
    d_difN = {}
    d_difD = {}
    maxD = 0
    maxN = 0
    minD = float('inf')
    minN = float('inf')

    for gid in grids1:
        grids1[gid].calcOutAggregation(flows1)
        grids2[gid].calcOutAggregation(flows2)
        difN = mdif(grids1[gid].wm, grids2[gid].wm)
        difD = ddif(grids1[gid].wd, grids2[gid].wd, grids1[gid].wm, grids2[gid].wm)
        d_difN[gid] = difN
        d_difD[gid] = difD
        minN = min(minN, difN)
        maxN = max(maxN, difN)
        minD = min(minD, difD)
        maxD = max(maxD, difD)

    dif = {}
    for gid in grids1:
        dif[gid] = alpha*(d_difN[gid]-minN)/(maxN-minN) + (1-alpha)*(d_difD[gid]-minD)/(maxD-minD)

    return dif

# comprehensive difference between several patterns and a specific pattern
def cdif_multi(lgrids, lflows, alpha):
    d_difN = {}
    d_difD = {}
    tNum = (len(lgrids) - 1)
    for gid in lgrids[0]:
        d_difN[gid] = [0] * tNum
        d_difD[gid] = [0] * tNum
    maxD = 0
    maxN = 0
    minD = float('inf')
    minN = float('inf')

    for i in range(tNum+1):
        for g in lgrids[i]:
            lgrids[i][g].calcOutAggregation(lflows[i])

    for gid in lgrids[0]:
        for i in range(1, tNum+1):
            difN = mdif(lgrids[0][gid].wm, lgrids[i][gid].wm)
            difD = ddif(lgrids[0][gid].wd, lgrids[i][gid].wd, lgrids[0][gid].wm, lgrids[i][gid].wm)
            d_difN[gid][i-1] = difN
            d_difD[gid][i-1] = difD
            minN = min(minN, difN)
            maxN = max(maxN, difN)
            minD = min(minD, difD)
            maxD = max(maxD, difD)

    dif = {}
    for gid in lgrids[0]:
        dif[gid] = [0] * tNum
        for i in range(tNum):
            dif[gid][i] = alpha*(d_difN[gid][i]-minN)/(maxN-minN) + (1-alpha)*(d_difD[gid][i]-minD)/(maxD-minD)

    return dif

def drawCdif_Kmeans(grids1, grids2, flows1, flows2, alpha, ia, saveFileName):
    k_dif = ia['k_dif']
    dif = cdif(grids1, grids2, flows1, flows2, alpha)
    dif_train = []
    for gid in grids1:
        dif_train.append([dif[gid], 0])
    difk, difl = kmeans(dif_train, k_dif)
    ia['margin'] /= 2
    ia['height'] = 2700
    ia['width'] = 2700
    ia['ox'] = 10
    ia['oy'] = 30
    c_dif = ia['c_dif']
    gridWidth = ia['gridWidth']
    iwidth = ia['width']
    iheight = ia['height']

    image = Image.new("RGB", (iwidth, iheight), '#ffffff')
    draw = ImageDraw.Draw(image)

    for gid in grids1:
        cenx, ceny = computeCen(gid, ia)
        hex_co = computeCo_hexagon(cenx, ceny, gridWidth)

        nc = c_dif[difl.index(difk.predict([[dif[gid], 0]])[0])]
        co = []
        for item in hex_co:
            co.append(item[2])
            co.append(item[3])
        co.append(co[0])
        co.append(co[1])
        draw.polygon(co, fill=nc, outline=nc)

    '''
    if True:
        indicatorfont = ImageFont.truetype('./font/times.ttf', 50)
        cenx, ceny = computeCen(5262, ia, shape)
        symbolWidth = gridWidth + ia['margin']
        draw.line([cenx, ceny, cenx-2*symbolWidth+10, ceny+3*symbolWidth], width=1, fill='#000000')
        draw.text((cenx-2*symbolWidth-10, ceny+3*symbolWidth+10), u'\u2161', font=indicatorfont, fill=(0,0,0))

        cenx, ceny = computeCen(6476, ia, shape)
        symbolWidth = gridWidth + ia['margin']
        draw.line([cenx, ceny, cenx + 9 * symbolWidth+10, ceny - 4 * symbolWidth-5], width=1, fill='#000000')
        draw.text((cenx + 9 * symbolWidth+30, ceny - 4 * symbolWidth - 45), u'\u2160', font=indicatorfont, fill=(0, 0, 0))
    '''
    # ----绘制边框----
    #fm = ia['frameMargin']
    #draw.rectangle([fm, fm, iwidth - fm, iheight - fm], outline='#000000')

    # ----绘制图例----
    imageTitlefont = ImageFont.truetype('./font/times.ttf', 54)
    imageMeasureFont = ImageFont.truetype('./font/times.ttf', 50)
    sy = iheight - 50
    lw = ia['legendWidth']*2

    # 绘制差异矩形
    mx = iwidth - 300
    for i, c in enumerate(c_dif):
        draw.line([mx, sy - i * lw, mx + gridWidth, sy - i * lw], width=lw, fill=c)

    draw.text((mx - gridWidth / 2 - 40, sy - (k_dif + 3) * lw), 'Difference', font=imageTitlefont, fill=(0, 0, 0))
    draw.text((mx + 60 + gridWidth / 2, sy - lw), 'Small', font=imageMeasureFont, fill=(0, 0, 0))
    draw.text((mx + 60 + gridWidth / 2, sy - lw * k_dif - lw/2), 'Large', font=imageMeasureFont, fill=(0, 0, 0))

    iquality = ia['quality']
    idpi = ia['dpi']
    image.save(saveFileName, quality=iquality, dpi=idpi)

def drawCdifDistribution(gids, gdif, c, labels):
    sns.set(style="whitegrid")
    sns.set_context("paper")

    fig, ax = plt.subplots()
    ax.set_ylabel('odif', fontname="Times New Roman", style='italic', fontsize=13)
    ax.set_xlabel('Time', fontname="Times New Roman", fontsize=13)
    x = [i for i in range(5)]
    ls = []
    for i, gid in enumerate(gids):
        l, = ax.plot(x, gdif[gid], 'o--', linewidth = 2, color = c[i], label = labels[i])
        ls.append(l)


    ax.set_ylim(0, 0.4)
    ys = [0, 0.1, 0.2, 0.3, 0.4]
    ax.set_yticks(ys)
    ylabels = [str(abs(item)) for item in ys]
    ax.yaxis.set_ticklabels(ylabels, fontname="Times New Roman", fontsize=12)


    ax.set_xlim(0, 4)
    xs = [i for i in range(0, 5)]
    ax.set_xticks(xs)
    xlabels = ['1-5 a.m.', '9 a.m.-1 p.m.', '1-5 p.m.', '5-9 p.m.', '9 p.m.-1 a.m.']
    ax.xaxis.set_ticklabels(xlabels, fontname="Times New Roman", fontsize=12)


    leg = plt.legend(handles=ls, loc=0)
    for l in leg.get_texts():
        l.set_fontsize(12)
        l.set_fontname("Times New Roman")

    plt.show()

def userScore():
    sns.set(style="whitegrid")

    x = [i for i in range(1, 4)]
    '''
    oyIM = [[3,2,1,2,1,2,3,4,1,4,0,2,3,2,1,3,3,3,2,4], [3,4,1,1,1,2,3,3,1,2,0,2,3,1,1,3,3,2,2,3], [1,0,2,1,3,0,1,2,3,3],
           [4,2,1,2,2,2,2,3,5,2,2,0,3,1,1,0,2,2,1,3], [3,3,3,3,2,1,2,5,3,2,0,0,0,0,0,2,4,3,3,5],
           [0,1,0,0,0,0,0,0,0,0,0,3,2,1,0,1,0,0,0,0], [1,1,2,2,1,1,1,2,4,5,1,2,1,2,4,1,3,1,1,3]]
    oyFM = [[2,2,0,3,2,4,2,4,3,2,1,1,3,3,3,1,1,2,4,2], [4,4,2,4,2,4,4,5,4,3,3,4,4,3,5,3,3,3,5,3], [4,4,4,3,4,3,4,3,5,4],
           [4,4,2,4,3,3,4,4,5,4,4,4,5,3,5,4,4,4,3,4], [4,1,1,5,2,3,3,4,5,5,3,3,1,1,5,3,1,4,4,3],
           [4,3,2,5,3,3,2,3,3,4,4,2,0,2,5,4,5,3,4,5], [4,2,3,4,3,4,3,4,3,3,3,3,3,3,4,3,2,3,3,5]]
    oyPM = [[5,5,3,5,4,4,4,4,5,3,4,4,5,4,5,5,4,5,5,5], [5,4,3,5,4,4,5,5,4,4,4,4,5,4,4,5,4,4,5,4], [5,5,4,4,5,5,5,4,5,5],
           [5,4,3,5,3,4,3,4,3,3,4,5,5,3,4,4,4,3,5,4], [5,4,2,4,4,5,4,3,1,3,5,3,5,5,3,4,4,2,5,4],
           [5,4,3,5,4,5,4,4,3,3,4,4,4,5,3,5,5,5,5,4], [5,5,4,5,5,5,4,4,2,4,4,4,5,5,3,5,4,5,5,4]]
    
    yIM = []
    yFM = []
    yPM = []

    for i in range(7):
        yIM.append(np.mean(sorted(oyIM[i])[1:-1]))
        yFM.append(np.mean(sorted(oyFM[i])[1:-1]))
        yPM.append(np.mean(sorted(oyPM[i])[1:-1]))

    '''
    yIM = [0.1,0,1,0.1]
    yFM = [0.3,0.8,1.0,0.1]
    yPM = [1,1,1,0.9]
    Q1 = [3/14, 4/14, 14/14]
    Q2 = [0, 11/14, 14/14]
    Q3 = [14/14, 14/14, 14/14]
    Q4 = [1/14, 1/14, 13/14]

    x = np.array(x)
    fs1 = 18
    fs2 = 16

    fig, ax = plt.subplots()
    #ax.set_xlabel('', fontname="Times New Roman", fontsize=fs1)
    ax.set_ylabel('Accuracy', fontname="Times New Roman", fontsize=fs1)

    l1 = ax.bar(x-0.2, Q1, facecolor='#ff2121', width=0.1, label='Q1')
    l2 = ax.bar(x-0.1, Q2, facecolor='#44cef6', width=0.1, label='Q2')
    l3 = ax.bar(x, Q3, facecolor='#00e500', width=0.1, label='Q3')
    l4 = ax.bar(x+0.1, Q4, facecolor='#fff143', width=0.1, label='Q4')


    ax.set_ylim(0, 1)
    ys = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
    ax.set_yticks(ys)
    ylabels = [str(item) for item in ys]
    ax.yaxis.set_ticklabels(ylabels, fontname="Times New Roman", fontsize=fs2)

    ax.set_xlim(0, 4)
    xs = [1, 2, 3]
    ax.set_xticks(xs)
    xlabels = ['The interaction matrix', 'The flow map', 'Our approach']
    ax.xaxis.set_ticklabels(xlabels, fontname="Times New Roman", fontsize=fs2)

    leg = plt.legend(handles=[l1, l2, l3, l4])
    for l in leg.get_texts():
        l.set_fontsize(14)
        l.set_fontname("Times New Roman")
    plt.show()