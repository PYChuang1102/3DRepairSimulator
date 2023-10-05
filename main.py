from util import *
from LayoutParser import *

grid_ratio = 1

if __name__ == "__main__":
    myarray = IArray()
    dir = os.getcwd() + "\\..\\data\\"
    layoutfilename = "\\UCIePitch25-37.csv"
    listfilename = "\\test.csv"

    # Parse layout form to a list form
    parser = layoutParser()
    parser.read_csv(dir + layoutfilename)
    parser.write_csv(dir + listfilename)

    # Read layout from the list format file
    myarray.read_csv(dir + listfilename)
    # Construct micro-bump map
    array = myarray.construct_imap()
    # Create the micro-bump array figure
    myarray.create_fig()
    # Setting drawing ratio
    myarray.set_XYRatio(grid_ratio)
    # Plot the figure
    myarray.plot()
    # Update the figure
    myarray.ax.autoscale_view()
    # Show the plotted figure
    plt.show()

    # Press 'a' to get the statistical results
