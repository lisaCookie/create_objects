build:
	docker build -t docker_flask_project .

sync:
	uv sync

run:
	docker run -d -p 5000:5000 --name my_flask_app docker_flask_project

stop:
	docker stop my_flask_app

kill:
	docker rm my_flask_app

tree:
	tree -I 'node_modules|.venv|__pycache__|.git|.expo' --dirsfirst


logs:
	docker logs my_flask_app

flash:
	docker build -t docker_flask_project .
	docker stop my_flask_app
	docker rm my_flask_app
	docker run -d -p 5000:5000 --name my_flask_app docker_flask_project

down:
	docker-compose down

up:
	docker-compose up


down-up:
	docker-compose down
	docker-compose up --build

clear-build:
	docker-compose down -v
	docker-compose up --build


logs-compose:
	docker-compose logs -f
	docker-compose logs -f web

test:
	coverage run -m pytest tests/ && coverage report

test-admin:
	uv run pytest tests/unit/admin/

test-categories:
	uv run pytest tests/unit/categories/

test-filters:
	uv run pytest tests/unit/utils/

test-integration:
	uv run pytest tests/integration/

lint:
	ruff check .
