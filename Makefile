.PHONY: install test lint sample models dashboard demo clean

install:
	pip install -e ".[dev,dbt]"

test:
	pytest -q

lint:
	ruff check .
	ruff format --check .

# Try the whole pipeline offline with synthetic data.
sample:
	LP_DATA_DIR=data london-pulse sample --days 3

models:
	cd dbt && LP_RAW_PATH=../data/raw LP_DUCKDB_PATH=../london_pulse.duckdb dbt build --profiles-dir .

dashboard:
	london-pulse dashboard --db london_pulse.duckdb --out site

demo: sample models dashboard
	@echo "Open site/index.html in your browser."

clean:
	rm -rf data site london_pulse.duckdb dbt/target dbt/logs .pytest_cache .ruff_cache
