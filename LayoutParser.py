import os
import csv
import re
import math
import Repair_pb2
import MicroBumpLayout_pb2
from google.protobuf import text_format

channels = {
    "VSS": 0, "vss": 0, "gnd": 0, "vssio": 0,                   #Physical Lane for Ground
    "VDD": 1, "vdd": 1, "vcc": 1, "vccio": 1, "vccfwdio": 1,    #Physical Lane for Power
    "RCK_P": 2, "RXCLP": 2, "rxckp": 2,                         #Physical Lane for Clock Receiver Phase-1
    "RCKN_N": 3, "RXCKN": 3, "rxckn": 3,                        #Physical Lane for Clock Receiver Phase-2
    "RRDCK_P": 4, "RXCKRD": 4, "rxckRD": 4,                     #Physical Lane for redundant Clock/Track Receiver
    "RTRK_P": 5, "RXTRK": 5, "rxtrk": 5,                        #Physical Lane for Track Receiver
    "RD_P": 6, "RD_PN": 6, "RXDATA": 6, "rxdata": 6,            #Physical Lane for Data Receiver
    "RRD_P": 7, "RRD_PN": 7, "RXDATARD": 7, "rxdataRD": 7,      #Physical Lane for redundant Data Receiver
    "RVLD_P": 8, "RXVLD": 8, "rxvld": 8,                        #Physical Lane for Valid Receiver
    "RRDVLD_P": 9, "RXVLDRD": 9, "rxvldRD": 9,                  #Physical Lane for redundant Valid Receiver
    "RXDATASB": 10, "rxdatasb": 10,                             #Physical Lane for sideband Data Receiver
    "RXCKSB": 11, "rxcksb": 11,                                 #Physical Lane for sideband Clock Receiver
    "RXDATASBRD": 12, "rxdatasbRD": 12,                         #Physical Lane for redundant sideband Data Receiver
    "RXCKSBRD": 13, "rxcksbRD": 13,                             #Physical Lane for redundant sideband Clock Receiver
    "TCKP_P": 14, "TXCKP": 14, "txckp": 14,                     #Physical Lane for Clock Transmitter Phase-1
    "TCKN_P": 15, "TXCKN": 15, "txckn": 15,                     #Physical Lane for Clock Transmitter Phase-2
    "TRDCK_P": 16, "TXCKRD": 16, "txckRD": 16,                  #Physical Lane for redundant Clock/Track Transmitter
    "TTRK_P": 17, "TXTRK": 17, "txtrk": 17,                     #Physical Lane for Track Transmitter
    "TD_P": 18, "TD_PN": 18, "TXDATA": 18, "txdata": 18,        #Physical Lane for Data Transmitter
    "TRD_P": 19, "TRD_PN": 19, "TXDATARD": 19, "txdataRD": 19,  #Physical Lane for redundant Data Transmitter
    "TVLD_P": 20, "TXVLD": 20, "txvld": 20,                     #Physical Lane for Valid Transmitter
    "TRDVLD_P": 21, "TXVLDRD": 21, "txvldRD": 21,               #Physical Lane for redundant Valid Transmitter
    "TXDATASB": 22, "txdatasb": 22,                             #Physical Lane for sideband Data Transmitter
    "TXCKSB": 23, "txcksb": 23,                                 #Physical Lane for sideband Clock Transmitter
    "TXDATASBRD": 24, "txdatasbRD": 24,                         #Physical Lane for redundant sideband Data Transmitter
    "TXCKSBRD": 25, "txcksbRD": 25,                             #Physical Lane for redundant sideband Clock Transmitter
}

IODir = {
    0:2,
    1:2,
    2:0,
    3:0,
    4:0,
    5:0,
    6:0,
    7:0,
    8:0,
    9:0,
    10:0,
    11:0,
    12:0,
    13:1,
    14:1,
    15:1,
    16:1,
    17:1,
    18:1,
    19:1,
    20:1,
    21:1,
    22:1,
    23:1,
    24:1,
    25:1,
}

IODir_inversed = {
    0:2,
    1:2,
    2:1,
    3:1,
    4:1,
    5:1,
    6:1,
    7:1,
    8:1,
    9:1,
    10:1,
    11:1,
    12:1,
    13:0,
    14:0,
    15:0,
    16:0,
    17:0,
    18:0,
    19:0,
    20:0,
    21:0,
    22:0,
    23:0,
    24:0,
    25:0,
}

bundles = {
    0: 0,
    1: 1,
    2: 2,
    3: 2,
    4: 2,
    5: 2,
    6: 3,
    7: 3,
    8: 4,
    9: 4,
    10: 5,
    11: 6,
    12: 5,
    13: 6,
    14: 7,
    15: 7,
    16: 7,
    17: 7,
    18: 8,
    19: 8,
    20: 9,
    21: 9,
    22: 10,
    23: 11,
    24: 10,
    25: 11,
}

types = {
    0:0,
    1:1,
    2:2,
    3:2,
    4:3,
    5:2,
    6:2,
    7:3,
    8:2,
    9:3,
    10:2,
    11:2,
    12:3,
    13:3,
    14:2,
    15:2,
    16:3,
    17:2,
    18:2,
    19:3,
    20:2,
    21:3,
    22:2,
    23:2,
    24:3,
    25:3,
}

