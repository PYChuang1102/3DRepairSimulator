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


class App(tk.Tk):

    def __init__(self):
        super().__init__()

        self.bumps = None
        self.array = None
        self.title('3D Repair Simulator')

        # create a figure
        self.figure = Figure(dpi=120)

        self.rowconfigure(2, weight=1)
        self.columnconfigure(2, weight=1)

        frm_buttons = tk.Frame(self, relief=tk.RAISED, bd=2)
        btn_open = tk.Button(frm_buttons, text="Open", command=self.open_layout_file)
        btn_save = tk.Button(frm_buttons, text="Save As...")
        btn_line = tk.Button(frm_buttons, text="Draw shorts", command=self.press_drawlines)
        btn_clean_line = tk.Button(frm_buttons, text="Clean shorts", command=self.press_cleanlines)
        btn_open_repair = tk.Button(frm_buttons, text="Open repair", command=self.open_repair_file)

        btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_save.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        btn_line.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        btn_clean_line.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        btn_open_repair.grid(row=4, column=0, sticky="ew", padx=5, pady=5)

        frm_buttons.grid(row=0, column=0, sticky="ns")

        # create FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(self.figure, self)
        self.figure_canvas.mpl_connect('key_press_event', self.on_press)

        # create the toolbar
        frm_toolbar = tk.Frame(self)
        frm_toolbar.grid(row=1, column=1, sticky="nsew")
        toolbar = NavigationToolbar2Tk(self.figure_canvas, frm_toolbar)
        #NavigationToolbar2Tk(self.figure_canvas, self)

        # create axes
        self.axes = self.figure.add_subplot()

        # Plot default figure
        self.graph(self.bumps)

        # create the barchart
        #self.axes.set_title('Top 5 Programming Languages')
        #self.axes.set_ylabel('Popularity')

        x_left, x_right = self.axes.get_xlim()
        y_low, y_high = self.axes.get_ylim()
        self.axes.set_aspect(abs((x_right - x_left) / (y_low - y_high)) * 1)

        #figure_canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.figure_canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")
        toolbar.update()

    def set_array(self, ref):
        self.array = ref[0]
        return id(self.array)

    def load_bumps(self, text):
        self.array.protomarray = text
        self.array.clean_lmap()
        self.array.clean_imap()
        self.array.load_layout_from_proto(text)
        self.array.construct_imap()
        self.array.construct_lmap()
        return text

    def load_repairs(self, text):
        self.array.protorepair = text
        self.array.construct_rmap()
        self.cleandrawings()
        self.graph(self.array.protomarray, drawbundles=False)
        return text

    def press_drawlines(self):
        self.cleanDrawingLines()
        self.drawing_all_lines(self.array.larray)
        self.flush_fig()

    def press_cleanlines(self):
        self.cleanDrawingLines()
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
        self.graph(self.array.protomarray, drawbundles=True)

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

    def cleandrawings(self):
        for item in self.axes.lines:
            item.remove()
            del item
        for item in self.axes.patches:
            item.remove()
            del item
        #self.figure.clear()

    def cleanDrawingCircles(self):
        for item in self.axes.patches:
            item.remove()
            del item
    def flush_fig(self):
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        self.axes.autoscale_view()
    def graph(self, drawingbumps, drawbundles=True):
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
                    facecolor = colorBoard[item.bundle%15 if drawbundles else item.color%15]
                elif type == 'Spare':
                    edgecolor = 'orange'
                    facecolor = colorBoard[item.bundle%15 if drawbundles else item.color%15]
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
                self.axes.text(tx - 5, ty - 4, '+', fontsize=8, zorder=11)
            for item in textMinus:
                tx, ty = item
                self.axes.text(tx - 3, ty - 5, '-', fontsize=10, zorder=11)
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
            print("Total number of drawing lines: ", len(larray))

    def cleanDrawingLines(self):
        for item in self.axes.lines:
            item.remove()
            del item

    def on_press(self, event):
        print('press', event.key)
        if event.key == 'd':
            self.press_cleanlines()
        elif event.key == 'a':
            self.press_drawlines()

if __name__ == "__main__":
    #window = tk.Tk()
    #window.title("Simple Text Editor")

    #window.rowconfigure(0, minsize=800, weight=1)
    #window.columnconfigure(1, minsize=800, weight=1)

    #txt_edit = tk.Text(window)
    #frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
    #btn_open = tk.Button(frm_buttons, text="Open", command=open_file)
    #btn_save = tk.Button(frm_buttons, text="Save As...")

    #btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
    #btn_save.grid(row=1, column=0, sticky="ew", padx=5)

    #frm_buttons.grid(row=0, column=0, sticky="ns")
    #txt_edit.grid(row=0, column=1, sticky="nsew")

    #languages = data.keys()
    #popularity = data.values()

    #figure_canvas = FigureCanvasTkAgg(UCIeLayout.fig)
    #figure_canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")


    app = App()
    app.mainloop()