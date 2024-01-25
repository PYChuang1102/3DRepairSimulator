import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patch
import csv
from matplotlib.lines import Line2D
import matplotlib.ticker as ticker
from scipy.stats import weibull_min

colorBoard = {-1: 'white',
              0: 'black',
              1: 'gray',
              2: 'hotpink',
              3: 'royalblue',   #rxdata 0-31
              4: 'maroon',
              5: 'silver',
              6: 'olive',
              7: 'lightgreen',
              8: 'orange',        # txdata 32-63
              9: 'darkorchid',
              10: 'tomato',
              11: 'aqua',
              12: 'paleturquoise', #rxdata 32-63
              13: 'khaki', # txdata 0-31
              14: 'darkorange'
              }

bumpType = {0: 'Vss',
            1: 'Vdd',
            2: 'Function',
            3: 'Spare',
}

# format: key: [groupIdx, color, lineLevels, lineWidth]
# color rule:
# chartreuse:   -0,         do not need repair
# red:                      dead
# fuchsia:      -1/bundle,  need repair
# orange:       -1/bundle,  do not need repair
# blue:         -2,         do not need repair
# black:        -2,         need repair


# for checking how many spare we lose
shortType = {'None': [-1, 'white', 0, 0],
             'vss-vss': [0, 'chartreuse', 2, 1],
             'vdd-vdd': [1, 'chartreuse', 2, 1],
             'vdd-vss': [2, 'red', 5, 1.5],
             'vss-signal': [3, 'fuchsia', 0, 0],
             'vdd-signal': [4, 'fuchsia', 0, 0],
             'inter-bundle-signal-signal': [5, 'black', 0, 0],
             'intra-bundle-signal-signal': [6, 'black', 0, 0],

             'vss-spare': [7, 'fuchsia', 0, 0],
             'vdd-spare': [8, 'fuchsia', 0, 0],

             'intra-bundle-signal-spare-allow-short': [9, 'fuchsia', 0, 0],
             'intra-bundle-signal-spare-not-allow-short': [10, 'black', 0, 0],
             'inter-bundle-signal-spare': [11, 'black', 0, 0],

             'intra-bundle-spare-spare': [12, 'black', 0, 0],
             'inter-bundle-spare-spare': [13, 'black', 0, 0],

             'trk-clk-signal-spare':[14, 'fuchsia', 0, 0]

             }

'''
# for checking required number of repaired spares / drawing short lines
shortType = {'None': [-1, 'white', 0, 0],
             'vss-vss': [0, 'chartreuse', 2, 1],
             'vdd-vdd': [1, 'chartreuse', 2, 1],
             'vdd-vss': [2, 'red', 5, 2],
             'vss-signal': [3, 'fuchsia', 0, 0],
             'vdd-signal': [4, 'fuchsia', 0, 0],
             'inter-bundle-signal-signal': [5, 'black', 0, 0],
             'intra-bundle-signal-signal': [6, 'black', 0, 0],

             'vss-spare': [7, 'chartreuse', 1, 1],
             'vdd-spare': [8, 'chartreuse', 1, 1],

             'intra-bundle-signal-spare-allow-short': [9, 'chartreuse', 2, 1],
             'intra-bundle-signal-spare-not-allow-short': [10, 'fuchsia', 0, 0],
             'inter-bundle-signal-spare': [11, 'fuchsia', 0, 0],

             'intra-bundle-spare-spare': [12, 'chartreuse', 0, 0],
             'inter-bundle-spare-spare': [13, 'chartreuse', 0, 1],

             'trk-clk-signal-spare':[14, 'fuchsia', 0, 1]

             }
'''
'''
# for calculating yield (repair rate)
# use this when running DefectCalculation_v2.py
shortType = {'None': [-1, 'white', 0, 0],
             'vss-vss': [0, 'chartreuse', 2, 1],
             'vdd-vdd': [1, 'chartreuse', 2, 1],
             'vdd-vss': [2, 'red', 5, 2],
             'vss-signal': [3, 'black', 0, 0],
             'vdd-signal': [4, 'black', 0, 0],
             'inter-bundle-signal-signal': [5, 'black', 0, 0],
             'intra-bundle-signal-signal': [6, 'black', 0, 0],

             'vss-spare': [7, 'blue', 1, 1],
             'vdd-spare': [8, 'blue', 1, 1],

             'intra-bundle-signal-spare-allow-short': [9, 'orange', 2, 1],
             'intra-bundle-signal-spare-not-allow-short': [10, 'black', 0, 0],
             'inter-bundle-signal-spare': [11, 'black', 0, 0],

             'intra-bundle-spare-spare': [12, 'blue', 0, 0],
             'inter-bundle-spare-spare': [13, 'blue', 0, 1],

             'trk-clk-signal-spare':[14, 'fuchsia', 0, 1]

             }
'''
class ExpoLogarithmic(object):
    def __init__(self):
        return self

    # Define the PDF if the Exponential-Logarithmic distribution
    def pdf(self, x, λ, α):
        return (α * np.exp(-λ * x)) / (1 - np.exp(-λ))

    # Define the CDF of the Exponential-Logarithmic distribution
    def cdf(self, x, λ, α):
        return 1 - np.exp(-λ * x) ** α

