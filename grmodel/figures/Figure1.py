"""
This creates Figure 1.
"""

import pandas as pd
import numpy as np
import scipy as sp
import numpy_indexed as npi


def plot_mean_and_CI(_x, _y, confidence, ax):
    """ Plot the mean value and confidence interval """
    # Group _y by _x and find the mean, standard deviation of _y at each _x
    x_unique, y_mean = npi.group_by(_x).mean(_y)
    y_std = npi.group_by(_x).std(_y)[1]
    sample_size = npi.count(_x)[1]
    yerr = []  # a list to store the confidence interval
    for i, item in enumerate(sample_size):
        yerr.append((y_std[i] / np.sqrt(item)) * sp.stats.t._ppf((1 + confidence) / 2., item - 1))
    ax.errorbar(x=x_unique, y=y_mean, yerr=yerr, fmt='.', color='black')


def plot_median_and_quantile(_df, xvar, yvar, ax, c='b', quantiles=[0.90, 0.75, 0.50], lb=None):
    """ Plot the median, low and high quantile """
    _x = _df[xvar].tolist()
    _y = _df[yvar].tolist()
    x_unique, y_median = npi.group_by(_x).median(_y)
    x_unq = _df.groupby(xvar)

    if(lb is None):
        ax.plot(x_unique, y_median, color=c, linewidth=1, alpha=0.9)
    else:
        ax.plot(x_unique, y_median, color=c, linewidth=1, alpha=0.9, label=lb)

    alphas = [0.2, 0.3, 0.5]
    for i in range(len(quantiles)):
        y_low = np.array(x_unq.quantile((1 - quantiles[i]) / 2)[yvar].tolist())
        y_high = np.array(x_unq.quantile(1 - (1 - quantiles[i]) / 2)[yvar].tolist())
        if(lb is not None):
            ax.fill_between(x_unique, y_high, y_low, color=c, alpha=alphas[i])
        else:
            ax.fill_between(x_unique, y_high, y_low, color=c, alpha=alphas[i], label=str(int(quantiles[i] * 100)) + '% CI')


def plot_exact_data(M, ax2, ax3):
    """ Plot the data provided """
    X = np.array(M.drugCs)
    lObs = np.array(M.lObs)
    # Figure C: plot the mean and 95% CI of lObs at each concentration X
    plot_mean_and_CI(X, lObs, 0.95, ax2)
    ax2.set_xlabel(r'$\mathregular{log_{10}}$[DOX(nM)]')
    ax2.set_ylabel(r'Cell viability' + '\n' + r'normalized to untreated cells')
    ax2.set_ylim(0, 1.1)
    # Part of Figure D: Compare the sampling lExp with the exact data lObs
    plot_mean_and_CI(X, lObs, 0, ax3)


def df_crossjoin(df1, df2, **kwargs):
    """
    Make a cross join (cartesian product) between two dataframes by using a constant temporary key.
    Also sets a MultiIndex which is the cartesian product of the indices of the input dataframes.
    See: https://github.com/pydata/pandas/issues/5401
    :param df1 dataframe 1
    :param df1 dataframe 2
    :param kwargs keyword arguments that will be passed to pd.merge()
    :return cross join of df1 and df2
    """
    df1['_tmpkey'] = 1
    df2['_tmpkey'] = 1

    res = pd.merge(df1, df2, on='_tmpkey', **kwargs).drop('_tmpkey', axis=1)
    res.index = pd.MultiIndex.from_product((df1.index, df2.index))

    df1.drop('_tmpkey', axis=1, inplace=True)
    df2.drop('_tmpkey', axis=1, inplace=True)

    return res


