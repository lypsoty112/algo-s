PYTHON_PATH =  ./.venv/scripts/python.exe

main: 
	@$(PYTHON_PATH) main.py

docker: 
	docker compose --env-file ./.env.docker up -d

docker.build:
	docker compose build --no-cache

docker.down:
	docker compose down

docker.clean:
	docker image prune