class Bump(object):
    def __init__(self, name='', id=0, row=-1, col=-1, x=-1.0, y=-1.0, size=0., bundle=0, color=0, type=2, itemname=''):
        self.name = name
        self.id = id
        self.row = row
        self.col = col
        self.x = x
        self.y = y
        self.size = size
        self.bundle = bundle
        self.color = color
        self.type = type
        self.itemname = itemname

        self.sizeScaler = 1.0

class Line(object):
    def __init__(self, point1=None, point2=None, linetype=None):
        self.link = (point1, point2)
        self.color = shortType[linetype][1] if shortType[linetype] else 'white'
        self.level = shortType[linetype][2] if shortType[linetype] else 0
        self.width = shortType[linetype][3] if shortType[linetype] else 0
        self.type = linetype

    def sef_line(self, left=None, right=None):
        self.link = (left, right)


class IArray:
    def __init__(self):
        self.bump = []
        self.fig = None
        self.ax = None
        self.length = 0
        self.idx = 0
        self.bx = []
        self.by = []
        self.marray = None
        self.adjacent = None
        self.ux = None
        self.uy = None
        self.anchorVector = None
        self.larray = []

        # I-Array parameters
        self.ArraySize = None
        self.counting = []
        self.bcounting = []
        for i in range(7):
            self.counting.append(0)
            self.bcounting.append(0)

        # Error calculation parameters
        self.SingleShortErrorSum = []
        self.SingleShortErrorRate = []
        for i in range(7):
            self.SingleShortErrorSum.append(0)
            self.SingleShortErrorRate.append(0)

        self.SingleOpenErrorSum = []
        self.SingleOpenErrorRate = []
        for i in range(3):
            self.SingleOpenErrorSum.append(0)
            self.SingleOpenErrorRate.append(0)

        self.line_num = [0] * len(self.bump)

    def __iter__(self):
        return self

    def __next__(self):
        self.idx += 1
        if self.idx > self.length:
            self.idx = 0
            raise StopIteration
        else:
            return self.bump[self.idx-1]

    def __getitem__(self, idx=-1):
        if idx < 0 & idx > self.length:
            raise IndexError("list index out of range")
            return None
        else:
            return self.bump[idx].__getitem__()

    def __len__(self):
        if self.length != len(self.bump):
            raise Exception('Length Error!!!')
        else:
            return self.length

    def append(self, bump):
        self.bump.append(bump)
        self.length = len(self.bump)

    def clean_list(self):
        self.bump.clear()
        self.length = 0
        self.idx = 0

    def read_csv(self, filename):
        self.clean_list()
        file = open(filename, "r")
        data = list(csv.reader(file, delimiter=","))
        title = data.pop(0)
        id = 0
        for element in data:
            self.append(Bump(name='', id=id, row=int(element[0]), col=int(element[1]), x=float(element[2]), y=float(element[3]),
                             size=float(element[4]), bundle=int(element[5]), color=int(element[6]), type=int(element[7]), itemname=str(element[8])))
            id+=1
    def createCheckboard(self, n, m):
        list_0_1 = np.array([[0, 1], [1, 0]])
        checkerboard = np.tile(list_0_1, (n // 2, m // 2))
        return checkerboard

    def createHexMask(self, n, m):
        # Create Hexagonal mask
        checkerboard = self.createCheckboard(n+1, m+1)
        mask = checkerboard[1:, 1:]
        _mh, _mw = mask.shape
        mask[_mh // 2, _mw // 2] = 0
        mask[:, 0] = 0
        mask[:, -1] = 0
        mask[_mh // 2, 0] = 1
        mask[_mh // 2, -1] = 1
        #print(mask.shape)
        return mask

    def createRectMask(self, n, m):
        # Create Rectangular mask
        matrix = np.ones([n, m])
        matrix[n // 2, m // 2] = 0
        return matrix

    def conv2d(self, a, f):
        s = f.shape + tuple(np.subtract(a.shape, f.shape) + 1)
        strd = np.lib.stride_tricks.as_strided
        subM = strd(a, shape=s, strides=a.strides * 2)
        return np.einsum('ij,ijkl->kl', f, subM)

    def createLine(self, bump1, bump2):
        #Ground-to-gound
        if bump1.type == 0 and bump2.type == 0:
            line = Line(point1=bump1, point2=bump2, linetype='vss-vss')
        #Power-to-power
        elif bump1.type == 1 and bump2.type == 1:
            line = Line(point1=bump1, point2=bump2, linetype='vdd-vdd')
        #Power-to-ground
        elif bump1.type < 2 and bump2.type < 2 and bump1.type != bump2.type:
            line = Line(point1=bump1, point2=bump2, linetype='vdd-vss')
        #Ground-to-signal
        elif (bump1.type == 0 and bump2.type == 2) or (bump1.type == 2 and bump2.type == 0):
            line = Line(point1=bump1, point2=bump2, linetype='vss-signal')
        #Power-to-signal
        elif (bump1.type == 1 and bump2.type == 2) or (bump1.type == 2 and bump2.type == 1):
            line = Line(point1=bump1, point2=bump2, linetype='vdd-signal')
        #Intra-bundle signal-to-signal
        elif bump1.type == 2 and bump2.type == 2 and bump1.bundle == bump2.bundle:
            line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-signal')
        #Inter-bundle signal-to-signal
        elif bump1.type == 2 and bump2.type == 2 and bump1.bundle != bump2.bundle:
            line = Line(point1=bump1, point2=bump2, linetype='inter-bundle-signal-signal')
        #vss-spare
        elif (bump1.type == 0 and bump2.type == 3) or (bump1.type == 3 and bump2.type == 0):
            line = Line(point1=bump1, point2=bump2, linetype='vss-spare')
        #vdd-spare
        elif (bump1.type == 1 and bump2.type == 3) or (bump1.type == 3 and bump2.type == 1):
            line = Line(point1=bump1, point2=bump2, linetype='vdd-spare')
        #inter-bundle-signal-spare
        elif ((bump1.type == 2 and bump2.type == 3) or (bump1.type == 3 and bump2.type == 2)) and bump1.bundle != bump2.bundle:
            line = Line(point1=bump1, point2=bump2, linetype='inter-bundle-signal-spare')
        #intra-bundle-spare-spare
        elif bump1.type == 3 and bump2.type == 3 and bump1.bundle == bump2.bundle:
            line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-spare-spare')
        #inter-bundle-spare-spare
        elif bump1.type == 3 and bump2.type == 3 and bump1.bundle != bump2.bundle:
            line = Line(point1=bump1, point2=bump2, linetype='inter-bundle-spare-spare')
        else:
            #intra-bundle-signal-spare-allow-short
            if (bump1.itemname == ' rxdata63' and bump2.itemname == ' rxdataRD3') or (bump1.itemname == ' rxdataRD3' and bump2.itemname == ' rxdata63'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            elif (bump1.itemname == ' rxdata32' and bump2.itemname == ' rxdataRD2') or (bump1.itemname == ' rxdataRD2' and bump2.itemname == ' rxdata32'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            elif (bump1.itemname == ' rxdata31' and bump2.itemname == ' rxdataRD1') or (bump1.itemname == ' rxdataRD1' and bump2.itemname == ' rxdata31'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            elif (bump1.itemname == ' rxdata0' and bump2.itemname == ' rxdataRD0') or (bump1.itemname == ' rxdataRD0' and bump2.itemname == ' rxdata0'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')

            elif (bump1.itemname == ' txdata63' and bump2.itemname == ' txdataRD3') or (bump1.itemname == ' txdataRD3' and bump2.itemname == ' txdata63'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            elif (bump1.itemname == ' txdata32' and bump2.itemname == ' txdataRD2') or (bump1.itemname == ' txdataRD2' and bump2.itemname == ' txdata32'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            elif (bump1.itemname == ' txdata31' and bump2.itemname == ' txdataRD1') or (bump1.itemname == ' txdataRD1' and bump2.itemname == ' txdata31'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            elif (bump1.itemname == ' txdata0' and bump2.itemname == ' txdataRD0') or (bump1.itemname == ' txdataRD0' and bump2.itemname == ' txdata0'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')

            elif (bump1.itemname == ' rxcksb' and bump2.itemname == ' rxcksbRD') or (bump1.itemname == ' rxcksbRD' and bump2.itemname == ' rxcksb'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            elif (bump1.itemname == ' rxdatasb' and bump2.itemname == ' rxdatasbRD') or (bump1.itemname == ' rxdatasbRD' and bump2.itemname == ' rxdatasb'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            elif (bump1.itemname == ' rxckn' and bump2.itemname == ' rxckRD') or (bump1.itemname == ' rxckRD' and bump2.itemname == ' rxckn'):
                line = Line(point1=bump1, point2=bump2, linetype='trk-clk-signal-spare')
            elif (bump1.itemname == ' rxckp' and bump2.itemname == ' rxckRD') or (bump1.itemname == ' rxckRD' and bump2.itemname == ' rxckp'):
                line = Line(point1=bump1, point2=bump2, linetype='trk-clk-signal-spare')
            elif (bump1.itemname == ' rxtrk' and bump2.itemname == ' rxckRD') or (bump1.itemname == ' rxckRD' and bump2.itemname == ' rxtrk'):
                line = Line(point1=bump1, point2=bump2, linetype='trk-clk-signal-spare')
            elif (bump1.itemname == ' rxvld' and bump2.itemname == ' rxvldRD') or (bump1.itemname == ' rxvldRD' and bump2.itemname == ' rxvld'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')

            elif (bump1.itemname == ' txcksb' and bump2.itemname == ' txcksbRD') or (bump1.itemname == ' txcksbRD' and bump2.itemname == ' txcksb'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            elif (bump1.itemname == ' txdatasb' and bump2.itemname == ' txdatasbRD') or (bump1.itemname == ' txdatasbRD' and bump2.itemname == ' txdatasb'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            elif (bump1.itemname == ' txckn' and bump2.itemname == ' txckRD') or (bump1.itemname == ' txckRD' and bump2.itemname == ' txckn'):
                line = Line(point1=bump1, point2=bump2, linetype='trk-clk-signal-spare')
            elif (bump1.itemname == ' txckp' and bump2.itemname == ' txckRD') or (bump1.itemname == ' txckRD' and bump2.itemname == ' txckp'):
                line = Line(point1=bump1, point2=bump2, linetype='trk-clk-signal-spare')
            elif (bump1.itemname == ' txtrk' and bump2.itemname == ' txckRD') or (bump1.itemname == ' txckRD' and bump2.itemname == ' txtrk'):
                line = Line(point1=bump1, point2=bump2, linetype='trk-clk-signal-spare')
            elif (bump1.itemname == ' txvld' and bump2.itemname == ' txvldRD') or (bump1.itemname == ' txvldRD' and bump2.itemname == ' txvld'):
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-allow-short')
            #inter-bundle-signal-spare-not-allow-short
            else:
                line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-spare-not-allow-short')
        return line

    def check_is_line(self, bump1, bump2):
        return [item for i, item in enumerate(self.larray) if (item.link == (bump1, bump2) or item.link == (bump2, bump1))]

    def search_Lines_by_Bump(self, bump):
        return [item for i, item in enumerate(self.larray) if [j for j in item.link if (j == bump)]]

    def createLinesByBump(self, bump):
        if bump != None:
            tr, tc = bump.row, bump.col
            mr, mc = self.ArraySize
            ax, ay = self.anchorVector
            # Upper line
            if tr + 1 < mr and self.marray[tr + 1][tc] != None:
                if not self.check_is_line(bump, self.marray[tr + 1][tc]):
                    self.larray.append(self.createLine(bump, self.marray[tr + 1][tc]))
            # Bottom line
            if tr - 1 >= 0 and self.marray[tr - 1][tc] != None:
                if not self.check_is_line(bump, self.marray[tr - 1][tc]):
                    self.larray.append(self.createLine(bump, self.marray[tr - 1][tc]))
            # Left-most
            if tc - 2 >= 0 and self.marray[tr][tc - 2] != None:
                if not self.check_is_line(bump, self.marray[tr][tc - 2]):
                    self.larray.append(self.createLine(bump, self.marray[tr][tc - 2]))
            # Right-upper line
            if tr + 1 < mr and tc + 1 < mc and self.marray[tr + 1][tc + 1] != None:
                if not self.check_is_line(bump, self.marray[tr + 1][tc + 1]):
                    self.larray.append(self.createLine(bump, self.marray[tr + 1][tc + 1]))
            # Right-top line
            if tr < mr and tc + 1 < mc and self.marray[tr][tc + 1] != None:
                if not self.check_is_line(bump, self.marray[tr][tc + 1]):
                    self.larray.append(self.createLine(bump, self.marray[tr][tc + 1]))
            # Right-lower line
            if tr - 1 >= 0 and tc + 1 < mc and self.marray[tr - 1][tc + 1] != None:
                if not self.check_is_line(bump, self.marray[tr - 1][tc + 1]):
                    self.larray.append(self.createLine(bump, self.marray[tr - 1][tc + 1]))
            # Left-upper line
            if tr + 1 < mr and tc - 1 >= 0 and self.marray[tr + 1][tc - 1] != None:
                if not self.check_is_line(bump, self.marray[tr + 1][tc - 1]):
                    self.larray.append(self.createLine(bump, self.marray[tr + 1][tc - 1]))
            # left-top line
            if tr < mr and tc - 1 >= 0 and self.marray[tr][tc - 1] != None:
                if not self.check_is_line(bump, self.marray[tr][tc - 1]):
                    self.larray.append(self.createLine(bump, self.marray[tr][tc - 1]))
            # left-lower line
            if tr - 1 >= 0 and tc - 1 >= 0 and self.marray[tr - 1][tc - 1] != None:
                if not self.check_is_line(bump, self.marray[tr - 1][tc - 1]):
                    self.larray.append(self.createLine(bump, self.marray[tr - 1][tc - 1]))

            # Type 1:
            #     *   *
            #       *
            #     $   *
            #       $
            # Type 2:
            #       *
            #     *   *
            #       $
            #     $   *
            if ay < 0:
                # Type 1
                factor = 0
            else:
                # Type 2
                factor = 1
            if ((tc + factor) % 2) == 0:
                # Right-top line
                if tr + 2 < mr and tc + 1 < mc and self.marray[tr + 2][tc + 1] != None:
                    if not self.check_is_line(bump, self.marray[tr + 2][tc + 1]):
                        self.larray.append(self.createLine(bump, self.marray[tr + 2][tc + 1]))
                # Left-upper line
                if tr + 2 < mr and tc - 1 >= 0 and self.marray[tr + 2][tc - 1] != None:
                    if not self.check_is_line(bump, self.marray[tr + 2][tc - 1]):
                        self.larray.append(self.createLine(bump, self.marray[tr + 2][tc - 1]))
            else:
                # Right-bottom line
                if tr - 2 >= 0 and tc + 1 < mc and self.marray[tr - 2][tc + 1] != None:
                    if not self.check_is_line(bump, self.marray[tr - 2][tc + 1]):
                        self.larray.append(self.createLine(bump, self.marray[tr - 2][tc + 1]))
                # left-lower line
                if tr - 2 >= 0 and tc - 1 >= 0 and self.marray[tr - 2][tc - 1] != None:
                    if not self.check_is_line(bump, self.marray[tr - 2][tc - 1]):
                        self.larray.append(self.createLine(bump, self.marray[tr - 2][tc - 1]))

    def construct_lmap(self):
        for bump in self:
            self.createLinesByBump(bump)

        print("\nTotal number of lines: ", len(self.larray))

        print("\nnumber of Vss: ", sum(1 for bump in self.bump if bump.type == 0))
        print("number of Vdd: ", sum(1 for bump in self.bump if bump.type == 1))
        print("number of function: ", sum(1 for bump in self.bump if bump.type == 2))
        print("number of spare: ", sum(1 for bump in self.bump if bump.type == 3))

        print("\nnumber of red lines: ", sum(1 for line in self.larray if line.color == 'red'))
        print("number of green lines: ", sum(1 for line in self.larray if line.color == 'chartreuse'))
        print("number of blue lines (-2, no repair): ", sum(1 for line in self.larray if line.color == 'blue'))
        print("number of black lines (-2, need repair): ", sum(1 for line in self.larray if line.color == 'black'))
        print("number of orange lines (-1, no repair): ", sum(1 for line in self.larray if line.color == 'orange'))
        print("number of pink lines(-1, need repair): ", sum(1 for line in self.larray if line.color == 'fuchsia'))

        print("\nRequire no repair (Vss-Vss, Vdd-Vdd): ", sum(1 for line in self.larray if (line.type=='vss-vss' or line.type=='vdd-vdd')))
        print("Require no repair (others): ", sum(1 for line in self.larray if (line.type=='intra-bundle-spare-spare' or line.type=='inter-bundle-spare-spare'
                                                                                  or line.type=='vss-spare' or line.type=='vdd-spare'
                                                                                  )))
        print("Require 1 spare: ", sum(1 for line in self.larray if (line.type=='vss-signal' or line.type=='vdd-signal'
                                                                     or line.type=='intra-bundle-signal-spare-allow-short' or line.type=='intra-bundle-signal-spare-not-allow-short'
                                                                     or line.type=='inter-bundle-signal-spare' or line.type=='trk-clk-signal-spare')))
        print("Require 2 spares: ", sum(1 for line in self.larray if (line.type=='inter-bundle-signal-signal' or line.type=='intra-bundle-signal-signal')))
        print("Catastrophic: ", sum(1 for line in self.larray if line.type=='vdd-vss'))
        return self.larray

    def drawing_all_lines(self):
        # Drawing all lines:
        for item in self.larray:
            # for drawing specific colored line, I add the if condition
            # if item.color=='red' or item.color=='chartreuse':
            self.createDrawingLines(item)
        print("Total number of lines: ", len(self.larray))

    def construct_imap(self):
        if self.bump:
            r = []
            c = []
            p = []
            self.marray = []
            for item in self:
                r.append(int(item.row))
                c.append(int(item.col))
                p.append((int(item.row), int(item.col)))

            mr, mc = max(r)+1, max(c)+1
            self.ArraySize = (mr, mc)
            #print("self.ArraySize:", self.ArraySize)

            for i in range(mr):
                tmp = []
                self.marray.append(tmp)
                for j in range(mc):
                    indices = [index for index, item in enumerate(p) if item == (i, j)]
                    if len(indices) == 0:
                        self.marray[i].append(None)
                    else:
                        self.marray[i].append(self.bump[indices[0]])
            self.ux = abs(self.marray[0][1].x-self.marray[0][0].x)
            self.uy = abs(self.marray[1][0].y-self.marray[0][0].y)
            self.anchorVector = ((self.marray[0][1].x-self.marray[0][0].x), (self.marray[0][1].y-self.marray[0][0].y))
            return self.marray
        else:
            raise Exception('No interconnect to construct the array!!')

    def neighborsRectMap(self):
        # Retangular
        arrayR = np.pad(np.ones(self.ArraySize), ((1, 1), (1, 1)), mode='constant', constant_values=(0, 0))
        mask = self.createRectMask(3, 3)
        outputR = self.conv2d(arrayR, mask)
        return outputR

    def neighborsHexaMap(self):
        # Hexagonal
        _mr, _mc = self.ArraySize
        assayH = np.pad(np.ones([_mr*2, _mc]), ((3, 3), (2, 2)), mode='constant', constant_values=(0, 0))
        mask = self.createHexMask(7, 5)
        rst = self.conv2d(assayH, mask)
        rr, rc = rst.shape
        outputH = np.zeros([(rr+1)//2, rc])
        for i in range(rc):
            if i%2 == 0:
                outputH[:, i] = rst[::2, i]
            else:
                outputH[:, i] = rst[1::2, i]
        return outputH

    def create_fig(self, xlim=12, ylim=12):
        self.fig, self.ax = plt.subplots()
        cid = self.fig.canvas.mpl_connect('button_press_event', self.mouseclicks)
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        #self.ax.set_xlim(0, xlim)
        #self.ax.set_ylim(0, ylim)

    def set_XYRatio(self, ratio):
        x_left, x_right = self.ax.get_xlim()
        y_low, y_high = self.ax.get_ylim()
        self.ax.set_aspect(abs((x_right - x_left) / (y_low - y_high)) * ratio)

    def createDrawingLines(self, line):
        basedLineWidth = 0.5
        basedZOrder = 1.0
        #Ground-to-gound
        bump1, bump2 = line.link
        line = Line2D([bump1.x, bump2.x],
                      [bump1.y, bump2.y], color='black', linewidth=basedLineWidth+0, zorder=basedZOrder+line.level)
        self.ax.add_line(line)

    def cleanDrawingLines(self):
        for item in self.ax.lines:
            item.remove()
            del item

    def cleanBumps(self):
        for item in self.ax.patches:
            item.remove()
            del item

    def on_press(self, event):
        print('press', event.key)
        if event.key == 'd':
            self.cleanDrawingLines()
        elif event.key == 'a':
            self.drawing_all_lines()
            plt.savefig('51-55.png', dpi=1000)
        elif event.key == '+' or event.key == '-':
            for item in self:
                if event.key == '+':
                    item.sizeScaler += 0.04
                else:
                    item.sizeScaler -= 0.04
            self.cleanBumps()
            self.plot()
        elif event.key == 'r':
            for item in self:
                item.sizeScaler = 1.0
            self.cleanDrawingLines()
            self.cleanBumps()
            self.plot()
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()
        self.ax.autoscale_view()

    def mouseclicks(self, event):
        if event.dblclick:
            tc = ((event.xdata + self.ux / 2) // self.ux).astype(int)
            ax, ay = self.anchorVector
            mr, mc = self.ArraySize
            yoffset = 0
            if ay < 0 and (tc % 2) == 0:
                yoffset = self.uy / 2
            elif ay > 0 and (tc % 2) == 1:
                yoffset = self.uy / 2
            else:
                yoffset = 0
            tr = ((event.ydata + self.uy / 2 - yoffset) // self.uy).astype(int)
            print("row: %d, col: %d" % (tr, tc))
            if tr >= 0 and tr < mr and tc >= 0 and tc < mc:
                linelist = self.search_Lines_by_Bump(self.marray[tr][tc])
                for line in linelist:
                   self.createDrawingLines(line)
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                self.ax.autoscale_view()

    def calculate_line_num(self):
        self.line_num = [0]*len(self)
        #print("len of line_num: ", len(self.line_num))
        for line in self.larray:
            bump1, bump2 = line.link
            self.line_num[bump1.id]+=1
            self.line_num[bump2.id]+=1
        #print(self.line_num)

    def plot(self):
        if self.bump:
            x = []
            y = []
            textPlus = []
            textMinus = []
            for item in self:
                xy = (item.x, item.y)
                size = item.size
                scaler = item.sizeScaler
                type = bumpType[int(item.type)]
                if type == 'Spare':
                    edgecolor = 'black'
                    facecolor = colorBoard[item.bundle%15]
                    #edgecolor = colorBoard[item.bundle % 15]
                    #edgecolor = 'orange'
                    linewidth=1
                    xy = (item.x-size * scaler * 125.0, item.y-size * scaler * 125.0)
                    #self.ax.add_patch(plt.Rectangle(xy=xy, width=size * scaler * 250.0, height=size * scaler * 250.0,
                    #                             edgecolor=edgecolor, facecolor=facecolor,
                    #                             linewidth=linewidth, zorder=10))
                    self.ax.add_patch(plt.Polygon([[item.x-size * scaler * 150.0, item.y-size * scaler * 150.0],[item.x+size * scaler * 150.0, item.y-size * scaler * 150.0],[item.x, item.y+size * scaler * 150.0]],
                                                    edgecolor=edgecolor, facecolor=facecolor,
                                                   linewidth=linewidth, zorder=10))

                else:
                    if type == 'Function':
                        #edgecolor = colorBoard[item.bundle%15]
                        #facecolor = colorBoard[item.color+1]
                        edgecolor = 'black'
                        facecolor = colorBoard[item.bundle%15]
                        linewidth=1

                    elif type == 'Vdd':
                        edgecolor = 'red'
                        facecolor = 'white'
                        textPlus.append(xy)
                        linewidth=1
                    elif type == 'Vss':
                        edgecolor = 'black'
                        facecolor = 'white'
                        textMinus.append(xy)
                        linewidth=1
                    else:
                        edgecolor = colorBoard[-1]
                        facecolor = colorBoard[-1]
                    #edgecolor = 'black'
                    #facecolor = 'white'
                    #if type =='Vss' or type=='Vdd':
                    self.ax.add_patch(plt.Circle(xy=xy, radius=size*scaler*150.0,
                                                 edgecolor=edgecolor, facecolor=facecolor,
                                                 linewidth=linewidth, zorder=10))
                self.calculate_line_num()
                line_num = str(12-self.line_num[item.id])
                # plt.text(item.x - 3, item.y - 5, line_num, fontsize=size*scaler*100.0, zorder=12)
                x.append(float(item.x))
                y.append(float(item.y))
            self.ax.scatter(x, y, s=0, marker='o')
            fmt_x = ticker.FuncFormatter(lambda x, _: int(x / 22))
            fmt_y = ticker.FuncFormatter(lambda y, _: int(y / 25 *2/2))
            self.ax.xaxis.set_major_formatter(fmt_x)
            self.ax.yaxis.set_major_formatter(fmt_y)
            self.ax.xaxis.set_tick_params(labelsize=10*0.8)
            self.ax.yaxis.set_tick_params(labelsize=10*0.8)
            plt.xticks(np.arange(0,16*22,2*22))
            #plt.rcParams["figure.figsize"] = (5,40)
            '''
            max_x = max(x)
            min_x = min(x)
            width = max_x - min_x

            # Set the width of the figure to match the width of the array
            self.ax.set_xlim(min_x - 5, max_x + 5)
            '''
            for item in textPlus:
                tx, ty = item
                #plt.text(tx-5, ty-4, '+', fontsize=14, zorder=11)
                plt.text(tx - 5, ty - 4, '+', fontsize=9, zorder=11)
            for item in textMinus:
                tx, ty = item
                plt.text(tx-3, ty-5, '-', fontsize=11, zorder=11)
                #plt.text(tx - 3, ty - 5, '-', fontsize=18, zorder=11)
            self.fig.set_size_inches(5.00,9.0)
        else:
            raise Exception('Array is empty!!')