import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    import cPickle as pickle
except ImportError:
    import pickle


def geweke_single_chain(chain1, chain2=None):
    """
    Perform the Geweke Diagnostic between two univariate chains. If two chains are input 
    instead of one, Student's t-test is performed instead. Returns p-value.
    """

    from scipy.stats import ttest_ind

    len0 = chain1.shape[0]
    if chain2 is None:
        chain2 = chain1[int(np.ceil(len0 / 2)):len0]
        chain1 = chain1[0:int(np.ceil(len0 * 0.1))]

    return ttest_ind(chain1, chain2)[1]


def read_dataset(column, filename=None):
    ''' Read the specified column from the shared test file. '''
    import os
    import h5py

    if filename is None:
        filename = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "./data/first_chain.h5")

    # Open hdf5 file
    f = h5py.File(filename, 'r')

    # Read in StoneModel and unpickle
    classM = pickle.loads(f['/column' + str(column)].attrs['class'].tobytes())

    # Read in likelihood and chain
    dln = np.expand_dims(
        np.array(f['/column' + str(column) + '/lnprob']), axis=2)
    dchain = np.array(f['/column' + str(column) + '/chain'])

    # Close hdf5 file
    f.close()

    # Merge likelihood and chain, make into panel, then frame
    dset = pd.Panel(np.dstack((dln, dchain))).swapaxes(0, 2).to_frame()

    # Get names ready
    pNames = classM.pNames
    pNames.insert(0, 'LL')
    dset.columns = pNames

    dset.index.names = ['step', 'walker']

    return (classM, dset)


def growth_rate_plot(column):
    from .GrowthModel import mcFormat

    # Read in dataset to Pandas data frame
    classM, pdset = read_dataset(column)

    pdset = pdset.loc[pdset['LL'] > -3000, :]

    print(classM.expTable)

    # Time interval to solve over
    t_interval = np.arange(0, np.max(classM.uniqueT), 0.2)

    # Evaluate each of the growth rates over the time interval
    calcset = np.full((pdset.shape[0], len(t_interval)), np.inf)

    varr = 0
    vv = 0

    for row in pdset.iterrows():
        mparm = mcFormat(row[1].as_matrix()[1:-4])

        calcset[varr, :] = np.exp(np.polyval(mparm[:, vv], t_interval))

        varr = varr + 1

    # Get median & 95% confidence interval for each time point
    med = np.median(calcset, axis=0)
    upper = np.percentile(calcset, 0.95, axis=0)
    lower = np.percentile(calcset, 0.05, axis=0)

    plt.figure(figsize=(10, 10))
    plt.plot(t_interval, med)
    plt.fill_between(t_interval, lower, upper, alpha=0.3)
    plt.show()


def sim_plot(column):
    from .GrowthModel import mcFormat, simulate

    # Read in dataset to Pandas data frame
    classM, pdset = read_dataset(column)

    pdset = pdset.loc[pdset['LL'] > -3000, :]

    # Time interval to solve over
    t_interval = np.arange(0, np.max(classM.uniqueT), 0.2)

    # Evaluate each of the growth rates over the time interval
    calcset = np.full((pdset.shape[0], len(t_interval)), np.inf)

    varr = 0
    vv = 0

    for row in pdset.iterrows():
        mparm = mcFormat(row[1].as_matrix()[1:-4])

        simret = simulate(mparm, t_interval)[1]

        calcset[varr, :] = np.sum(simret, axis=1) * row[1]['conv_confl']

        varr = varr + 1

    # Get median & 95% confidence interval for each time point
    qqq = np.percentile(calcset, [5, 25, 50, 75, 95], axis=0)

    plt.figure(figsize=(10, 10))
    plt.plot(t_interval, qqq[2, :])
    plt.fill_between(t_interval, qqq[1, :], qqq[3, :], alpha=0.3)
    plt.fill_between(t_interval, qqq[0, :], qqq[4, :], alpha=0.3)
    plt.show()


def plotSimulation(self, paramV):
    """
    Plots the results from a simulation.
    TODO: Run simulation when this is called, and also plot observations.
    TODO: If selCol is None, then plot simulation but not observations.
    """

    # Calculate model data table
    params = mcFormat(paramV[:-4])
    t_interval = np.arange(
        0, self.data_confl.iloc[-1, 1], (self.data_confl.iloc[2, 1] - self.data_confl.iloc[1, 1]))

    state = simulate(params, t_interval)

    # plot simulation results; if selCol is not None, also plot observations
    if self.selCol is not None:
        # print(self.selCol)
        data_confl_selCol = self.data_confl.iloc[:, self.selCol]
        data_green_selCol = self.data_green.iloc[:, self.selCol]
        t_interval_observ = self.data_confl.iloc[:, 1]

        # get conversion constants
        conv_confl, conv_green = np.power(10, paramV[-4:-2])

        # adjust simulation values
        simulation_confl = state.iloc[:, 1] * conv_confl
        simulation_green = (state.iloc[:, 2] + state.iloc[:, 3]) * conv_green

        f, axarr = plt.subplots(3, figsize=(10, 10))
        axarr[0].set_title('Simulation Results')
        t_interval = state.iloc[:, 0].values
        axarr[0].plot(t_interval, state.iloc[:, 1], 'b-', label="live")
        axarr[0].plot(t_interval, state.iloc[:, 2], 'r-', label="dead")
        axarr[0].plot(t_interval, state.iloc[:, 3],
                      'g-', label="early apoptosis")
        axarr[0].plot(t_interval, state.iloc[:, 4], 'k-', label="gone")
        axarr[0].legend(bbox_to_anchor=(1.04, 0.5),
                        loc="center left", borderaxespad=0)

        axarr[1].set_title('Observed: data_confl')
        axarr[1].plot(t_interval_observ, data_confl_selCol, label='data_confl')
        axarr[1].plot(t_interval, simulation_confl, label='simulation_confl')
        axarr[1].legend(bbox_to_anchor=(1.04, 0.5),
                        loc="center left", borderaxespad=0)

        axarr[2].set_title('Observed: data_green')
        axarr[2].plot(t_interval_observ, data_green_selCol, label='data_green')
        axarr[2].plot(t_interval, simulation_green, label='simulation_green')
        axarr[2].legend(bbox_to_anchor=(1.04, 0.5),
                        loc="center left", borderaxespad=0)
        plt.tight_layout()
        plt.show()
    else:
        figure()
        xlabel('Time')
        ylabel('Number of Cells')
        t_interval = state.iloc[:, 0].values
        plt.plot(t_interval, state.iloc[:, 1], 'b-', label="live")
        plt.plot(t_interval, state.iloc[:, 2], 'r-', label="dead")
        plt.plot(t_interval, state.iloc[:, 3], 'g-', label="early apoptosis")
        plt.plot(t_interval, state.iloc[:, 4], 'k-', label="gone")
        plt.legend(loc='upper right')
        show()
