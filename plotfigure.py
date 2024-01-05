import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt
import MicroBumpLayout_pb2
import Repair_pb2
from google.protobuf import text_format
from matplotlib.lines import Line2D

matplotlib.use('TkAgg')

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
from tkinter.filedialog import askopenfilename

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
            3: 'Spare'
}

class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.bumps = None
        self.array = None
        self.arrows = []
        self.texts = []
        self.drawnRepairGroup = []
        self.title('3D Repair Simulator')

        # create a figure
        self.figure = Figure(dpi=60) #dpi=120

        #self.rowconfigure(3, weight=2)
        #self.columnconfigure(2, weight=2)

        frm_buttons = tk.Frame(self, relief=tk.RAISED, bd=2)
        btn_open = tk.Button(frm_buttons, text="Open", command=self.open_layout_file)
        btn_save = tk.Button(frm_buttons, text="Save As...")
        btn_line = tk.Button(frm_buttons, text="Draw shorts", command=self.press_drawlines)
        btn_clean_line = tk.Button(frm_buttons, text="Clean shorts", command=self.press_cleanlines)
        btn_open_repair = tk.Button(frm_buttons, text="Open repair", command=self.open_repair_file)
        btn_arrows = tk.Button(frm_buttons, text="Draw arrows", command=self.press_drawarrows)
        btn_clean_arrows = tk.Button(frm_buttons, text="Clean arrows", command=self.press_cleanarrows)
        btn_new_button = tk.Button(frm_buttons, text="New buttons", command=lambda: self.new_mode_btn(self.print_by_press, 'New'))
        btn_rm_mode_btn = tk.Button(frm_buttons, text="Rm buttons", command=self.remove_mode_btns)

        btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_save.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        btn_line.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        btn_clean_line.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        btn_open_repair.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        btn_arrows.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        btn_clean_arrows.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
        btn_new_button.grid(row=7, column=0, sticky="ew", padx=5, pady=5)
        btn_rm_mode_btn.grid(row=8, column=0, sticky="ew", padx=5, pady=5)

        #frm_buttons.grid(row=1, column=0, sticky="ns")
        frm_buttons.pack(side=tk.LEFT, fill='y', expand=False)

        # Dynamic buttoms
        self.mode_btn = []
        self.mode_frm = None
        self.mode_frm = tk.Frame(self, relief=tk.RAISED, bd=2)
        self.mode_frm.pack(side=tk.RIGHT, fill='y', expand=False)

        # create FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(self.figure, self)
        self.figure_canvas.mpl_connect('key_press_event', self.on_press)
        self.figure_canvas.mpl_connect('button_press_event', self.mouseclicks)

        # create the toolbar
        frm_toolbar = tk.Frame(self)
        #frm_toolbar.grid(row=2, column=1, sticky="nsew")
        frm_toolbar.pack(side=tk.BOTTOM, fill='x', expand=False)
        toolbar = NavigationToolbar2Tk(self.figure_canvas, frm_toolbar)
        #NavigationToolbar2Tk(self.figure_canvas, self)

        # create axes
        self.axes = self.figure.add_subplot()

        # create the barchart
        #self.axes.set_title('Top 5 Programming Languages')
        #self.axes.set_ylabel('Popularity')

        x_left, x_right = self.axes.get_xlim()
        y_low, y_high = self.axes.get_ylim()
        self.axes.set_aspect(abs((x_right - x_left) / (y_low - y_high)) * 1)

        #figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        #self.figure_canvas.get_tk_widget().grid(row=1, column=1, sticky="nsew")
        self.figure_canvas.get_tk_widget().pack(side=tk.TOP, fill='both', expand=True)
        toolbar.update()

        self.frm_textbox = tk.Frame(self)
        #self.frm_textbox.grid(row=0, column=1, sticky="ew")
        self.frm_textbox.pack(side=tk.BOTTOM, fill='x', expand=False)
        self.textbox = tk.Text(self.frm_textbox, height=5)
        self.textbox.grid(row=0, column=0, sticky="nsew")

    def set_array(self, ref):
        self.array = ref[0]
        return id(self.array)

    def new_mode_btn(self, func, text, argv=None):
        #if not self.mode_frm:
        #    self.mode_frm = tk.Frame(self, relief=tk.RAISED, bd=2)
        #self.mode_frm.grid(row=1, column=2, sticky="ns")
        #self.mode_frm.pack(side=tk.RIGHT, fill='both', expand=False)
        last_row = -1
        if self.mode_btn:
            last_row = self.mode_btn[-1].grid_info()['row']
        if argv:
            self.mode_btn.append(tk.Button(self.mode_frm, text=str(text), command=lambda: func(argv[0], argv[1])))
        else:
            self.mode_btn.append(tk.Button(self.mode_frm, text=str(text), command=func))
        self.mode_btn[-1].grid(row=last_row+1, column=0, sticky="ew", padx=5, pady=5)

    def print_by_press(self, arg1=None, arg2=None):
        while arg1:
            print(arg1.pop())

    def remove_mode_btns(self):
        while self.mode_btn:
            btn = self.mode_btn.pop()
            btn.grid_remove()
            del btn

        if self.mode_btn:
            raise "Error when remove mode buttons."

        if self.mode_frm:
            self.mode_frm.grid_remove()
            #del self.mode_frm
            #self.mode_frm = None

    def load_bumps(self, text):
        if self.array.protomarray:
            del self.array.protomarray
        self.array.protomarray = text
        self.array.clean_mmap()
        self.array.clean_lmap()
        self.array.clean_rmap()
        self.remove_mode_btns()
        self.array.construct_mmap()
        self.array.construct_lmap()
        return text

    def load_repairs(self, text):
        self.array.protorepair = text
        self.array.clean_rmap()
        self.array.construct_rmap()
        #self.cleandrawings()
        #self.drawMicroBumps(self.array.protomarray, drawbundles=False)
        self.remove_mode_btns()
        # Create mode buttons
        #for bundle in self.array.protorepair.Bundle:
        #    max_mode = max([bundle.DetourPathCount])
        #for idx in range(max_mode+1):
        #    self.new_mode_btn(self.print_by_press, [idx*2])
        return text

    def press_drawlines(self):
        self.cleanDrawingLines()
        self.drawing_all_lines(self.array.larray)
        self.flush_fig()

    def press_cleanlines(self):
        self.cleanDrawingLines()
        self.flush_fig()

    def press_cleanarrows(self):
        self.cleanDrawingArrows()
        self.flush_fig()

    def open_layout_file(self):
        """Open a file for editing."""
        filepath = askopenfilename(
            filetypes=[("Layout Files", "*.layout"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, mode="r", encoding="utf-8") as input_file:
            text = text_format.Parse(input_file.read(), MicroBumpLayout_pb2.MicroBumpArrays())
            #print(text)
            self.load_bumps(text)
        self.title(f"Bump layout - {filepath}")
        self.cleandrawings()
        self.drawMicroBumps(self.array.protomarray, drawbundles=False)

    def open_repair_file(self):
        """Open a file for editing."""
        filepath = askopenfilename(
            filetypes=[("Repair Files", "*.repair"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, mode="r", encoding="utf-8") as input_file:
            text = text_format.Parse(input_file.read(), Repair_pb2.Arrays())
            self.load_repairs(text)
            if self.array.rarray:
                self.update_text("Imported repair file: "+filepath)
            else:
                self.update_text("Failed.")

    def cleandrawings(self):
        self.axes.clear()

    def cleanDrawingCircles(self):
        for item in self.axes.patches:
            item.remove()
            del item
    def flush_fig(self):
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        self.axes.autoscale_view()

    def drawMicroBumps(self, drawingbumps, drawbundles=True):
        if drawingbumps:
            x = []
            y = []
            textPlus = []
            textMinus = []
            for idx, item in enumerate(drawingbumps.MicroBump):
                xy = (item.x, item.y)
                size = item.size
                scaler = 1.0
                type = bumpType[int(item.type)]
                if type == 'Function':
                    edgecolor = 'black'
                    facecolor = colorBoard[item.bundle%15 if drawbundles else -1]
                elif type == 'Spare':
                    edgecolor = 'orange'
                    facecolor = colorBoard[item.bundle%15 if drawbundles else -1]
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
                self.axes.add_patch(plt.Circle(xy=xy, radius=size*scaler*150.0,
                                             edgecolor=edgecolor, facecolor=facecolor,
                                             linewidth=1, zorder=10))
                x.append(float(item.x))
                y.append(float(item.y))
            self.axes.scatter(x, y, s=0, marker='o')
            for item in textPlus:
                tx, ty = item
                self.texts.append( self.axes.text(tx - 5, ty - 4, '+', fontsize=8, zorder=11) )
            for item in textMinus:
                tx, ty = item
                self.texts.append( self.axes.text(tx - 3, ty - 5, '-', fontsize=10, zorder=11) )
        #else:
        #    raise Exception('Array is empty!!')
        self.flush_fig()

    def cleanBumps(self):
        for item in self.axes.patches:
            item.remove()
            del item

    def createDrawingLine(self, line):
        basedLineWidth = 0.5
        basedZOrder = 1.0
        bump1, bump2 = line.link
        line = Line2D([bump1.x, bump2.x],
                      [bump1.y, bump2.y], color=line.color, linewidth=basedLineWidth+line.width, zorder=basedZOrder+line.level)
        self.axes.add_line(line)

    def drawing_all_lines(self, larray):
        if larray:
            for item in larray:
                self.createDrawingLine(item)
            #print("Total number of drawing lines: ", len(larray))

    def cleanDrawingLines(self):
        for item in self.axes.lines:
            item.remove()
            del item

    def createDrawingArrows(self, route, color):
        From, To = route
        rad = 0.27+len(self.drawnRepairGroup)*0.03 #rad = 0.33
        arpr = {"arrowstyle": "->", "connectionstyle": "arc3, rad="+str(rad), "color":str(color)}
        self.arrows.append(self.axes.annotate("", xy=(To.x, To.y), xytext=(From.x, From.y), arrowprops=arpr, zorder=11))

    def drawing_a_group(self, routes, color='black'):
        if routes:
            if routes not in self.drawnRepairGroup:
                self.drawnRepairGroup.append(routes)
                for item in routes:
                    self.createDrawingArrows((item[0], item[1]), color)
                self.flush_fig()
                print("Drawing ...")

    def cleanDrawingArrows(self):
        while self.arrows:
            ar = self.arrows.pop()
            ar.remove()
            del ar
        self.drawnRepairGroup.clear()
        self.flush_fig()

    def on_press(self, event):
        print('press', event.key)
        if event.key == 'd':
            self.press_cleanlines()
        elif event.key == 'a':
            self.press_drawlines()
        elif event.key == 'z':
            self.press_drawarrows()
    def press_drawarrows(self):
        if self.array.rarray:
            for idx, item in enumerate(self.array.rarray):
                self.drawing_a_group(item, colorBoard[idx + 3])
    def mouseclicks(self, event):
        if self.array.protomarray and event.dblclick and event.xdata:
            tc = ((event.xdata + self.array.ux / 2) // self.array.ux).astype(int)
            ax, ay = self.array.anchorVector
            mr, mc = self.array.ArraySize
            yoffset = 0
            if ay < 0 and (tc % 2) == 0:
                yoffset = self.array.uy / 2
            elif ay > 0 and (tc % 2) == 1:
                yoffset = self.array.uy / 2
            else:
                yoffset = 0
            tr = ((event.ydata + self.array.uy / 2 - yoffset) // self.array.uy).astype(int)
            #print("row: %d, col: %d" % (tr, tc))
            if tr >= 0 and tr < mr and tc >= 0 and tc < mc and self.array.marray:
                self.remove_mode_btns()
                #self.cleanDrawingArrows()
                self.update_text(self.array.marray[tr][tc])
                if self.array.rarray:
                    groups = self.search_RepairGroup_by_bump(self.array.marray[tr][tc])
                    for idx in groups:
                        item = self.array.rarray[idx]
                        self.new_mode_btn(self.drawing_a_group, 'Group '+str(idx), (item, colorBoard[idx+3]))
                    self.new_mode_btn(self.cleanDrawingArrows, 'Clean')

    def search_RepairGroup_by_bump(self, bump):
        rst = []
        for idx, group in enumerate(self.array.rlist):
            if bump in group:
                rst.append(idx)
                #print("found in group ", idx)
        return rst


    def update_text(self, text):
        self.textbox.delete('1.0', tk.END)
        self.textbox.insert(tk.END, text)

if __name__ == "__main__":
    app = App()
    app.mainloop()