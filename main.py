from util import *
from LayoutParser import *
from plotfigure import *

grid_ratio = 1

if __name__ == "__main__":
    UCIeLayout = IArray()
    dir = os.getcwd() + "\\.\\data\\"
    layoutfilename = "\\UCIePitch38-50.csv"
    listfilename = "\\test.csv"


    # Parse layout form to a list form
    #parser = layoutParser()
    #parser.read_csv(dir + layoutfilename)
    #parser.write_csv(dir + listfilename)

    # Read layout from the list format file
    #UCIeLayout.read_csv(dir + listfilename)

    # Load micro-bump layout
    #protolyfilename = ".\\UCIe.layout"
    #protomarray = UCIeLayout.load_layout(dir+protolyfilename)
    #print(protomarray)

    # Load repair mechanism
    #protodir = os.getcwd() + "\\..\\ProtoBuffer\\"
    #repairfilename = "UCIe.repair"
    #repair = UCIeLayout.load_repairs(protodir+repairfilename)
    #print(repair)

    # Construct micro-bump map
    #marray = UCIeLayout.construct_imap()
    #larray = UCIeLayout.construct_lmap()

    ref = []
    ref.append(UCIeLayout)

    # Create the micro-bump array figure
    #UCIeLayout.create_fig()
    # Setting drawing ratio
    #UCIeLayout.set_XYRatio(grid_ratio)
    # Plot the figure
    #.plot()
    # Update the figure
    #UCIeLayout.ax.autoscale_view()
    # Show the plotted figure
    #plt.show()

    app = App()
    addr = app.set_array(ref)
    if addr != id(UCIeLayout):
        raise("Reference fault!")
    #app.graph(app.array.protomarray)
    app.mainloop()

    # Press 'a' to get the statistical results
