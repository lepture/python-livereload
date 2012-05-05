.PHONY: clean-pyc clean-build docs

clean: clean-build clean-pyc


clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info


clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

docs:
	$(MAKE) -C docs html
