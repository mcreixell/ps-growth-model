"""
This module handles reading drug combination data.
"""
import re
from os.path import join, dirname, abspath
import numpy as np
import pandas as pd


def readCombo(name="072718_PC9_BYL_PIM"):
    """ Read in data file, melt each table across conditions, and then merge all measurements into one table. """
    filename = join(dirname(abspath(__file__)), "data/combinations/" + name + "_rawdata.xlsx")

    data = pd.read_excel(filename, sheet_name=None)

    del data["Conditions"]

    for key in data:
        data[key]["Well"] = np.repeat([1, 2, 3], 25)
        data[key] = pd.melt(data[key], id_vars=["Elapsed", "Well"], var_name="Condition", value_name="Measure")
        data[key].dropna(inplace=True)

    data = pd.concat(data).reset_index().drop(["level_1"], axis=1)

    data[["Type", "drug_amt"]] = data["level_0"].str.split("_", 1, expand=True)

    data.drop(["level_0"], axis=1, inplace=True)

    return data


def filterDrugC(df, drugAname, drugBname):
    df["drugA"] = 0

    for index, row in df.iterrows():
        m = re.search(drugAname + r" (\d*\.?\d*)", row["Condition"])

        if m is not None:
            df.loc[index, "drugA"] = float(m.group(1))

    df["drugB"] = 0

    for index, row in df.iterrows():
        m = re.search(drugBname + r" (\d*\.?\d*)", row["Condition"])

        if m is not None:
            df.loc[index, "drugB"] = float(m.group(1))

    df.loc[df["Condition"] == "blank", ["drugA", "drugB"]] = np.nan
    df.drop("Condition", axis=1, inplace=True)

    return df


def dataSplit(df):
    """ This will pull out the data """
    keepCols = ["drugA", "drugB", "Elapsed", "Measure", "Type"]
    grpCols = ["Elapsed", "drugA", "drugB", "Type"]
    df.dropna(inplace=True)

    timeV = np.sort(np.array(df.Elapsed.unique(), dtype=np.float64))

    dfGrp = df[keepCols].groupby(grpCols).agg({"Measure": "mean"}).unstack(0)

    phase = dfGrp.xs('phase', level='Type').values
    dfRED = dfGrp.xs('red', level='Type').values
    dfGreen = dfGrp.xs('green', level='Type').values

    dfRED = dfRED - dfRED[0]  # substract by control
    dfGreen = dfGreen - dfGreen[0]  # substract by control

    X1 = dfGrp.index.get_level_values('drugA').values + 0.01
    X2 = dfGrp.index.get_level_values('drugB').values + 0.01

    assert phase.shape == dfRED.shape == dfGreen.shape

    return (X1, X2, timeV, phase, dfRED, dfGreen)
