PYTHON_PATH =  ./.venv/scripts/python.exe

main: 
	@$(PYTHON_PATH) main.py


docker: 
	docker compose --env-file ./.env.docker up -d --build

docker.build:
	docker compose build

docker.down:
	docker compose down

docker.clean:
	docker image prune
