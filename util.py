import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patch
import csv
from matplotlib.lines import Line2D

colorBoard2 = {-1: 'white',
              0: 'black',
              1: 'cornflowerblue',
              2: 'orange',
              3: 'cyan',
              4: 'lawngreen',
              5: 'blue',
              6: 'navy',
              7: 'purple',
              8: 'maroon',
              9: 'yellow',
              10: 'olive',
              11: 'lightseagreen',
              12: 'aquamarine',
              13: 'rebeccapurple',
              14: 'crimson'
              }

colorBoard = {-1: 'white',
              0: 'black',
              1: 'royalblue',
              2: 'red',
              3: 'hotpink',
              4: 'limegreen',
              5: 'blue',
              6: 'navy',
              7: 'purple',
              8: 'maroon',
              9: 'yellow',
              10: 'olive',
              11: 'lightseagreen',
              12: 'aquamarine',
              13: 'rebeccapurple',
              14: 'crimson'
              }

bumpType = {0: 'Vss',
            1: 'Vdd',
            2: 'Function',
            3: 'Spare'
            }

class Bump(object):
    def __init__(self, name='', id=0, row=-1, col=-1, x=-1.0, y=-1.0, size=0., bundle=0, color=0, type=2):
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

        self.sizeScaler = 1.0


    def __getitem__(self, idx=0):
        return self
    #    return [self.row, self.col, self.x, self.y, self.size, self.bundle, self.color, self.type]

