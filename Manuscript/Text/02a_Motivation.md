## Markers of live cell number are insufficient to distinguish cell growth and death effects

With the notion that cell growth and death are confounded in live cell measurements, we wished to characterize what relationship exists between the uncertainty of each when further information is not available ([@fig:Motivate]A). To do so, we fit a model incorporating both to typical measurements of H1299 dose-response to a chemotherapy doxorubicin ([@fig:Motivate]C). This model was able to confidently fit metrics of dose response when restricted to the live cell number relationship ([@fig:Motivate]D). In contrast, the model showed large uncertainty when it came to the cellular growth or death rates ([@fig:Motivate]E-F).





![**Measures of cell death are critical to quantifying cell response.** A) Schematic of our growth model incorporating cell death. In addition to undergoing exponential growth cells can die at some constant rate. B) ... C) Celltiter Glo measurements of HCC1299 cells treated with doxorubicin at varying concentrations (N = 3). D) Model fit to live cell measurements. E) Model fit and confidence intervals for the predicted growth rate of cells after fitting to measurements of live cell number. F) Model fit and confidence intervals for the predicted death rate. G) Model fit posterior samples of doxorubicin's effect on growth versus its effect on cell death. H) Principal components analysis of the model posterior samples. I) Model predictions and confidence intervals for the rate of cell turnover and cumulative number of dead cells over the course of the experiment.](./Figures/Figure1.svg){#fig:Motivate}

# TODO: Is there a quantity used for selection rate we can use here?