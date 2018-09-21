"""
This module handles experimental data for drug interaction.
"""
import numpy as np
import pymc3 as pm
import theano.tensor as T
from .pymcGrowth import theanoCore, convSignal, conversionPriors


def theanoCorr(a, b):
    a, b = T.flatten(a), T.flatten(b)
    a_centered, b_centered = a - a.mean(), b - b.mean()
    r_num = T.dot(a_centered, b_centered)
    r_den = T.sqrt(T.dot(a_centered, a_centered) * T.dot(b_centered, b_centered))

    return r_num / r_den


def blissInteract(X1, X2, hill, IC50):
    drug_one = T.pow(X1, hill[0]) / (T.pow(IC50[0], hill[0]) + T.pow(X1, hill[0]))
    drug_two = T.pow(X2, hill[1]) / (T.pow(IC50[1], hill[1]) + T.pow(X2, hill[1]))
    return drug_one + drug_two - drug_one*drug_two


def build_model(X1, X2, timeV, conv0=0.1, confl=None, apop=None, dna=None):
    ''' Builds then returns the pyMC model. '''

    assert(X1.shape == X2.shape)

    growth_model = pm.Model()

    with growth_model:
        conversions = conversionPriors(conv0)

        # Rate of moving from apoptosis to death, assumed invariant wrt. treatment
        d = pm.Lognormal('d', np.log(0.01), 1)

        # hill coefs for drug 1, 2; assumed to be the same for both phenotype
        hill_growth = pm.Lognormal('hill_growth', 0.0, 0.1, shape=2)
        hill_death = pm.Lognormal('hill_death', 0.0, 0.1, shape=2)

        # IL50 for drug 1, 2; assumed to be the same for both phenotype
        IC50_growth = pm.Lognormal('IC50_growth', -1., 1., shape=2)
        IC50_death = pm.Lognormal('IC50_death', -1., 1., shape=2)

        # E_con values; first death then growth
        E_con = pm.Lognormal('E_con', -1., 1., shape=2)

        # Fraction of dying cells that go through apoptosis
        apopfrac = pm.Beta('apopfrac', 2., 2.)

        # Calculate the death rate
        death_rates = E_con[0] * blissInteract(X1, X2, hill_death, IC50_death)

        # Calculate the growth rate
        growth_rates = E_con[1] * (1 - blissInteract(X1, X2, hill_growth, IC50_growth))

        # Test the dimension of growth_rates
        growth_rates = T.opt.Assert('growth_rates did not match X1 size')(growth_rates, T.eq(growth_rates.size, X1.size))

        lnum, eap, deadapop, deadnec = theanoCore(timeV, growth_rates, death_rates, apopfrac, d)

        # Test the size of lnum
        lnum = T.opt.Assert('lnum did not match X1*timeV size')(lnum, T.eq(lnum.size, X1.size*timeV.size))

        confl_exp, apop_exp, dna_exp = convSignal(lnum, eap, deadapop, deadnec, conversions)

        # Compare to experimental observation
        if confl is not None:
            confl_obs = T.flatten(confl_exp - confl)
            pm.Deterministic('confl_corr', theanoCorr(confl_exp, T._shared(confl)))
            pm.Normal('confl_fit', sd=T.std(confl_obs), observed=confl_obs)

        if apop is not None:
            apop_obs = T.flatten(apop_exp - apop)
            pm.Deterministic('apop_corr', theanoCorr(apop_exp, T._shared(apop)))
            pm.Normal('apop_fit', sd=T.std(apop_obs), observed=apop_obs)

        if dna is not None:
            dna_obs = T.flatten(dna_exp - dna)
            pm.Deterministic('dna_corr', theanoCorr(dna_exp, T._shared(dna)))
            pm.Normal('dna_fit', sd=T.std(dna_obs), observed=dna_obs)

        pm.Deterministic('logp', growth_model.logpt)

    return growth_model
