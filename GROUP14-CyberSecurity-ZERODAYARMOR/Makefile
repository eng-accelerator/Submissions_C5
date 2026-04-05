.PHONY: install format lint test run clean

install:
	pip install -r requirements.txt

format:
	black agents/ tools/ rag/ schemas/ tests/ app.py orchestrator.py

lint:
	flake8 agents/ tools/ rag/ schemas/ tests/ app.py orchestrator.py --max-line-length=150 --ignore=E501,W293,E402,F401,F841,E226,W503,W504

test:
	pytest tests/ -v

run:
	@if [ "$(tunnel)" = "true" ]; then \
		python start_cloudflare_tunnel.py; \
	else \
		streamlit run app.py; \
	fi

deploy:
	python start_cloudflare_tunnel.py

clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete
	rm -rf .pytest_cache
