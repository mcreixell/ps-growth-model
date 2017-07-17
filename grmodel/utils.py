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
            os.path.abspath(__file__)), "./data/062117_second_chain.h5")

    # Open hdf5 file
    f = h5py.File(filename, 'r')

    # Close hdf5 file
    f.close()

    # Read in sampling chain
    df = pd.read_hdf(filename, key='column' + str(column) + '/chain')
    
    # Initialize StoneModel
    classM = GrowthModel()
    classM.importData(column)

    # Add the column this came from
    df['Col'] = column
    
    # Unmangle condition names for duplicate columns
    if classM.condName[-2:] == '.1':
        df['Condition'] = classM.condName[:-2]
    else:
        df['Condition'] = classM.condName

    # Remove unlikely points if chosen
    if trim:
        cutoff = np.amin(df['ssqErr'])+20
        df = df.loc[df['ssqErr'] < cutoff,:]

    return (classM, df)


def sim_plot(column, replica = False):
    """ Given column, plots simulation of predictions overlaying observed data """
    # Read in dataset to Pandas data frame
    classM, pdset = read_dataset(column)

    print(pdset.shape)

    print(pdset)

    #Initialize variables 
    if replica:
        time = classM.timeV.reshape(3,int(len(classM.timeV)/3))[0,:]
    else:
        time = classM.timeV 
    calcset = np.full((pdset.shape[0], len(time)), np.inf)
    calcseta = np.full((pdset.shape[0], len(time)), np.inf)
    calcsetd = np.full((pdset.shape[0], len(time)), np.inf)

    varr = 0
    # Evaluate predictions for each set of parameter fits
    for row in pdset.iterrows():
        mparm = np.copy(row[1].as_matrix()[0:4])
        try:
            # Use old_model to calculate lnum, eap, and dead over time
            simret = classM.old_model(mparm, row[1]['confl_conv'], row[1]['apop_conv'], row[1]['dna_conv'])[1]
            if replica:
                simret = simret[:len(time),:]
                simret = simret.reshape((len(time),3))

            # Calculate predictions for total, apop, and dead cells over time
            calcset[varr, :] = np.sum(simret, axis = 1) * row[1]['confl_conv']
            calcseta[varr,:] = np.sum(simret[:,1:3], axis = 1) *row[1]['apop_conv']
            calcsetd[varr,:] = simret[:,2] * row[1]['dna_conv']

            varr = varr + 1
        except:
            print('Failed')
            continue
    
    # Plot prediction distribution and observation
    plt.figure(figsize=(10, 10))
    # Iterate over total, apop, and dead cels
    for calc in [calcset, calcseta, calcsetd]:
        # Get median & 90% confidence interval for each time point
        qqq = np.percentile(calc, [5, 25, 50, 75, 95], axis=0)
        # Plot confidence interval 
        plt.plot(time, qqq[2, :])
        plt.fill_between(time, qqq[1, :], qqq[3, :], alpha=0.5)
        plt.fill_between(time, qqq[0, :], qqq[4, :], alpha=0.2)
    # Plot observation 
    plt.scatter(classM.timeV, classM.expTable['confl'])
    if replica:
        plt.scatter(classM.timeV, classM.expTable['apop']*4)
        plt.scatter(classM.timeV, classM.expTable['dna']*8)
    else:
        plt.scatter(classM.timeV, classM.expTable['apop'])
        plt.scatter(classM.timeV, classM.expTable['dna'])
    plt.show()


def fit_plot(param, column, replica = False):
    '''
    Inputs: param = a list of len(7) in normal space, column = column for corresponding observation
    Plot model prediction overlaying observation
    '''
    # Import an instance of GrowthModel
    classM, _ = read_dataset(column)

    # Initialize variables and parameters 
    if replica:
        ltime = int(len(classM.timeV)/3)
    else:
        ltime = int(len(classM.timeV))
    calcset = np.full((ltime), np.inf)
    calcseta = np.full((ltime), np.inf)
    calcsetd = np.full((ltime), np.inf)
    mparm = param[0:4]

    # Use old model to calculate cells nubmers
    simret = classM.old_model(mparm, param[4], param[5], param[6])[1]
    if replica:
        simret = simret[:ltime,:]
    simret = simret.reshape(ltime,3)

    # Calculate total, apop, and dead cells 
    calcset[:] = np.sum(simret,axis = 1) * param[4]
    calcseta[:] = np.sum(simret[:,1:3], axis = 1) * param[5]
    calcsetd[:] = simret[:,2] * param[6]
    
    # Plot prediction curves overlayed with observation 
    if replica:
        plt.plot(classM.timeV.reshape(3,ltime)[0,:], calcset)
        plt.plot(classM.timeV.reshape(3,ltime)[0,:], calcseta)
        plt.plot(classM.timeV.reshape(3,ltime)[0,:], calcsetd)
    else:
        plt.plot(classM.timeV, calcset)
        plt.plot(classM.timeV, calcseta)
        plt.plot(classM.timeV, calcsetd)
    plt.scatter(classM.timeV, classM.expTable['confl'])
    plt.scatter(classM.timeV, classM.expTable['apop'])
    plt.scatter(classM.timeV, classM.expTable['dna'])
    plt.show()


