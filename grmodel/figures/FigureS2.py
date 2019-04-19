"""
This creates Figure S2.
"""

# from ..sampleAnalysis import readSingle


def build(loadFile='072718_PC9_BYL_PIM', singles=True):
    ''' Build and save the drugInteractionModel '''
    from ..pymcGrowth import GrowthModel
    M = GrowthModel(loadFile, singles)
    M.importData(firstCols=2)
    M.performFit()
    # Save the drug interaction model
    M.save()


def makeFigure():
    ''' Make Figure S2. This should be the experimental data of
        single drug in each drug combinations '''
    from .Figure2 import simulationPlots
    from string import ascii_uppercase
    from .FigureCommon import getSetup, subplotLabel

    # Get list of axis objects
    ax, f, _ = getSetup((12, 8), (4, 6))

    for axis in ax[0:24]:
        axis.tick_params(axis='both', which='major', pad=-2)  # set ticks style

    files = ['072718_PC9_BYL_PIM', '081118_PC9_LCL_TXL', '071318_PC9_OSI_Bin', '090618_PC9_TXL_Erl']
    drugAs = ['PIM447', 'LCL161', 'OSI-906', 'Paclitaxel']
    drugBs = ['BYL749', 'Paclitaxel', 'Binimetinib', 'Erl']

    # Show simulation plots (predicted vs experimental)
    simulationPlots(axes=[ax[0], ax[1], ax[2], ax[6], ax[7], ax[8]],
                    ff=files[0], drugAname=drugAs[0], drugBname=drugBs[0], sg=True)
    simulationPlots(axes=[ax[3], ax[4], ax[5], ax[9], ax[10], ax[11]],
                    ff=files[1], drugAname=drugAs[1], drugBname=drugBs[1], sg=True)
    simulationPlots(axes=[ax[12], ax[13], ax[14], ax[18], ax[19], ax[20]],
                    ff=files[2], drugAname=drugAs[2], drugBname=drugBs[2], sg=True)
    simulationPlots(axes=[ax[15], ax[16], ax[17], ax[21], ax[22], ax[23]],
                    ff=files[3], drugAname=drugAs[3], drugBname=drugBs[3], sg=True)

    # TODO: change labels for each subplot
    for ii, item in enumerate([ax[0], ax[3], ax[12], ax[15]]):
        subplotLabel(item, ascii_uppercase[ii])

    # Try and fix overlapping elements
    f.tight_layout(pad=0.1)

    return f
