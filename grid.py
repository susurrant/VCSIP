# -*- coding: utf-8 -*-：

import numpy as np

class Grid(object):
    def __init__(self, gid, dnum):
        # 格网ID
        self.gid = gid
        # 关联的流集合
        self.outFlow = []
        self.inFlow = []

        self.wm = [0]*dnum
        self.wd = [0]*dnum

    def addOutFlow(self, fid):
        self.outFlow.append(fid)

    def addInFlow(self, fid):
        self.inFlow.append(fid)

    def calcOutAggregation(self, flows):
        for fid in self.outFlow:
            td, ta = calcInteraction(flows[fid])
            tm = 1
            idx, tw = calcMD(ta, len(self.wm))
            self.wm[idx] += tm
            self.wd[idx] += tm * td

        for i in range(len(self.wm)):
            if self.wm[i] != 0:
                self.wd[i] /= self.wm[i]

# compute main interaction direction
def calcMD(a, n):
    d = np.array([i*2*np.pi/n for i in range(n)]) + np.pi/n
    w = np.cos(d-a)
    idx = np.where(w==np.max(w))[0][0]
    return idx, w[idx]

def calcInteraction(flow):
    dx = flow[1][0]-flow[0][0]
    dy = flow[1][1]-flow[0][1]
    d = np.sqrt(dy**2+dx**2)
    a = abs(np.arcsin(dy/d))
    if dx>0:
        if dy<0:
            a = 2*np.pi - a
        elif dy==0:
            a = 0
    elif dx<0:
        if dy>0:
            a = np.pi - a
        elif dy<0:
            a += np.pi
        else:
            a = np.pi
    else:
        if dy>0:
            a = 0.5*np.pi
        elif dy<0:
            a = 1.5*np.pi
        else:
            a = -1

    return d/1000.0, a  #距离单位以km计算