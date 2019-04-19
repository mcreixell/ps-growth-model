fdir = ./Manuscript/Figures
tdir = ./Manuscript/Templates
pan_common = -s -F pandoc-crossref -F pandoc-citeproc --filter=$(tdir)/figure-filter.py -f markdown ./Manuscript/Text/*.md

.PHONY: clean test profile testcover all doc

all: $(fdir)/Figure1.pdf $(fdir)/Figure2.pdf $(fdir)/Figure3.pdf $(fdir)/Figure4.pdf $(fdir)/Figure5.pdf $(fdir)/FigureS1.pdf $(fdir)/FigureS2.pdf $(fdir)/FigureS3.pdf $(fdir)/FigureS4.pdf $(fdir)/FigureS5.pdf

$(fdir)/Figure%.svg: genFigures.py
	mkdir -p ./Manuscript/Figures
	python3 genFigures.py $*

$(fdir)/Figure%pdf: $(fdir)/Figure%svg
	rsvg-convert -f pdf $< -o $@

grmodel/data/030317-2_H1299_samples.pkl: 
	curl -LSso $@ https://www.dropbox.com/s/bh8swc75kk0z3b6/030317-2_H1299_samples.pkl?dl=0

grmodel/data/111717_PC9_samples.pkl: 
	curl -LSso $@ https://www.dropbox.com/s/z1xce0kwafa612a/111717_PC9_samples.pkl?dl=0

grmodel/data/101117_H1299_ends_samples.pkl: 
	curl -LSso $@ https://www.dropbox.com/s/eiwyq8pi67qut09/101117_H1299_ends_samples.pkl?dl=0

grmodel/data/030317-2-R1_H1299_samples.pkl: 
	curl -LSso $@ https://www.dropbox.com/s/a0al7xal2g6hpcd/030317-2-R1_H1299_samples.pkl?dl=0

grmodel/data/062117_PC9_samples.pkl: 
	curl -LSso $@ https://www.dropbox.com/s/1tdur7ljesn7thg/062117_PC9_samples.pkl?dl=0

grmodel/data/111717_PC9_ends_samples.pkl: 
	curl -LSso $@ https://www.dropbox.com/s/8c1xj33chlhn7tw/111717_PC9_ends_samples.pkl?dl=0

clean:
	rm -f ./Manuscript/Manuscript.* ./Manuscript/index.html $(fdir)/Figure*
	rm -rf doc/build/* doc/build/.doc* doc/build/.build* doc/source/grmodel.* doc/source/modules.rst

dataclean:
	rm -f grmodel/data/*.pkl

sampleDose:
	python3 -c "from grmodel.pymcDoseResponse import doseResponseModel; M = doseResponseModel(); M.sample()"

test:
	nosetests3 --with-timer

testprofile:
	nosetests3 --with-timer --with-cprofile --cprofile-stats-erase

testcover:
	nosetests3 --with-xunit --with-xcoverage --cover-package=grmodel -s --with-timer

profile:
	python3 -c "from grmodel.pymcGrowth import GrowthModel; grM = GrowthModel(); grM.importData(3); grM.model.profile(grM.model.logpt).summary()"

doc:
	sphinx-apidoc -o doc/source grmodel
	sphinx-build doc/source doc/build
