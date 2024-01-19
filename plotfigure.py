import tkinter as tk
import matplotlib
import matplotlib.pyplot as plt
import MicroBumpLayout_pb2
import Repair_pb2
from google.protobuf import text_format
from matplotlib.lines import Line2D
from util import *

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
        self.database = None
        self.dies = []
        self.figures = []
        self.figure_widget = []

        self.geometry("720x360")
        self.title('3D Repair Simulator')
        self.dpi = 80  #dpi=120
        self.scaler = 1.0

        self.frm_buttons = tk.Frame(self, relief=tk.RAISED, bd=2)
        self.btn_open = tk.Button(self.frm_buttons, text="Open Layout",
                                  command=lambda: self.open_layout_file(self.dies))
        self.btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        self.frm_buttons.pack(side=tk.LEFT, fill='y', expand=False)  # item1

        # create textbox
        self.frm_textbox = tk.Frame(self)
        self.frm_textbox.pack(side=tk.BOTTOM, fill='x', expand=False)  # item4
        self.textbox = tk.Text(self.frm_textbox, height=7)
        self.textbox.grid(row=0, column=0, sticky="nsew")

        # Dynamic buttoms
        self.mode_btn = []
        self.mode_frm = None
        self.mode_frm = tk.Frame(self, relief=tk.RAISED, bd=2)
        self.mode_frm.pack(side=tk.BOTTOM, fill='x', expand=False)  # item2

        # create toolbars frame
        self.frm_toolbar = tk.Frame(self)
        self.frm_toolbar.pack(side=tk.BOTTOM, fill='x', expand=False)  # item5

        # create dpi bottoms
        btn_incr_dpi = tk.Button(self.frm_toolbar, text="DPI+10", command=lambda: self.add_dpi(10))
        btn_incr_dpi.pack(side=tk.LEFT, fill='x', expand=False)
        btn_decr_dpi = tk.Button(self.frm_toolbar, text="DPI-10", command=lambda: self.add_dpi(-10))
        btn_decr_dpi.pack(side=tk.LEFT, fill='x', expand=False)

        # create figure frame
        self.frm_figure = tk.Frame(self)
        self.frm_figure.pack(side=tk.TOP, fill='both', expand=True)
        self.frm_figure.bind('<Configure>', self.resize_window)
        # Mouse event list
        self.mouseevent = []
    def add_dpi(self, num):
        self.dpi = self.dpi + num
        self.flush_fig()

    def contruct_app(self, numDies):
        self.dies.clear()
        self.figures.clear()
        self.figure_widget.clear()

        self.btn_load_repair = tk.Button(self.frm_buttons, text="Load Repair",
                                    command=lambda: self.open_repair_file(self.dies))
        self.btn_load_mapping = tk.Button(self.frm_buttons, text="Load Mapping")
        self.btn_stack_dies = tk.Button(self.frm_buttons, text="Bind Layouts", command=self.create_stacked_mapping)
        self.btn_unstack_dies = tk.Button(self.frm_buttons, text="Unbind Layouts", command=self.remove_stacked_mapping)
        self.btn_line = tk.Button(self.frm_buttons, text="Draw shorts", command=self.press_drawlines)
        self.btn_clean_line = tk.Button(self.frm_buttons, text="Clean shorts", command=self.press_cleanlines)
        self.btn_show_signals = tk.Button(self.frm_buttons, text="Show signals", command=self.show_signals)
        self.btn_new_window = tk.Button(self.frm_buttons, text="Pop window", command=self.open_popup)
        self.btn_load_repair.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        self.btn_load_mapping.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.btn_stack_dies.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        self.btn_line.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        self.btn_clean_line.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        self.btn_show_signals.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
        self.btn_new_window.grid(row=9, column=0, sticky="ew", padx=5, pady=5)


        for i in range(numDies):
            die = IArray()
            self.dies.append(die)
            # create a figure
            figure = Figure(dpi=self.dpi)
            self.figures.append(figure)

            if i == 0:
                figure.suptitle('Micro-bump Map '+str(i)+' (Primary)')
            else:
                figure.suptitle('Micro-bump Map ' + str(i) + ' (Secondary)')

            # create mouse events
            mouse = MouseEvent(die, func=self.mouseclicks)
            self.mouseevent.append(mouse)
            # create FigureCanvasTkAgg object
            #figure_canvas = FigureCanvasTkAgg(figure, self)
            figure_canvas = FigureCanvasTkAgg(figure, self.frm_figure)
            figure_canvas.mpl_connect('key_press_event', self.on_press)
            figure_canvas.mpl_connect('button_press_event', mouse.mouseclick_wrapper)

            # create axes for die
            die.ax = figure.add_subplot()
            x_left, x_right = die.ax.get_xlim()
            y_low, y_high = die.ax.get_ylim()
            die.ax.set_aspect(abs((x_right - x_left) / (y_low - y_high)) * 1)

            # create the toolbar for die 1
            frm_toolbar = tk.Frame(self.frm_toolbar)
            frm_toolbar.pack(side=tk.LEFT, fill='x', expand=False)
            toolbar = NavigationToolbar2Tk(figure_canvas, frm_toolbar)
            toolbar.update()

            figure_widget = figure_canvas.get_tk_widget()
            #side = tk.LEFT
            #figure_widget.pack(side=side, fill='both', expand=True)  # item6
            figure_widget.grid(row=int(i/2), column=i%2, sticky="nsew")
            self.figure_widget.append(figure_widget)

    def resize_window(self, event=None):
        self.adjust_window(event.width, event.height)
    def adjust_window(self, new_width, new_height):
        #new_width = event.width
        #new_height = event.height
        #print(len(self.figure_widget))
        num = int( (len(self.figure_widget)+1) / 2 )
        for widget in self.figure_widget:
            widget.configure(width=new_width/2, height=new_height/num)
        #for fig in self.figures:
        #    fig.set_figwidth(new_width / 2)
        #    fig.set_figheight(new_height/2)


    def app_clear(self):
        del self.database
        self.database = None
        self.dies.clear()
        self.figures.clear()
        while self.figure_widget:
            self.figure_widget.pop().destroy()

    def open_popup(self, text="Hello world!"):
        top = tk.Tk()
        top.geometry("750x250")
        top.title("Child Window")
        #frm_textbox = tk.Frame(top)
        textbox = tk.Text(top)
        #textbox.grid(row=0, column=0, sticky="nsew")
        textbox.pack(side=tk.TOP, fill='both', expand=True)

        textbox.delete('1.0', tk.END)
        textbox.insert(tk.END, text)

    def new_mode_btn(self, func, text, argv=None):
        #if not self.mode_frm:
        #    self.mode_frm = tk.Frame(self, relief=tk.RAISED, bd=2)
        #self.mode_frm.grid(row=1, column=2, sticky="ns")
        #self.mode_frm.pack(side=tk.RIGHT, fill='both', expand=False)
        last_row = -1
        last_column = -1
        if self.mode_btn:
            last_row = self.mode_btn[-1].grid_info()['row']
            last_column = self.mode_btn[-1].grid_info()['column']
        if argv:
            if len(argv) == 1:
                self.mode_btn.append(tk.Button(self.mode_frm, text=str(text), command=lambda: func(argv[0])))
            elif len(argv) == 2:
                self.mode_btn.append(tk.Button(self.mode_frm, text=str(text), command=lambda: func(argv[0], argv[1])))
            elif len(argv) == 3:
                self.mode_btn.append(tk.Button(self.mode_frm, text=str(text), command=lambda: func(argv[0], argv[1], argv[2])))
            else:
                self.mode_btn.append(tk.Button(self.mode_frm, text=str(text), command=func))
        else:
            self.mode_btn.append(tk.Button(self.mode_frm, text=str(text), command=func))
        #self.mode_btn[-1].grid(row=last_row+1, column=0, sticky="ew", padx=5, pady=5)
        self.mode_btn[-1].grid(row=int((last_column+1)/6), column=(last_column+1)%6, sticky="ew", padx=5, pady=5)
        return self.mode_btn[-1]

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

    def load_bumps(self, layouts, text):
        if layouts:
            for idx, array in enumerate(layouts):
                if array.protomarray:
                    print("old array found")
                    del array.protomarray
                array.protomarray = text.MicroBumpArray[idx]
                array.clean_mmap()
                array.clean_lmap()
                array.clean_rmap_vEJ()

                array.construct_mmap()
                array.construct_lmap()
            self.remove_mode_btns()
            #return text

    def load_repairs(self, layouts, text):
        if layouts:
            for idx, array in enumerate(layouts):
                if array.protorepair:
                    del array.protorepair
                if idx < len(text.Array):
                    array.protorepair = text.Array[idx]
                    array.clean_rmap_vEJ()
                    array.construct_rmap_vEJ()
            self.remove_mode_btns()
            #return text

    def press_drawlines(self):
        self.cleanDrawingLines()
        self.drawing_all_lines()
        self.flush_fig()

    def press_cleanlines(self):
        self.cleanDrawingLines()
        self.flush_fig()

    def press_cleanarrows(self):
        self.cleanDrawingArrows()
        self.flush_fig()

    def open_layout_file(self, layouts):
        """Open a file for editing."""
        filepath = askopenfilename(
            filetypes=[("Layout Files", "*.layout"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, mode="r", encoding="utf-8") as input_file:
            text = text_format.Parse(input_file.read(), MicroBumpLayout_pb2.Layouts())
            self.app_clear()
            self.contruct_app(len(text.MicroBumpArray))
            self.database = text
            self.load_bumps(layouts, text)
        self.title(f"Bump layout - {filepath}")
        for array in layouts:
            if array.ax:
                array.ax.clear()
                self.drawMicroBumps(array, drawbundles=False)

    def open_repair_file(self, layouts):
        """Open a file for editing."""
        filepath = askopenfilename(
            filetypes=[("Repair Files", "*.repair"), ("All Files", "*.*")]
        )
        if not filepath:
            return
        with open(filepath, mode="r", encoding="utf-8") as input_file:
            text = text_format.Parse(input_file.read(), Repair_pb2.Arrays())
            self.load_repairs(layouts, text)
            self.show_signals()

    def cleanDrawingCircles(self):
        for item in self.axes.patches:
            item.remove()
            del item
    def flush_fig(self):
        for fig in self.figures:
            fig.set_dpi(self.dpi)
            fig.canvas.draw()
            fig.canvas.flush_events()
        #width = self.frm_figure.winfo_width()
        #height = self.frm_figure.winfo_height()
        #self.frm_figure.config(width=width*(self.dpi/60), height=height*(self.dpi/60))
        #for i, widget in enumerate(self.figure_widget):
        #    widget.grid(row=int(i/2), column=i%2)

    def drawMicroBumps(self, target_array, drawbundles=True):
        if target_array.protomarray and target_array.ax:
            drawingbumps = target_array.protomarray
            ax = target_array.ax
            x = []
            y = []
            textPlus = []
            textMinus = []
            for idx, item in enumerate(drawingbumps.MicroBump):
                self.scaler = 1.0
                xy = (item.x*self.scaler, item.y*self.scaler)
                size = item.size
                type = bumpType[int(item.type)]
                linewidth = 1
                linestyle = 'solid'
                if type == 'Function':
                    edgecolor = 'black'
                    facecolor = colorBoard[item.bundle%15 if drawbundles else -1]
                    linewidth = 2
                elif type == 'Spare':
                    edgecolor = 'orange'
                    facecolor = colorBoard[item.bundle%15 if drawbundles else -1]
                    linewidth = 2
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
                if item.direction == 0:
                    linestyle = 'dashed'
                elif item.direction == 1:
                    linestyle = 'solid'
                elif item.direction == 2:
                    linestyle = 'solid'
                ax.add_patch(plt.Circle(xy=xy, radius=size*self.scaler*180.0,
                                             edgecolor=edgecolor, facecolor=facecolor,
                                             linewidth=linewidth, zorder=10, linestyle=linestyle))
                target_array.phybumpText.append( ax.text(item.x-6, item.y+4, item.name, fontsize=10, zorder=11) )
                x.append(float(item.x))
                y.append(float(item.y))

                # Mark faulty bumps
                if item.faulty:
                    target_array.faultyText.append(
                        target_array.ax.text(item.x - 4, item.y, 'X', fontsize=10, zorder=11, color='red'))
                    target_array.faulty_bump.append(item)

            ax.scatter(x, y, s=0, marker='o')
            for item in textPlus:
                tx, ty = item
                target_array.phybumpText.append( ax.text(tx - 5, ty, '+', fontsize=8, zorder=11) )
            for item in textMinus:
                tx, ty = item
                target_array.phybumpText.append( ax.text(tx - 3, ty - 1, '-', fontsize=10, zorder=11) )

        self.flush_fig()

    def show_signals(self):
        self.clean_all_SigText()
        for array in self.dies:
            if array.protomarray:
                for bump in array.protomarray.MicroBump:
                    for idx, df in enumerate(bump.signal):
                        array.sigText.append(array.ax.text(bump.x - 6, bump.y-(4*(idx+1)), df.port, fontsize=10, zorder=11, color='blue'))
        self.flush_fig()

    def clean_all_SigText(self):
        for array in self.dies:
            while array.sigText:
                array.sigText.pop().remove()
        self.flush_fig()

    def cleanBumps(self):
        for item in self.axes.patches:
            item.remove()
            del item

    def createDrawingLine(self, line, ax):
        if ax:
            basedLineWidth = 0.5
            basedZOrder = 1.0
            bump1, bump2 = line.link
            line = Line2D([bump1.x, bump2.x],
                          [bump1.y, bump2.y], color=line.color, linewidth=basedLineWidth+line.width, zorder=basedZOrder+line.level)
            ax.add_line(line)

    def drawing_all_lines(self):
        for die in self.dies:
            for item in die.larray:
                self.createDrawingLine(item, die.ax)
            #print("Total number of drawing lines: ", len(larray))

    def cleanDrawingLines(self):
        for array in self.dies:
            if array.ax:
                for item in array.ax.lines:
                    item.remove()
                    del item

    def createDrawingArrows(self, route, array=None, color='black'):
        if route not in array.drawn_routes:
            From, To = route
            #rad = 0.27+len(self.drawnRepairGroup)*0.03
            rad = 0.33
            arpr = {"arrowstyle": "->", "connectionstyle": "arc3, rad="+str(rad), "color":str(color)}
            array.arrows.append(array.ax.annotate("", xy=(To.x, To.y), xytext=(From.x, From.y), arrowprops=arpr, zorder=11))
            self.flush_fig()
            array.drawn_routes.append(route)

    def make_a_route(self, route, array=None):
        if route not in array.routes:
            From, To, signal = route
            self.createDrawingArrows((From, To), array, 'gray')
            array.routes.append(route)
            From.signal.remove(signal)
            To.signal.append(signal)
            self.update_mode_bottoms(array, To)
            self.show_signals()

    def resume_a_route(self, route, array=None):
        if route in array.routes:
            From, To, signal = route
            if (From, To) in array.drawn_routes:
                idx = array.drawn_routes.index((From, To))
                array.drawn_routes.remove((From, To))
                print(idx)
                ar = array.arrows[idx]
                del array.arrows[idx]
                ar.remove()
                array.routes.remove(route)

                To.signal.remove(signal)
                From.signal.append(signal)
                self.update_mode_bottoms(array, From)
                self.show_signals()

    def cleanDrawingArrows(self):
        for array in self.dies:
            while array.arrows:
                ar = array.arrows.pop()
                ar.remove()
                del ar
            array.drawn_routes.clear()
            #array.drawnRepairGroup.clear()
        self.flush_fig()

    def on_press(self, event):
        print('press', event.key)
        if event.key == 'd':
            self.press_cleanlines()
            self.press_cleanarrows()
            self.clean_all_SigText()
        elif event.key == 'a':
            self.press_drawlines()

    def mouseclick_wrapper_die1(self, event):
        if event.dblclick and event.xdata:
            self.mouseclicks(event, self.dies[0])
    def mouseclick_wrapper_die2(self, event):
        if event.dblclick and event.xdata:
            self.mouseclicks(event, self.dies[1])
    def mouseclicks(self, event, array=None):
        if array.protomarray:
            tc = ((event.xdata + array.ux / 2) // array.ux).astype(int)
            ax, ay = array.anchorVector
            mr, mc = array.ArraySize
            yoffset = 0
            if ay < 0 and (tc % 2) == 0:
                yoffset = array.uy / 2
            elif ay > 0 and (tc % 2) == 1:
                yoffset = array.uy / 2
            else:
                yoffset = 0
            tr = ((event.ydata + array.uy / 2 - yoffset) // array.uy).astype(int)
            #print("row: %d, col: %d" % (tr, tc))
            if tr >= 0 and tr < mr and tc >= 0 and tc < mc and array.marray:
                self.update_mode_bottoms(array, array.marray[tr][tc])

    def update_mode_bottoms(self, array, bump):
        self.remove_mode_btns()
        self.update_text(bump)
        self.bump_repairs(array, bump)
        if bump.faulty:
            self.new_mode_btn(self.unmark_faulty, 'Unmark Faulty', (array, bump))
        else:
            self.new_mode_btn(self.mark_faulty, 'Mark Faulty', (array, bump))

    def mark_faulty(self, array, bump):
        #if bump.contactgroup == False:
        #    return

        bump.faulty = True
        if bump not in array.faulty_bump and array.ax:
            array.faultyText.append(array.ax.text(bump.x-4, bump.y, 'X', fontsize=10, zorder=11, color='red'))
            array.faulty_bump.append(bump)
        if bump.contactgroup:
            for target_array in self.dies:
                for target_bump in target_array.protomarray.MicroBump:
                    if bump != target_bump and target_bump.contactgroup == bump.contactgroup:
                        target_bump.faulty = True
                        if target_array.ax and target_bump not in target_array.faulty_bump:
                            target_array.faultyText.append(target_array.ax.text(bump.x - 4, bump.y, 'X', fontsize=10, zorder=11, color='red'))
                            target_array.faulty_bump.append(target_bump)
        self.update_mode_bottoms(array, bump)
        self.flush_fig()

    def unmark_faulty(self, array, bump):
        #if bump.contactgroup == False:
        #    return
        if bump.faulty:
            bump.ClearField('faulty')
            if bump in array.faulty_bump:
                index = array.faulty_bump.index(bump)
                array.faulty_bump.remove(bump)
                array.faultyText[index].remove()
                del array.faultyText[index]
            else:
                print("Error")
                return
            if bump.contactgroup:
                for target_array in self.dies:
                    for target_bump in target_array.protomarray.MicroBump:
                        if target_bump != bump and target_bump.contactgroup == bump.contactgroup:
                            target_bump.ClearField('faulty')
                            if target_bump in target_array.faulty_bump and target_array.ax:
                                target_index = target_array.faulty_bump.index(target_bump)
                                target_array.faulty_bump.remove(target_bump)
                                target_array.faultyText[target_index].remove()
                                del target_array.faultyText[target_index]
            self.update_mode_bottoms(array, bump)
            self.flush_fig()

    def bump_repairs(self, array, selected_bump):
        if array and selected_bump:
            for cur_sig in selected_bump.signal:
                for repair in cur_sig.repair:
                    bump = array.search_Bump_by_name(repair.To) + array.search_Bump_by_name(repair.From)
                    if len(bump) == 1 and selected_bump != bump[0] and (cur_sig.default.To == selected_bump.name or cur_sig.default.From == selected_bump.name):
                        self.new_mode_btn(self.make_a_route, str(cur_sig.port) + "->" + str(bump[0].name),
                                      ((selected_bump, bump[0], cur_sig), array))
                    #bump = array.search_Bump_by_name(repair.From)
                    #if len(bump) == 1 and selected_bump != bump[0] and cur_sig.default.From == selected_bump.name:
                    #    self.new_mode_btn(self.make_a_route, str(cur_sig.port) + "->" + str(bump[0].name),
                    #                  ((bump[0], selected_bump, cur_sig), array))

            #for item in selected_bump.repair:
            #    bumps_in_repair = []
            #    for bump in array.protomarray.MicroBump:
            #        for df_bump in bump.current:
            #            if df_bump.name == item.name:
            #                if bump not in bumps_in_repair:
            #                    bumps_in_repair.append(bump)
            #                    self.new_mode_btn(self.createDrawingArrows, str(bump.name) + ":" + str(item.name),
            #                                      ((selected_bump, bump), array, 'gray'))
            #    bumps_in_repair.clear()
            #self.new_mode_btn(self.cleanDrawingArrows, 'Clean')

            if selected_bump.signal:
                temp = [sig.port for sig in selected_bump.signal if sig.default.To and sig.default.To != selected_bump.name] + [sig.port for sig in selected_bump.signal if sig.default.From and sig.default.From != selected_bump.name]
                for name in temp:
                    for route in array.routes:
                        _, _, sig = route
                        if sig.port == name:
                            self.new_mode_btn(self.resume_a_route, 'Resume '+str(name), (route, array))

    def create_stacked_mapping(self):
        for idx, array in enumerate(self.dies):
            contactID = 1
            if array.protomarray == None:
                continue
            for bump in array.protomarray.MicroBump:
                if not bump.contactgroup:
                    bump.contactgroup = contactID
                    contactID = contactID + 1
                for i in range(1, len(self.dies)):
                    for searched_bump in self.dies[i].protomarray.MicroBump:
                        #if bump.row == searched_bump.row and bump.col == searched_bump.col:
                        if bump.id == searched_bump.id:
                            if not searched_bump.contactgroup:
                                #print("add mark: ", bump.contactgroup,", row-",searched_bump.row,", col-",searched_bump.col)
                                #print("while bump is row-", bump.row, ", col-", bump.col)
                                searched_bump.contactgroup = bump.contactgroup
        #print(self.database)
        for array in self.dies:
            for bump in array.protomarray.MicroBump:
                if bump.faulty:
                    self.mark_faulty(array, bump)
        self.btn_stack_dies.grid_remove()
        self.btn_unstack_dies.grid(row=3, column=0, sticky="ew", padx=5, pady=5)

    def remove_stacked_mapping(self):
        for array in self.dies:
            if array.protomarray == None:
                continue
            for bump in array.protomarray.MicroBump:
                bump.ClearField('contactgroup')
        self.btn_unstack_dies.grid_remove()
        self.btn_stack_dies.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
    def update_text(self, text):
        self.textbox.delete('1.0', tk.END)
        self.textbox.insert(tk.END, text)

class MouseEvent():
    def __init__(self, array, func=None, argv=None):
        self.array = array
        self.func = func
    def mouseclick_wrapper(self, event):
        if event.dblclick and event.xdata:
            self.func(event, self.array)

if __name__ == "__main__":
    app = App()
    app.mainloop()