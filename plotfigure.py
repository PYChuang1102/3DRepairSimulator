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
        self.layoutCount = 3
        self.database = None
        self.dies = []
        for i in range(self.layoutCount):
            self.dies.append(IArray())

        self.arrows = []
        self.routes = []
        self.drawn_routes = []
        self.drawnRepairGroup = []
        self.title('3D Repair Simulator')
        self.dpi = 60  #dpi=120
        self.scaler = 1.0
        # create a figure
        self.figure = Figure(dpi=self.dpi)
        self.figure_die2 = Figure(dpi=self.dpi)

        self.figure.suptitle('Micro-bump Map 0 (Primary)')
        self.figure_die2.suptitle('Micro-bump Map 1 (Secondary)')
        #self.rowconfigure(3, weight=2)
        #self.columnconfigure(2, weight=2)

        frm_buttons = tk.Frame(self, relief=tk.RAISED, bd=2)
        btn_open = tk.Button(frm_buttons, text="Open Layout", command=lambda: self.open_layout_file(self.dies))
        btn_load_repair = tk.Button(frm_buttons, text="Load Repair", command=lambda: self.open_repair_file(self.dies))
        btn_load_mapping = tk.Button(frm_buttons, text="Load Mapping")
        #btn_open_die2 = tk.Button(frm_buttons, text="Open Die2", command=lambda: self.open_layout_file(self.dies[1]))
        self.btn_stack_dies = tk.Button(frm_buttons, text="Bind Layouts", command=self.create_stacked_mapping)
        self.btn_unstack_dies = tk.Button(frm_buttons, text="Unbind Layouts", command=self.remove_stacked_mapping)
        #btn_open_repair_die2 = tk.Button(frm_buttons, text="Open repair die 2", command=lambda: self.open_repair_file(self.dies[1]))
        btn_line = tk.Button(frm_buttons, text="Draw shorts", command=self.press_drawlines)
        btn_clean_line = tk.Button(frm_buttons, text="Clean shorts", command=self.press_cleanlines)
        btn_show_signals = tk.Button(frm_buttons, text="Show signals", command=self.show_signals)
        #btn_clean_arrows = tk.Button(frm_buttons, text="Clean arrows", command=self.press_cleanarrows)
        #btn_new_button = tk.Button(frm_buttons, text="New buttons", command=lambda: self.new_mode_btn(self.print_by_press, 'New'))
        #btn_rm_mode_btn = tk.Button(frm_buttons, text="Rm buttons", command=self.remove_mode_btns)
        btn_new_window = tk.Button(frm_buttons, text="Pop window", command=self.open_popup)


        btn_open.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        btn_load_repair.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        btn_load_mapping.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        #btn_open_repair_die2.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        self.btn_stack_dies.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        btn_line.grid(row=4, column=0, sticky="ew", padx=5, pady=5)
        btn_clean_line.grid(row=5, column=0, sticky="ew", padx=5, pady=5)
        btn_show_signals.grid(row=6, column=0, sticky="ew", padx=5, pady=5)
        #btn_clean_arrows.grid(row=7, column=0, sticky="ew", padx=5, pady=5)
        #btn_new_button.grid(row=8, column=0, sticky="ew", padx=5, pady=5)
        #btn_rm_mode_btn.grid(row=9, column=0, sticky="ew", padx=5, pady=5)
        btn_new_window.grid(row=9, column=0, sticky="ew", padx=5, pady=5)

        #frm_buttons.grid(row=1, column=0, sticky="ns")
        frm_buttons.pack(side=tk.LEFT, fill='y', expand=False) #item1

        # Dynamic buttoms
        self.mode_btn = []
        self.mode_frm = None
        self.mode_frm = tk.Frame(self, relief=tk.RAISED, bd=2)
        self.mode_frm.pack(side=tk.RIGHT, fill='y', expand=False) #item2

        # create FigureCanvasTkAgg object
        self.figure_canvas = FigureCanvasTkAgg(self.figure, self)
        self.figure_canvas.mpl_connect('key_press_event', self.on_press)
        self.figure_canvas.mpl_connect('button_press_event', self.mouseclick_wrapper_die1)

        self.figure_die2_canvas = FigureCanvasTkAgg(self.figure_die2, self)
        self.figure_die2_canvas.mpl_connect('button_press_event', self.mouseclick_wrapper_die2)

        # create axes for die 1
        self.dies[0].ax = self.figure.add_subplot()
        x_left, x_right = self.dies[0].ax.get_xlim()
        y_low, y_high = self.dies[0].ax.get_ylim()
        self.dies[0].ax.set_aspect(abs((x_right - x_left) / (y_low - y_high)) * 1)

        # create axes for die 2
        self.dies[1].ax = self.figure_die2.add_subplot()
        x_left, x_right = self.dies[1].ax.get_xlim()
        y_low, y_high = self.dies[1].ax.get_ylim()
        self.dies[1].ax.set_aspect(abs((x_right - x_left) / (y_low - y_high)) * 1)

        # create textbox
        self.frm_textbox = tk.Frame(self)
        self.frm_textbox.pack(side=tk.BOTTOM, fill='x', expand=False) #item4
        self.textbox = tk.Text(self.frm_textbox, height=5)
        self.textbox.grid(row=0, column=0, sticky="nsew")

        # create toolbars frame
        self.frm_toolbar = tk.Frame(self)
        self.frm_toolbar.pack(side=tk.BOTTOM, fill='x', expand=False) #item5

            # create the toolbar for die 1
        frm_toolbar_die1 = tk.Frame(self.frm_toolbar)
        frm_toolbar_die1.pack(side=tk.LEFT, fill='x', expand=False)
        toolbar = NavigationToolbar2Tk(self.figure_canvas, frm_toolbar_die1)
        toolbar.update()

            # create the toolbar for die 2
        frm_toolbar_die2 = tk.Frame(self.frm_toolbar)
        frm_toolbar_die2.pack(side=tk.RIGHT, fill='x', expand=False)
        toolbar_die2 = NavigationToolbar2Tk(self.figure_die2_canvas, frm_toolbar_die2)
        toolbar_die2.update()

            # create dpi bottoms
        btn_incr_dpi = tk.Button(self.frm_toolbar, text="+", command=lambda: self.add_dpi(10))
        btn_incr_dpi.pack(side=tk.LEFT, fill='x', expand=False)
        btn_decr_dpi = tk.Button(self.frm_toolbar, text="-", command=lambda: self.add_dpi(-10))
        btn_decr_dpi.pack(side=tk.LEFT, fill='x', expand=False)

        # Plot die1 figure
        self.figure_canvas.get_tk_widget().pack(side=tk.LEFT, fill='both', expand=True) #item6
        # Plot die2 figure
        self.figure_die2_canvas.get_tk_widget().pack(side=tk.LEFT, fill='both', expand=True) #item7

    def add_dpi(self, num):
        self.dpi = self.dpi + num
        self.flush_fig()
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
        if self.mode_btn:
            last_row = self.mode_btn[-1].grid_info()['row']
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
        self.mode_btn[-1].grid(row=last_row+1, column=0, sticky="ew", padx=5, pady=5)
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
        self.figure.set_dpi(self.dpi)
        self.figure_die2.set_dpi(self.dpi)
        self.figure.canvas.draw()
        self.figure.canvas.flush_events()
        self.dies[0].ax.autoscale_view()
        self.figure_die2.canvas.draw()
        self.figure_die2.canvas.flush_events()
        self.dies[1].ax.autoscale_view()

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
                ax.add_patch(plt.Circle(xy=xy, radius=size*self.scaler*180.0,
                                             edgecolor=edgecolor, facecolor=facecolor,
                                             linewidth=1, zorder=10))
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
        if route not in self.drawn_routes:
            From, To = route
            #rad = 0.27+len(self.drawnRepairGroup)*0.03
            rad = 0.33
            arpr = {"arrowstyle": "->", "connectionstyle": "arc3, rad="+str(rad), "color":str(color)}
            self.arrows.append(array.ax.annotate("", xy=(To.x, To.y), xytext=(From.x, From.y), arrowprops=arpr, zorder=11))
            self.flush_fig()
            self.drawn_routes.append(route)

    def make_a_route(self, route, array=None):
        if route not in self.routes:
            From, To, signal = route
            self.createDrawingArrows((From, To), array, 'gray')
            self.routes.append(route)
            From.signal.remove(signal)
            To.signal.append(signal)
            self.update_mode_bottoms(array, To)
            self.show_signals()

    def resume_routes(self):
        return

    def cleanDrawingArrows(self):
        while self.arrows:
            ar = self.arrows.pop()
            ar.remove()
            del ar
        self.drawn_routes.clear()
        self.drawnRepairGroup.clear()
        self.flush_fig()

    def on_press(self, event):
        print('press', event.key)
        if event.key == 'd':
            self.press_cleanlines()
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
                    self.new_mode_btn(self.resume_routes, 'Resume '+str(name))

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


if __name__ == "__main__":
    app = App()
    app.mainloop()