import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patch
import csv
from matplotlib.lines import Line2D
from scipy.stats import weibull_min
from matplotlib.figure import Figure
import Repair_pb2
import MicroBumpLayout_pb2
from google.protobuf import text_format

# format: key: [groupIdx, color, lineLevels, lineWidth]
shortType = {'None': [-1, 'white', 0, 0],
             'vss-vss': [0, 'chartreuse', 2, 1],
             'vdd-vdd': [1, 'chartreuse', 2, 1],
             'vdd-vss': [2, 'red', 5, 2],
             'vss-signal': [3, 'fuchsia', 0, 0],
             'vdd-signal': [4, 'fuchsia', 0, 0],
             'inter-bundle-signal-signal': [5, 'red', 0, 0],
             'intra-bundle-signal-signal': [6, 'black', 0, 0],
}

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

class Line(object):
    def __init__(self, point1=None, point2=None, linetype=None):
        self.link = (point1, point2)
        self.color = shortType[linetype][1] if shortType[linetype] else 'white'
        self.level = shortType[linetype][2] if shortType[linetype] else 0
        self.width = shortType[linetype][3] if shortType[linetype] else 0
        self.type = linetype

    def sef_line(self, left=None, right=None):
        self.link = (left, right)

class Repair_group(object):
    def __init__(self):
        self.bumps = []

