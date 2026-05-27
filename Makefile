build:
	docker build -t docker_flask_project .

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

fast:
	docker-compose down -v 
	docker-compose up --build

logs-compose:
	docker-compose logs -f
	docker-compose logs -f web
