##! /usr/bin/env python3
#
#import matplotlib
#matplotlib.use('Agg')
#
#from grmodel.pymcGrowth import MultiSample
#from grmodel.sampleAnalysis import diagnostics, read_dataset
#
#a = MultiSample()
#
#print(a.loadCols(2))
#a.sample()
#a.save()
#
#cL = read_dataset()
#
#diagnostics(cL)

from grmodel.fitcurves import MultiDrugs
from grmodel.utils import plot_dose_fits 
a = MultiDrugs([4,6,8,10,12], ['Dox'], ['div', 'deathRate'])
a.get_tables()
curves = a.fitCurves()
print(curves)