class IArray:
    def __init__(self):
        self.marray = []
        self.larray = []
        self.rarray = []
        self.ArraySize = None
        self.ux = None
        self.uy = None
        self.anchorVector = None
        self.protomarray = None
        self.protorepair = None
        self.rlist = []
        self.ax = None
        self.faultyText = []
        self.sigText = []
        self.phybumpText = []
        self.phy2Fn = []
        self.faulty_bump = []

    def construct_mmap(self):
        if self.protomarray:
            r = []
            c = []
            p = []
            self.marray = []
            for item in self.protomarray.MicroBump:
                r.append(int(item.row))
                c.append(int(item.col))
                p.append((int(item.row), int(item.col)))

            mr, mc = max(r)+1, max(c)+1
            self.ArraySize = (mr, mc)

            for i in range(mr):
                tmp = []
                self.marray.append(tmp)
                for j in range(mc):
                    indices = [index for index, item in enumerate(p) if item == (i, j)]
                    if len(indices) == 0:
                        self.marray[i].append(None)
                    else:
                        self.marray[i].append(self.protomarray.MicroBump[indices[0]])
            self.ux = abs(self.marray[0][1].x-self.marray[0][0].x)
            self.uy = abs(self.marray[1][0].y-self.marray[0][0].y)
            self.anchorVector = ((self.marray[0][1].x-self.marray[0][0].x), (self.marray[0][1].y-self.marray[0][0].y))
        else:
            raise Exception("Constructing mmap fail...")

    def clean_mmap(self):
        self.marray.clear()

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
        elif bump1.type == 0 or bump2.type == 0:
            line = Line(point1=bump1, point2=bump2, linetype='vss-signal')
        #Power-to-signal
        elif bump1.type == 1 or bump2.type == 1:
            line = Line(point1=bump1, point2=bump2, linetype='vdd-signal')
        #Inter-bundle signal-to-signal
        elif bump1.bundle != bump2.bundle:
            line = Line(point1=bump1, point2=bump2, linetype='inter-bundle-signal-signal')
        #Intra-bundle signal-to-signal
        else:
            line = Line(point1=bump1, point2=bump2, linetype='intra-bundle-signal-signal')
        return line

    def check_is_line(self, bump1, bump2):
        return [item for i, item in enumerate(self.larray) if (item.link == (bump1, bump2) or item.link == (bump2, bump1))]

    def search_Lines_by_Bump(self, bump):
        return [item for i, item in enumerate(self.larray) if [j for j in item.link if (j == bump)]]

    def createLinesByBump(self, bump):
        if bump != None:
            tr, tc = int(bump.row), int(bump.col)
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

    def clean_lmap(self):
        self.larray.clear()

    def construct_lmap(self):
        for bump in self.protomarray.MicroBump:
            self.createLinesByBump(bump)
        print("Constructed lines: ", len(self.larray))

    def dump_all_lines(self, filename):
        return

    '''
    def construct_rmap_v3(self):
        if self.protomarray:
            self.rarray.clear()
            self.rlist.clear()
            for group in self.protorepair.RepairGroup:
                repairroutes = []
                if len(group.Route) != group.RouteCount:
                    raise Exception("Constructing rmap fail ... Description file does not match.")
                for route in group.Route:
                    fromBump = self.search_Bump_by_name( str(route.From) )
                    toBump = self.search_Bump_by_name( str(route.To) )
                    if len(fromBump) != 1 or len(toBump) != 1:
                        print("Cannot find bumps by name. From: "+str(route.From)+", To: "+str(route.To))
                        continue
                    repairroutes.append([fromBump[0], toBump[0]])
                if len(repairroutes) != group.RouteCount:
                    raise Exception("Constructing rmap fail ...")
                bumplist = []
                for phy in group.Phy:
                    bump = self.search_Bump_by_name( str(phy) )
                    if len(bump) != 1:
                        print("Cannot find bumps by name. Phy: "+str(phy))
                        continue
                    bumplist.append(bump[0])
                for spare in group.Spare:
                    bump = self.search_Bump_by_name(str(spare))
                    if len(bump) != 1:
                        print("Cannot find bumps by name. Phy: "+str(spare))
                        continue
                    bumplist.append(bump[0])
                self.rarray.append(repairroutes)
                self.rlist.append(bumplist)
            #print("repair groups: ", len(self.rarray))
        else:
            raise Exception("Constructing rmap fail ...")
    '''
    def contruct_bmap_vEJ(self):
        if self.protomarray and self.protorepair:
            for fnintrnt in self.protorepair.FnInterconnects:
                phylane = self.search_Bump_by_name(fnintrnt.PhyInterconnect.TX) + self.search_Bump_by_name(signal.default.From)
                if len(phylane) != 1:
                    print("Cannot find bumps by name. Phy: " + str(phylane))
                    continue
    def construct_rmap_vEJ(self):
        if self.protomarray and self.protorepair:
            for group in self.protorepair.Repairgroup:
                for logics in [group.TXRepairLogic, group.RXRepairLogic]:
                    for logic in logics:
                        for signal in logic.signal:
                            #fnsignal = MicroBumpLayout_pb2.Fnsignals()
                            #fnsignal.name = signal.port
                            #for control in signal.default.control:
                            #    fncntrl = fnsignal.cntrls()
                            #    fncntrl.mux = control.adapter
                            #    fncntrl.sel = control.Sel
                            #    fnsignal.mode.append(fncntrl)
                            phylane = self.search_Bump_by_name(signal.default.To) + self.search_Bump_by_name(signal.default.From)
                            if len(phylane) != 1:
                                print("Cannot find bumps by name. Phy: " + str(phylane))
                                continue
                            #phylane[0].current.append(fnsignal)
                            phylane[0].signal.append(signal)
                            #for repair in signal.repair:
                            #    fnsignal = MicroBumpLayout_pb2.Fnsignals()
                            #    fnsignal.name = signal.port
                            #    for control in repair.control:
                            #        fncntrl = fnsignal.cntrls()
                            #        fncntrl.mux = control.adapter
                            #        fncntrl.sel = control.Sel
                            #        fnsignal.mode.append(fncntrl)
                            #    phylane = self.search_Bump_by_name(repair.To) + self.search_Bump_by_name(repair.From)
                            #    if len(phylane) != 1:
                            #        print("Cannot find bumps by name. Phy: " + str(phylane))
                            #        continue
                            #    phylane[0].repair.append(fnsignal)
            #print(self.protomarray)
        else:
            raise Exception("Constructing rmap fail ...")

    def search_Bump_by_name(self, name):
        return [item for i, item in enumerate(self.protomarray.MicroBump) if item.name == name]
    def clean_rmap_vEJ(self):
        for bump in self.protomarray.MicroBump:
            while bump.current:
                bump.current.pop()
            while bump.repair:
                bump.repair.pop()