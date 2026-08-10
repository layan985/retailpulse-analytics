all:
	python -m src.retailpulse.generate
	python -m src.retailpulse.pipeline
	python -m src.retailpulse.analyze
	python -m src.retailpulse.ml
	pytest -q
