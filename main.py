from LayoutParser import *
from plotfigure import *

grid_ratio = 1

if __name__ == "__main__":
    UCIeLayout = IArray()
    dir = os.getcwd() + "\\.\\data\\"
    layoutfilename = "\\UCIePitch38-50.csv"
    listfilename = "\\test.csv"

    ref = []
    ref.append(UCIeLayout)

    app = App()
    #addr = app.set_array(ref)
    #if addr != id(UCIeLayout):
    #    raise("Reference fault!")
    #app.graph(app.array.protomarray)
    app.mainloop()

    # Press 'a' to get the statistical results
