import numpy as np
import pandas as pd
from scipy.optimize import brentq


def drug(IC, X, EE):
    """ Define a component of concentration-effect function for drug_n """
    return np.multiply(X, np.divide(np.power(EE, np.reciprocal(IC[1])), IC[0]))


def drugs(E, IC1, IC2, a, E_con, X1, X2):
    """ Define a component of concentration-effect function for multiple drugs """
    EE = (E_con - E) / E
    singleEffect = drug(IC1, X1, EE) + drug(IC2, X2, EE) - 1.0
    innerTerm = np.divide(np.reciprocal(IC1[1]) + np.reciprocal(IC2[1]), 2.0)

    return singleEffect + ((a * X1 * X2) / (IC1[0] * IC2[0])) * np.power(EE, innerTerm)


def concentration_effect(IC1, IC2, a, E_con, X1, X2):
    """ Define the concentration-effect function. """
    args = (IC1, IC2, a, E_con, X1, X2)
    low, high = np.array(1.E-8), np.array(E_con*0.999)

    flow, fhigh = drugs(low, *args), drugs(high, *args)

    if flow * fhigh > 0.0:
        if np.abs(flow) < np.abs(fhigh) and np.abs(flow) < 1.0E-5:
            return low
        elif np.abs(flow) > np.abs(fhigh) and np.abs(fhigh) < 1.0E-5:
            return high

        return np.nan

    # Solve for E using the Newton's method
    return brentq(drugs, low, high, args, xtol=1.0E-34)


def load_data(IC1, IC2, a, E_con, X1range, X2range, df, appendVar):
    """
        Load Data in dataframe
        IC = [IC50, hill]
        X1, X2: drug concentration for drug 1 and drug 2
        df: save the values to dataframe df
        appendVar: the name of the variables that will be added to df
    """
    w, h = len(X2range), len(X1range)
    M = [[0 for x in range(w)] for y in range(h)]
    append_df = pd.DataFrame()

    for i, X1 in zip(range(h), X1range):
        for j, X2 in zip(range(w), X2range):
            M[i][j] = concentration_effect(IC1, IC2, a, E_con, X1, X2)
        temp_df = pd.DataFrame({appendVar: M[i]})
        append_df = append_df.append(temp_df, ignore_index=True)

    df[appendVar] = append_df
    return df


def plot_2D(df, x, y):
    """ Plot 2D graph, i.e., X1 vs E, by keeping X2 as constant """
    import matplotlib.pyplot as plt

    plt.plot(df[x], df[y])
    plt.xlabel(x)
    plt.ylabel(y)


def makeAdditiveData(t=72.0, a=0.0, E_con=1.0):
    """ Generate data from a situation we know is additive, for later fitting. """
    X1range = np.arange(1.00, 4.00, 0.02)
    X2range = np.arange(1.00, 2.00, 0.01)
    df = pd.DataFrame()

    # load X1 and X2 into dataframe df
    for i, X1 in zip(range(len(X1range)), X1range):
        temp_df = pd.DataFrame({'X1': [X1range[i]] * len(X2range),
                                'X2': X2range})
        df = df.append(temp_df, ignore_index=True)

    # load div into df
    # When the value of hill is positive, brentq does not work
    # Raise Error: ValueError: f(a) and f(b) must have different signs
    # IC_div_X1 = [0.5, 1.0]
    IC_div_X1 = [0.5, -1.0]
    IC_div_X2 = [0.6, -2.0]
    df = load_data(IC_div_X1, IC_div_X2, a, E_con, X1range, X2range, df, 'div')

    # load deathRate into df
    IC_DR_X1 = [0.4, -1.0]
    IC_DR_X2 = [0.7, -2.0]
    df = load_data(IC_DR_X1, IC_DR_X2, a, E_con, X1range, X2range, df, 'deathRate')

    # Calculate lnum based on the formula: lnum = exp((div - deathRate) * t)
    # load lnum into df
    df['lnum'] = np.exp((df['div'] - df['deathRate']) * t)

    return df