def plot_sampling_data(df, ax3, ax4, ax5, ax6):
    """ Check that MCMC actually fit the data provided """
    # Define drug concentrations x to test MCMC sampling data fit
    df1 = df_crossjoin(df, pd.DataFrame({'concentration': np.arange(-1.0, 3.0, 0.01)}))

    # Drug term since we're using constant IC50 and hill slope
    df1['drugTerm'] = 1.0 / (1.0 + np.power(10.0, (df1['IC50s'] - df1['concentration']) * df1['hill']))

    # Minimum drug term
    df1['controlDrugTerm'] = 1.0 / (1.0 + np.power(10.0, (df1['IC50s'] - np.min(df1['concentration'])) * df1['hill']))

    # growthV = Emin_growth + (Emax_growth - Emin_growth) * drugTerm
    df1['growthV'] = df1['Emax_growth'] + ((df1['Emin_growth'] - df1['Emax_growth']) * df1['drugTerm'])

    # Control growth rate
    df1['growthControl'] = df1['Emax_growth'] + ((df1['Emin_growth'] - df1['Emax_growth']) * df1['controlDrugTerm'])

    # Range of growth effect
    df1['growthRange'] = df1['Emax_growth'] - df1['Emin_growth']

    # _Assuming deathrate in the absence of drug is zero
    # deathV = Emax_death * drugTerm
    df1['deathV'] = df1['Emax_death'] * df1['drugTerm']

    # Calculate the growth rate
    df1['GR'] = df1['growthV'] - df1['deathV']

    # Calculate the number of live cells, normalized to T=0
    df1['lExp'] = np.exp(df1['GR'] * 72.0 - df1['growthControl'] * 72.0)

    # Figure D: Plot the median, 90% and 50% quantile of the expected number
    # of live cells at each x
    plot_median_and_quantile(df1, 'concentration', 'lExp', ax3)
    ax3.set_xlabel(r'$\mathregular{Log_{10}}$[DOX(nM)]')
    ax3.set_ylabel('Fit CellTiter quantitation')
    ax3.set_ylim(0, 1.05)
    ax3.legend(loc=6)

    # Figure E: Plot the median, 90% and 50% quantile of growth rate at each x
    plot_median_and_quantile(df1, 'concentration', 'growthV', ax4)
    ax4.set_xlabel(r'$\mathregular{Log_{10}}$[DOX(nM)]')
    ax4.set_ylabel('Predicted growth rate (1/min)')
    ax4.set_ylim(0., ax4.get_ylim()[1])
    ax4.legend(loc=6)

    # Figure F: Plot the median, 90% and 50% quantile of growth rate at each x
    plot_median_and_quantile(df1, 'concentration', 'deathV', ax5)
    ax5.set_xlabel(r'$\mathregular{Log_{10}}$[DOX(nM)]')
    ax5.set_ylabel('Predicted death rate (1/min)')
    ax5.legend(loc=6)

    # Figure G: Plot growth rate vs. death rate
    ax6.scatter(x=df['Emax_growth'] - df['Emin_growth'],
                y=df['Emax_death'], color='b', s=1)
    ax6.set_xlim(0., df['Emax_growth'][0])
    ax6.set_ylim(0., 0.03)
    ax6.set_xlabel('Drug growth effect (1/min)')
    ax6.set_ylabel('Drug death effect (1/min)')


def plot_PCA(df, ax):
    """ Check the dimensionality of the sampling uncertainty using PCA """
    from sklearn.decomposition import PCA

    # Separating out the features
    m = df.values

    pca = PCA(n_components=5)
    pcs = pca.fit_transform(m)

    # print out explained_variance
    print(pca.explained_variance_ratio_)

    # Scatter plot of PC1 vs. PC2
    ax.scatter(pcs[:, 0], pcs[:, 1], s=2)
    ax.set_xlabel('Principal Component 1')
    ax.set_ylabel('Principal Component 2')

    # TODO: Plot PCA's loadings


def alphaFig(M, ax1):
    drug_lnum_effect = 0.25

    # alpha = (R_g0 - R_gd) / R_dD ---- R_d0 is 0
    # -ln(drug_lnum_effect) / t = (1 + alpha) R_dD

    alpha = np.logspace(-2, 2)
    R_dD = -np.log(drug_lnum_effect) / M.time / (1 + alpha)
    R_gD = M.Emax_growth - R_dD * alpha

    cellDiv = R_gD * 72.
    deadCells = R_dD * (np.exp((R_gD - R_dD) * 72.) - 1) / (R_gD - R_dD)

    ax1.semilogx(alpha, deadCells, label="cum. # dead")
    ax1.set_xlabel(r'$\alpha$ (ratio growth to death effect)')
    ax1.set_ylabel('Quantity per starting cell')
    ax1.semilogx(alpha, cellDiv, 'r', label="avg. divisions")
    ax1.legend(handlelength=0.5)


def makeFigure():
    '''
    Generate Figure 1
    Broadly, this figure should motivate looking at cell death.
    This should be by showing that it's not captured in existing
    measurements.
    '''
    from matplotlib.ticker import FormatStrFormatter
    from ..pymcDoseResponse import doseResponseModel
    from .FigureCommon import getSetup, subplotLabel
    from string import ascii_uppercase

    M = doseResponseModel()
    M.readSamples()

    # Store the sampling data for priors to calculate the lExp, growthV and deathV at each concentration
    df = pd.DataFrame({'IC50s': M.trace['IC50s'],
                       'hill': M.trace['hill'],
                       'Emin_growth': M.trace['Emin_growth'],
                       'Emax_death': M.trace['Emax_death']})
    df['Emax_growth'] = M.Emax_growth

    # Get list of axis objects
    ax, f, _ = getSetup((7, 6), (3, 3))

    for axis in ax[0:9]:
        axis.grid(linestyle='dotted', linewidth=1.0)  # set grid style
        axis.tick_params(axis='both', which='major', pad=-2)  # set ticks style

    # set significant figures for xtick
    ax[3].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax[4].yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
    ax[5].yaxis.set_major_formatter(FormatStrFormatter('%.3f'))

    # Going to put a cartoons in A and B
    ax[0].axis('off')
    ax[1].axis('off')

    plot_exact_data(M, ax[2], ax[3])
    plot_sampling_data(df, ax[3], ax[4], ax[5], ax[6])
    plot_PCA(df, ax[7])
    alphaFig(M, ax[8])

    # Make first cartoon
    for ii, item in enumerate(ax):
        subplotLabel(item, ascii_uppercase[ii])

    # Try and fix overlapping elements
    f.tight_layout()

    return f
