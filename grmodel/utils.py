import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

try:
    import cPickle as pickle
except ImportError:
    import pickle


def read_dataset(column, filename=None, trim=True):
    ''' Read the specified column from the shared test file. '''
    import os
    import h5py
    from .pymcGrowth import GrowthModel

    if filename is None:
        filename = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "./data/030317_first_chain.h5")

    # Open hdf5 file
    f = h5py.File(filename, 'r')

    # Read in StoneModel and unpickle
    #classM = pickle.loads(f['/column' + str(column)].attrs['class'].tobytes())
    

    # Close hdf5 file
    f.close()

    # Read in sampling chain
    df = pd.read_hdf(filename, key='column' + str(column) + '/chain')
    
    # Initialize StoneModel
    classM = GrowthModel()
    classM.importData(column)

    # Add the column this came from
    df['Col'] = column
    df['Condition'] = classM.condName

    # Remove unlikely points if chosen
    if trim:
        cutoff = np.amin(df['ssqErr'])+10
        df = df.loc[df['ssqErr'] < cutoff,:]
        #df = df.loc[df['sqqErr'] < (np.min(df['sqqErr']) + 10), :]

    return (classM, df)


def growth_rate_plot(column):
    # Read in dataset to Pandas data frame
    classM, pdset = read_dataset(column)

    pdset = pdset.loc[pdset['LL'] > -30000, :]

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
    from .pymcGrowth import GrowthModel

    # Read in dataset to Pandas data frame
    classM, pdset = read_dataset(column)

    #print(pdset.shape)

    print(pdset)

    #raise

    # Time interval to solve over
#    t_interval = np.arange(0, np.max(classM.timeV), 0.2)

    # Evaluate each of the growth rates over the time interval
    calcset = np.full((pdset.shape[0], len(classM.timeV)), np.inf)

    varr = 0
    vv = 0

    for row in pdset.iterrows():
        mparm = np.copy(row[1].as_matrix()[0:4])
#        try:
        simret = classM.old_model(mparm, row[1]['confl_conv'])[1]

        calcset[varr, :] = np.sum(simret, axis = 1)

        varr = varr + 1
#        except:
#            print('Failed')
#            continue
    # Get rid of repeating predictions
    calcset = calcset[:,:25]
    time = classM.timeV.reshape(3,25)[0,:]
    # Get median & 90% confidence interval for each time point
    qqq = np.percentile(calcset, [5, 25, 50, 75, 95], axis=0)
    
    plt.figure(figsize=(10, 10))
    plt.plot(time, qqq[2, :])
    plt.fill_between(time, qqq[1, :], qqq[3, :], alpha=0.5)
    plt.fill_between(time, qqq[0, :], qqq[4, :], alpha=0.2)
#    calcset = np.full((len(classM.timeV)), np.inf)
#    mparm = np.power(10,[-1.5,-4,-4,-3])
#    simret = classM.old_model(mparm, np.power(10,0.75))[1]
#    calcset[:] = np.sum(simret,axis = 1)
#    calcset = calcset.reshape(3,25)[0,:]
#    plt.plot(classM.timeV.reshape(3,25)[0,:], calcset)
    plt.scatter(classM.timeV, classM.expTable['confl'])
    plt.scatter(classM.timeV, classM.expTable['apop'])
    plt.scatter(classM.timeV, classM.expTable['dna'])
    plt.show()


def hist_plot():
    """
    Display histograms of parameter values across conditions
    """
    import seaborn as sns
    # Read in dataset to Pandas data frame
    df = pd.concat(map(lambda x: read_dataset(x)[1], [2, 3, 4, 5]))

    print(df.columns)

    # Reduce the number of data points randomly
    df = df.sample(1000)
    
    # Main plot organization
    sns.pairplot(df, diag_kind="kde", hue='Condition', vars=['a', 'b', 'c', 'd', 'LL', 'conv'],
                 plot_kws=dict(s=5, linewidth=0),
                 diag_kws=dict(shade=True))

    # Shuffle positions to show legend
    plt.tight_layout(w_pad=3)

    # Draw plot
    plt.show()


def dose_response_plot(drugs, log=False):
    # Takes in a list of drugs
    # Makes 1*num(parameters) plots for each drug
    # Read in dataframe and reduce sample
    df = pd.concat(map(lambda x: read_dataset(x)[1], list(range(3,14))))
    print(df.columns)
    df = df.sample(2000)

    params = ['div', 'b', 'c', 'd', 'confl_conv', 'std']
    
    # Make plots for each drug
    f, axis = plt.subplots(len(drugs),6,figsize=(15,2.5*len(drugs)), sharex=False, sharey='col')
    for drug in drugs:
        # Set up table for the drug
        dfd = df[df['Condition'].str.contains(drug+' ')]
        # Break if drug not in dataset
        if dfd.empty:
            print("Error: Drug not in dataset")
            break 

        # Add dose to table
        dfd[drug+'-dose'] = dfd['Condition'].str.split(' ').str[1]
        dfd[drug+'-dose'] = dfd[drug+'-dose'].convert_objects(convert_numeric=True)
        
        # Set up mean and confidence interval
        if log == True:
            for param in params:
                dfd[param] = np.log(dfd[param])
        dfmean = dfd.groupby([drug+'-dose'])[params].mean().reset_index()
        dferr1 = dfmean-dfd.groupby([drug+'-dose'])[params].quantile(0.05).reset_index()
        dferr2 = dfd.groupby([drug+'-dose'])[params].quantile(0.95).reset_index()-dfmean

        # Plot params vs. drug dose
        j = drugs.index(drug)
        for i in range(len(params)):
            axis[j,i].errorbar(dfmean[drug+'-dose'],dfmean[params[i]],
                               [dferr1[params[i]],dferr2[params[i]]],
                               fmt='.',capsize=5,capthick=1)
            axis[j,i].set_xlabel(drug+'-dose')
            axis[j,i].set_ylabel(params[i])

    plt.tight_layout()
    plt.show()


def violinplot(drugs,log=False):
    '''
    Takes in a list of drugs
    Makes 1*num(parameters) boxplots for each drug
    '''
    import seaborn as sns
    df = pd.concat(map(lambda x: read_dataset(x)[1], list(range(3,14))))
    df = df.sample(2000)

    params = ['div', 'b', 'c', 'd', 'confl_conv', 'std']
    
    # Make plots for each drug
    f, axis = plt.subplots(len(drugs),6,figsize=(18,3*len(drugs)), sharex=False, sharey='col')
    for drug in drugs:
        # Set up table for the drug
        dfd = df[df['Condition'].str.contains(drug+' ')]
        # Break if drug not in dataset
        if dfd.empty:
            print("Error: Drug not in dataset")
            break 

        # Add dose to table
        dfd[drug+'-dose'] = dfd['Condition'].str.split(' ').str[1]
        dfd[drug+'-dose'] = dfd[drug+'-dose'].convert_objects(convert_numeric=True)

        # Plot params vs. drug dose
        j = drugs.index(drug)
        for i in range(len(params)):
            if log == True:
                sns.violinplot(dfd[drug+'-dose'],np.log(dfd[params[i]]),ax=axis[j,i])
            else:
                sns.violinplot(dfd[drug+'-dose'],dfd[params[i]],ax=axis[j,i])

    plt.tight_layout()
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