class IArray:
    def __init__(self):
        self.bump = []
        self.fig = None
        self.ax = None
        self.length = 0
        self.idx = 0
        self.bx = []
        self.by = []
        self.array = None
        self.adjacent = None
        self.ux = None
        self.uy = None
        self.anchorVector = None

        # I-Array parameters
        self.ArraySize = None
        self.counting = []
        self.bcounting = []
        for i in range(7):
            self.counting.append(0)
            self.bcounting.append(0)

    def __iter__(self):
        return self

    def __next__(self):
        self.idx += 1
        if self.idx > self.length:
            self.idx = 0
            raise StopIteration
        else:
            return self.bump[self.idx-1].__getitem__()

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
                             size=float(element[4]), bundle=int(element[5]), color=int(element[6]), type=int(element[7])))
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

    def construct_imap(self):
        if self.bump:
            r = []
            c = []
            p = []
            self.array = []
            for item in self:
                r.append(int(item.row))
                c.append(int(item.col))
                p.append((int(item.row), int(item.col)))

            mr, mc = max(r)+1, max(c)+1
            self.ArraySize = (mr, mc)
            #print("self.ArraySize:", self.ArraySize)

            for i in range(mr):
                tmp = []
                self.array.append(tmp)
                for j in range(mc):
                    indices = [index for index, item in enumerate(p) if item == (i, j)]
                    if len(indices) == 0:
                        self.array[i].append(None)
                    else:
                        self.array[i].append(self.bump[indices[0]])
            self.ux = abs(self.array[0][1].x-self.array[0][0].x)
            self.uy = abs(self.array[1][0].y-self.array[0][0].y)
            self.anchorVector = ((self.array[0][1].x-self.array[0][0].x), (self.array[0][1].y-self.array[0][0].y))
            return self.array
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
        cid = self.fig.canvas.mpl_connect('button_press_event', self.rightclick)
        self.fig.canvas.mpl_connect('key_press_event', self.on_press)
        #self.ax.set_xlim(0, xlim)
        #self.ax.set_ylim(0, ylim)

    def set_XYRatio(self, ratio):
        x_left, x_right = self.ax.get_xlim()
        y_low, y_high = self.ax.get_ylim()
        self.ax.set_aspect(abs((x_right - x_left) / (y_low - y_high)) * ratio)

    def cleanLines(self):
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
            #print(len(self.ax.lines))
            self.cleanLines()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
        elif event.key == 'a':
            print(len(self.array))
            GroundNum = 0
            PowerNum = 0
            SignalNum = 0
            for i in range(len(self.array)):
                for j in range(len(self.array[i])):
                    if self.array[i][j] != None:
                        self.drawShorts((i, j))
                        if self.array[i][j].type == 0:
                            GroundNum += 1
                        elif self.array[i][j].type == 1:
                            PowerNum += 1
                        else:
                            SignalNum += 1
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.ax.autoscale_view()
            print("Ground-to-ground:", self.counting[0]/2)
            print("Power-to-power:", self.counting[1]/2)
            print("Power-to-ground:", self.counting[2]/2)
            print("Power-to-signal:", self.counting[3]/2)
            print("Inter-bundle signal-to-signal:", self.counting[4]/2)
            print("Intra-bundle signal-to-signal:", self.counting[5]/2)
            print("----------------------------------")
            print("Bundle 1~40 power-to-signal:", (self.counting[3]/2 - self.bcounting[3]/2))
            print("Bundle 1~40 inter-bundle signal-to-signal:", (self.counting[4]/2 - self.bcounting[4]/2))
            print("Bundle 1~40 intra-bundle signal-to-signal:", (self.counting[5]/2 - self.bcounting[5]/2))
            print("----------------------------------")
            print("Bundle 41 power-to-signal:", self.bcounting[3]/2)
            print("Bundle 41 inter-bundle signal-to-signal:", self.bcounting[4]/2)
            print("Bundle 41 intra-bundle signal-to-signal:", self.bcounting[5]/2)

            print("----------------------------------")
            print("----------------------------------")
            print("----------------------------------")
            print("VSS-VCC shorts:", self.counting[2] / 2)
            print("VSS-VSS shorts:", self.counting[0] / 2)
            print("VCC-VCC shorts:", self.counting[1] / 2)
            print("VSS-signal shorts:", self.counting[3] / 2)
            print("VSS-signal shorts:", self.counting[6] / 2)
            print("Signal-to-signal:", (self.counting[4]+self.counting[5]) / 2)
            print("----------------------------------")
            print("VCC opens:", PowerNum)
            print("VSS opens:", GroundNum)
            print("Signal opens:", SignalNum)

        elif event.key == '+' or event.key == '-':
            for item in self:
                if event.key == '+':
                    item.sizeScaler += 0.04
                else:
                    item.sizeScaler -= 0.04
            self.cleanBumps()
            self.plot()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.ax.autoscale_view()
        elif event.key == 'r':
            for item in self:
                item.sizeScaler = 1.0
            self.cleanLines()
            self.cleanBumps()
            self.plot()
            self.fig.canvas.draw()
            self.fig.canvas.flush_events()
            self.ax.autoscale_view()
            for i in range(6):
                self.counting[i] = 0
                self.bcounting[i] = 0

    def rightclick(self, event):
        #print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
        #      ('double' if event.dblclick else 'single', event.button,
        #       event.x, event.y, event.xdata, event.ydata))
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
                self.drawShorts((tr, tc))
                self.fig.canvas.draw()
                self.fig.canvas.flush_events()
                self.ax.autoscale_view()

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
                if type == 'Function':
                    #edgecolor = colorBoard[item.bundle%15]
                    #facecolor = colorBoard[item.color+1]
                    edgecolor = 'black'
                    facecolor = colorBoard[item.bundle%15]
                elif type == 'Spare':
                    edgecolor = 'black'
                    facecolor = colorBoard[item.bundle%15]
                    #facecolor = colorBoard[item.color+1]
                elif type == 'Vdd':
                    edgecolor = 'red'
                    facecolor = 'white'
                    textPlus.append(xy)
                elif type == 'Vss':
                    edgecolor = 'black'
                    facecolor = 'white'
                    textMinus.append(xy)
                else:
                    edgecolor = colorBoard[-1]
                    facecolor = colorBoard[-1]
                #edgecolor = 'black'
                #facecolor = 'white'
                self.ax.add_patch(plt.Circle(xy=xy, radius=size*scaler*150.0,
                                             edgecolor=edgecolor, facecolor=facecolor,
                                             linewidth=1, zorder=10))
                x.append(float(item.x))
                y.append(float(item.y))
            self.ax.scatter(x, y, s=0, marker='o')
            for item in textPlus:
                tx, ty = item
                #plt.text(tx-5, ty-4, '+', fontsize=14, zorder=11)
                plt.text(tx - 5, ty - 4, '+', fontsize=8, zorder=11)
            for item in textMinus:
                tx, ty = item
                plt.text(tx-3, ty-5, '-', fontsize=10, zorder=11)
                #plt.text(tx - 3, ty - 5, '-', fontsize=18, zorder=11)
        else:
            raise Exception('Array is empty!!')

    def createLines(self, point1, point2):
        r1, c1 = point1
        r2, c2 = point2
        bump1 = self.array[r1][c1]
        bump2 = self.array[r2][c2]
        linewidth = 0.5
        zorder = 1.0
        #Ground-to-gound
        if bump1.type == 0 and bump2.type == 0:
            color = 'chartreuse'
            #color = 'white'
            linewidth += 1
            zorder = 2
            self.counting[0] += 1
        #Power-to-power
        elif bump1.type == 1 and bump2.type == 1:
            color = 'chartreuse'
            #color = 'white'
            linewidth += 1
            zorder = 2
            self.counting[1] += 1
        #Power-to-ground
        elif bump1.type < 2 and bump2.type < 2 and bump1.type != bump2.type:
            color = 'red'
            #color = 'white'
            linewidth += 2
            zorder = 5
            self.counting[2] += 1
        #Ground-to-signal
        elif bump1.type == 0 or bump2.type == 0:
            color = 'fuchsia'
            #color = 'white'
            self.counting[3] += 1
            zorder = 0
            if bump1.bundle == 41 or bump2.bundle == 41:
                self.bcounting[3] += 1
        #Power-to-signal
        elif bump1.type == 1 or bump2.type == 1:
            color = 'fuchsia'
            #color = 'white'
            self.counting[6] += 1
            zorder = 0
            if bump1.bundle == 41 or bump2.bundle == 41:
                self.bcounting[6] += 1
        #Inter-bundle signal-to-signal
        elif bump1.bundle != bump2.bundle:
            color = 'red'
            color = 'black'
            linewidth += 0
            zorder = 0
            self.counting[4] += 1
            if bump1.bundle == 41 or bump2.bundle == 41:
                self.bcounting[4] += 1
        #Intra-bundle signal-to-signal
        else:
            color = 'black'
            #color = 'white'
            zorder = 0
            self.counting[5] += 1
            if bump1.bundle == 41 and bump2.bundle == 41:
                self.bcounting[5] += 1
            elif bump1.bundle == 41 or bump2.bundle == 41:
                print("Something is wrong!!")
        line = Line2D([bump1.x, bump2.x],
                      [bump1.y, bump2.y], color=color, linewidth=linewidth, zorder=zorder)
        self.ax.add_line(line)

    def drawShorts(self, location):
        tr, tc = location
        mr, mc = self.ArraySize
        ax, ay = self.anchorVector
        # Upper line
        if tr + 1 < mr and self.array[tr + 1][tc] != None:
            #print("Draw upper line")
            self.createLines((tr + 1, tc), (tr, tc))
        # Bottom line
        if tr - 1 >= 0 and self.array[tr - 1][tc] != None:
            #print("Draw Bottom line")
            self.createLines((tr - 1, tc), (tr, tc))
        if tc + 2 < mc and self.array[tr][tc + 2] != None:
            #print("Draw Bottom line")
            self.createLines((tr, tc + 2), (tr, tc))
        # Left-most
        if tc - 2 >= 0 and self.array[tr][tc - 2] != None:
            #print("Draw Bottom line")
            self.createLines((tr, tc - 2), (tr, tc))
        # Right-upper line
        if tr + 1 < mr and tc + 1 < mc and self.array[tr + 1][tc + 1] != None:
            #print("Draw right-upper line")
            self.createLines((tr + 1, tc + 1), (tr, tc))
        # Right-top line
        if tr < mr and tc + 1 < mc and self.array[tr][tc + 1] != None:
            #print("Draw right line")
            self.createLines((tr, tc + 1), (tr, tc))
        # Right-lower line
        if tr - 1 >= 0 and tc + 1 < mc and self.array[tr - 1][tc + 1] != None:
            #print("Draw right-lower line")
            self.createLines((tr - 1, tc + 1), (tr, tc))

        # Left-upper line
        if tr + 1 < mr and tc - 1 >= 0 and self.array[tr + 1][tc - 1] != None:
            #print("Draw left-upper line")
            self.createLines((tr + 1, tc - 1), (tr, tc))
        # left-top line
        if tr < mr and tc - 1 >= 0 and self.array[tr][tc - 1] != None:
            #print("Draw left line")
            self.createLines((tr, tc - 1), (tr, tc))
        # left-lower line
        if tr - 1 >= 0 and tc - 1 >= 0 and self.array[tr - 1][tc - 1] != None:
            #print("Draw left-lower line:")
            self.createLines((tr - 1, tc - 1), (tr, tc))

        if ay < 0:
            factor = 0
        else:
            factor = 1

        if ((tc+factor) % 2) == 0:
            # Right-top line
            if tr + 2 < mr and tc + 1 < mc and self.array[tr + 2][tc + 1] != None:
                #print("Draw right-top line")
                self.createLines((tr + 2, tc + 1), (tr, tc))
            # Left-upper line
            if tr + 2 < mr and tc - 1 >= 0 and self.array[tr + 2][tc - 1] != None:
                #print("Draw left-upper line")
                self.createLines((tr + 2, tc - 1), (tr, tc))
        else:
            # Right-bottom line
            if tr - 2 >= 0 and tc + 1 < mc and self.array[tr - 2][tc + 1] != None:
                #print("Draw Right-bottom line")
                self.createLines((tr - 2, tc + 1), (tr, tc))
            # left-lower line
            if tr - 2 >= 0 and tc - 1 >= 0 and self.array[tr - 2][tc - 1] != None:
                #print("Draw left-lower line:")
                self.createLines((tr - 2, tc - 1), (tr, tc))