class layoutParser:
    def __init__(self):
        self.name = []
        self.bundle = []
        self.array = []
        self.xpitch = 21.65
        self.ypitch = 25
        self.dict_ = {}

    def read_csv(self, filename):
        #self.clean_list()
        with open(filename, "r") as file:
            data = reversed(list(csv.reader(file, delimiter=",")))

            for row, element in enumerate(data):
                for col, item in enumerate(element):
                    if item != "":
                        #print("row:{}, col:{}".format(row, col))
                        #print("item: {}".format(str(item)))
                        match = re.match(r"([a-z]+)([0-9]+)", item, re.I)
                        if match:
                            signal = match.groups()[0]
                            busNo = int(match.groups()[1])
                        else:
                            signal = item
                            busNo = 0
                        itemlist = []
                        idx = channels[signal]
                        mybundle = bundles[idx]
                        mytype = types[idx]
                        if idx == 6 and busNo >= 32:
                            mybundle = 12
                        if idx == 7 and busNo >= 2:
                            mybundle = 12
                        if idx == 18 and busNo >= 32:
                            mybundle = 13
                        if idx == 19 and busNo >= 2:
                            mybundle = 13
                        #print("item: {}, signal: {}, find id: {} in group {}".format(str(item), signal, idx, mybundle))
                        itemlist.append(int(row/2))
                        itemlist.append(int(col))
                        itemlist.append(round((int(col)*self.xpitch), 2))
                        itemlist.append(round((int(row/2)*self.ypitch+(self.ypitch/2 if int(col)%2 != 0 else 0)), 2))
                        itemlist.append(0.05)
                        itemlist.append(mytype)
                        itemlist.append(IODir_inversed[idx])
                        self.array.append(itemlist)
                        self.name.append(str(item))
                        del(itemlist)

    def print_array(self):
        #print("Row, Column, X, Y, Size, Bundle, Code word, Type")
        for idx, element in enumerate(self.array):
            #print(str(idx)+": ", end="")
            for item in element:
                print(item, end=", ")
            print("")
        mRow = len(self.array)
        print(mRow)

    def write_csv(self, filename):
        with open(filename, "w") as f:
            f.write("Row, Column, X, Y, Size, Bundle, Code word, Type\n")
            for idx, element in enumerate(self.array):
                for item in element:
                    f.write(str(item))
                    f.write(", ")
                f.write("\n")

    def write_layout(self, filename):
        with open(filename, "w") as f:
            dies = MicroBumpLayout_pb2.Layouts()
            array = MicroBumpLayout_pb2.MicroBumpArrays()
            array.MicroBumpCount = len(self.array)
            for idx, element in enumerate(self.array):
                microBump = MicroBumpLayout_pb2.MicroBumps()
                microBump.name = str(self.name[idx])
                microBump.id = idx
                microBump.row = int(element[0])
                microBump.col = int(element[1])
                microBump.x = float(element[2])
                microBump.y = float(element[3])
                microBump.size = float(element[4])
                microBump.type = int(element[5])
                microBump.direction = int(element[6])
                array.MicroBump.append(microBump)
                del(microBump)
            #print(dies)
            dies.MicroBumpArray.append(array)
            text_array = text_format.MessageToString(dies)
            #print(text_array)
            f.write(text_array)
        return None

    def parsenumber(self, item: object) -> object:
        match = re.match(r"([a-z]+)([0-9]+)", item, re.I)
        if match:
            signal = match.groups()[0]
            busNo = int(match.groups()[1])
        else:
            signal = item
            busNo = -1

        match2 = re.match(r"([a-z]+)([rR][dD])", signal, re.I)
        if match2:
            return (signal, 1, busNo)
        else:
            return (signal, 0, busNo)

        #match = re.match(r"([a-z]+)([rR][dD$])", item, re.I)
        #if match:
        #    return (match.groups()[0], match.groups()[1])

    def reorderlistbyname(self, items):
        min, max = (9999, -1)
        newList = []
        for item in items:
            signal, isSpare, busNo = self.parsenumber(item[0])
            if busNo > max:
                max = busNo
            if busNo < min:
                min = busNo
        for i in range(min, max+1):
            for item in items:
                signal, isSpare, busNo = self.parsenumber(item[0])
                if i == busNo:
                    newList.append(item)
        return newList

    def write_repair(self, filename):
        with open(filename, "w") as f:
            array = Repair_pb2.Arrays()
            dft = Repair_pb2.RepairDFTs()
            group = Repair_pb2.Groups()

            # TX groups
            #for idx, element in enumerate(self.array):


            dft.Repairgroup.append(group)
            array.Array.append(dft)
            print(array)
        return None

if __name__ == "__main__":
    print("LayoutParser as main function.")

    dir = os.getcwd() + "\\.\\data\\"
    layoutfilename = "\\UCIePitch38-50.csv"
    listfilename = "\\test.csv"
    lyfilename = "\\UCIe.layout"

    # Parse layout form to a list form
    parser = layoutParser()
    parser.read_csv(dir + layoutfilename)
    parser.write_csv(dir + listfilename)
    parser.write_layout(dir + lyfilename)

    #filename = "C:\\Users\\chuang90\\Downloads\\protoc-24.4-win64\\ucie.txt"
    #with open(filename, "r") as f:
    #    myarray = text_format.Parse(f.read(), Repair_pb2.Arrays())
    #print(myarray)
    #filename = ".\\data\\UCIe.layout"
    #with open(filename, "r") as f:
    #    mbarray = text_format.Parse(f.read(), MicroBumpLayout_pb2.Layouts())
    #print(mbarray)

    #repairfilename = "\\repair.txt"
    #parser.write_repair(dir + repairfilename)
    #print(parser.parsenumber("txdataRD"))