def hist_plot(cols):
    """
    Display histograms of parameter values across conditions
    """
    import seaborn as sns
    # Read in dataset to Pandas data frame
    df = pd.concat(map(lambda x: read_dataset(x)[1], cols))

    print(df.columns)
    
    # Log transformation
    for param in ['div', 'b', 'c', 'd', 'confl_conv', 'std']:
        df[param] = np.log10(df[param])

    # Main plot organization
    sns.pairplot(df, diag_kind="kde", hue='Condition', vars=['div', 'b', 'c', 'd', 'confl_conv', 'std'],
                 plot_kws=dict(s=5, linewidth=0),
                 diag_kws=dict(shade=True), size = 2)

    # Shuffle positions to show legend
    plt.tight_layout(pad = 0.1)
    plt.legend(bbox_to_anchor=(0, 6.5))

    # Draw plot
    plt.show()


def PCA(cols):
    """
    Principle components analysis of sampling results for parameter values
    """
    from sklearn.decomposition import PCA
    import seaborn as sns

    df = pd.concat(map(lambda x: read_dataset(x)[1], cols))

    print(df.columns)
 
    # Log transformation
    params = ['div', 'b', 'c', 'd', 'confl_conv', 'std']
    for param in params:
        df[param] = np.log10(df[param])

    # Keep columns in params
    dfmain = df.loc[:,params]

    # Run PCA
    pca = PCA(n_components=3)
    pca.fit(dfmain)
    # Get explained variance ratio
    expvar = pca.explained_variance_ratio_
    # Get PCA Scores
    dftran = pca.fit_transform(dfmain)
    dftran = pd.DataFrame(dftran, columns = ['PC 1', 'PC 2', 'PC 3'])
    # Add condition column to PCA scores
    condition = np.asarray(df.loc[:,'Condition'])
    dftran['Conditions'] = condition 

    # Plot first 2 principle components
    ax = sns.lmplot('PC 1', 'PC 2', data = dftran, hue = 'Conditions', fit_reg = False)
    # Set axis labels
    ax.set_xlabels('PC 1 ('+str(round(float(expvar[0])*100, 0))[:-2]+'%)')
    ax.set_ylabels('PC 2 ('+str(round(float(expvar[1])*100, 0))[:-2]+'%)')


def dose_response_plot(drugs, log=False):
    '''
    Takes in a list of drugs
    Makes 1*num(parameters) plots for each drug
    ''' 
    # Read in dataframe
    df = pd.concat(map(lambda x: read_dataset(x)[1], list(range(2,19))))
    print(df.columns)

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
        dfd = dfd.copy()
        dfd[drug+'-dose'] = dfd.loc[:, 'Condition'].str.split(' ').str[1]
        dfd.loc[:, drug+'-dose'] = pd.to_numeric(dfd[drug+'-dose'])
        
        # Set up mean and confidence interval
        if log: 
            for param in params:
                dfd.loc[:, param] = dfd[param].apply(np.log10)
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
    df = pd.concat(map(lambda x: read_dataset(x)[1], list(range(19,36))))

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
        dfd = dfd.copy()
        dfd[drug+'-dose'] = dfd.loc[:, 'Condition'].str.split(' ').str[1]
        dfd.loc[:, drug+'-dose'] = pd.to_numeric(dfd[drug+'-dose'])

        # Plot params vs. drug dose
        j = drugs.index(drug)
        for i in range(len(params)):
            if log: 
                sns.violinplot(dfd[drug+'-dose'],np.log10(dfd[params[i]]),ax=axis[j,i])
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
