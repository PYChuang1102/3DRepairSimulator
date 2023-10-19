from util import *
from LayoutParser import *

grid_ratio = 1

if __name__ == "__main__":
    UCIeLayout = IArray()
    dir = os.getcwd() + "\\.\\data\\"
    layoutfilename = "\\UCIePitch38-50.csv"
    listfilename = "\\test.csv"

    print("Hello Annie!")

    # Parse layout form to a list form
    parser = layoutParser()
    parser.read_csv(dir + layoutfilename)
    parser.write_csv(dir + listfilename)

    # Read layout from the list format file
    UCIeLayout.read_csv(dir + listfilename)
    # Construct micro-bump map
    marray = UCIeLayout.construct_imap()
    larray = UCIeLayout.construct_lmap()
    # Create the micro-bump array figure
    UCIeLayout.create_fig()
    # Setting drawing ratio
    UCIeLayout.set_XYRatio(grid_ratio)
    # Plot the figure
    UCIeLayout.plot()
    # Update the figure
    UCIeLayout.ax.autoscale_view()
    # Show the plotted figure
    plt.show()

    # Press 'a' to get the statistical results
