import csv
import re

channels = {
    "VSS": 0, "vss": 0, "gnd": 0, "vssio": 0,                   #Physical Lane for Ground
    "VDD": 1, "vdd": 1, "vcc": 1, "vccio": 1, "vccfwdio": 1,    #Physical Lane for Power
    "RCK_P": 2, "RXCLP": 2, "rxckp" : 2,                        #Physical Lane for Clock Receiver Phase-1
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
    "TD_P": 18, "TD_PN": 18, "TXDATA": 18, "txdata": 18,       #Physical Lane for Data Transmitter
    "TRD_P": 19, "TRD_PN": 19, "TXDATARD": 19, "txdataRD": 19,  #Physical Lane for redundant Data Transmitter
    "TVLD_P": 20, "TXVLD": 20, "txvld": 20,                     #Physical Lane for Valid Transmitter
    "TRDVLD_P": 21, "TXVLDRD": 21, "txvldRD": 21,               #Physical Lane for redundant Valid Transmitter
    "TXDATASB": 22, "txdatasb": 22,                             #Physical Lane for sideband Data Transmitter
    "TXCKSB": 23, "txcksb": 23,                                 #Physical Lane for sideband Clock Transmitter
    "TXDATASBRD": 24, "txdatasbRD": 24,                         #Physical Lane for redundant sideband Data Transmitter
    "TXCKSBRD": 25, "txcksbRD": 25,                             #Physical Lane for redundant sideband Clock Transmitter
}

bundles = {
    0:0,
    1:1,
    2:2,
    3:2,
    4:2,
    5:2,
    6:3,
    7:3,
    8:4,
    9:4,
    10:5,
    11:6,
    12:5,
    13:6,
    14:7,
    15:7,
    16:7,
    17:7,
    18:8,
    19:8,
    20:9,
    21:9,
    22:10,
    23:11,
    24:10,
    25:11,
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
        self.name = ""
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
                        print("item: {}".format(str(item)))
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
                        print("item: {}, signal: {}, find id: {} in group {}".format(str(item), signal, idx, mybundle))
                        itemlist.append(int(row/2))
                        itemlist.append(int(col))
                        itemlist.append(round((int(col)*self.xpitch), 2))
                        itemlist.append(round((int(row/2)*self.ypitch+(self.ypitch/2 if int(col)%2 != 0 else 0)), 2))
                        itemlist.append(0.05)
                        itemlist.append(mybundle)
                        itemlist.append(int(0))
                        itemlist.append(mytype)
                        self.array.append(itemlist)
                        del(itemlist)

    def print_array(self):
        print("Row, Column, X, Y, Size, Bundle, Code word, Type")
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
