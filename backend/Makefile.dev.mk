include .env

server:
	uv run fastapi dev app/main.py --port ${FASTAPI_PORT}

harbor_login: 
	kubectl get secret harbor-puller -o jsonpath="{.data.\.dockerconfigjson}" --as=ictu-devops-tab | \
	base64 --decode | \
	docker run --rm -i ghcr.io/jqlang/jq:latest -r '.auths."harbor-gn2.cicd.s15m.nl".auth' | \
	base64 --decode | \
	awk -F: '{print $$1, $$2}' | \
	xargs -I {} sh -c 'echo {} | \
	awk "{print \$$2}" | \
	docker login harbor-gn2.cicd.s15m.nl --username $$(echo {} | awk "{print \$$1}") --password-stdin'	

base_image:
	docker build -t harbor-gn2.cicd.s15m.nl/ictu-devops-pub/${PROJECT_NAME}-base -f Dockerfile.base .

image: base_image version_number
	APP_VERSION=$$(git describe --tags --abbrev=0 || echo "untagged") && echo "Using APP_VERSION from file: $$APP_VERSION" && \
	docker build --no-cache \
	--build-arg BASE_IMAGE=harbor-gn2.cicd.s15m.nl/ictu-devops-pub/${PROJECT_NAME}-base \
	--build-arg APP_VERSION=$$APP_VERSION \
	-t ${PROJECT_NAME} .

run_image_shell: image
	docker run --rm -it ${PROJECT_NAME} /bin/sh

push_base_image: base_image harbor_login
	docker tag harbor-gn2.cicd.s15m.nl/ictu-devops-pub/${PROJECT_NAME}-base harbor-gn2.cicd.s15m.nl/ictu-devops-pub/${PROJECT_NAME}-base:1.4
	docker push harbor-gn2.cicd.s15m.nl/ictu-devops-pub/${PROJECT_NAME}-base:1.4

check_docker:
	docker run --rm -it -v ${PWD}:/app harbor-gn2.cicd.s15m.nl/ictu-devops-pub/${PROJECT_NAME}-base:1.4 make check

clean_db:
	docker compose down db
	docker volume rm ${COMPOSE_PROJECT_NAME}_db
	docker compose up -d db

init_db_migration: clean_db
	uv run alembic revision --autogenerate -m "init"
	uv run alembic upgrade head

test:
	uv run coverage run -m pytest

test_docker: image
	docker run --rm \
		--network oc-backend_default \
		-e SECRET_KEY=dummydummydummydummydummydummy \
		-e POSTGRES_SERVER=db \
		-e POSTGRES_DB=${POSTGRES_DB} \
		-e CLIENT_BASE_URL=http://localhost \
		-e KEYCLOAK_API_CLIENT=http://localhost \
		-e KEYCLOAK_API_SECRET=dummy \
		-e KEYCLOAK_API_URI=http://localhost \
		-e EMAIL_RELAY_HOSTNAME=http://localhost \
		harbor-gn2.cicd.s15m.nl/ictu-devops/${PROJECT_NAME}:ci-test \
		coverage run -m pytest

port_forward_db:
	kubectl port-forward svc/${DB_PROJECT_NAME}-r 5438:5432 --as=ictu-devops-tab
	
backup:
	docker run --rm -i --env PGPASSWORD="${PGPASSWORD_SUPERUSER}" --net=host postgres pg_dump -p 5438 -d ${POSTGRES_DB} -U postgres -h localhost > db/dump.sql

restore_local:
	docker run --rm -i --env PGPASSWORD=${POSTGRES_PASSWORD} --net=host postgres dropdb --if-exists -U ${POSTGRES_USER} -p ${POSTGRES_PORT} -h localhost '${POSTGRES_DB}' -f --if-exists
	docker run --rm -i --env PGPASSWORD=${POSTGRES_PASSWORD} --net=host postgres createdb -U ${POSTGRES_USER} -p ${POSTGRES_PORT} -h localhost '${POSTGRES_DB}'
	docker run --rm -i --env PGPASSWORD=${POSTGRES_PASSWORD} --net=host -v ${PWD}/db/:/db postgres psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -p ${POSTGRES_PORT} -h localhost -f /db/dump.sql		

psql:
	docker run --rm -it \
		--env PGPASSWORD="${POSTGRES_PASSWORD}" \
		--net=host \
		postgres \
		psql \
		-U ${POSTGRES_USER} \
		-d ${POSTGRES_DB} \
		-p ${POSTGRES_PORT} \
		-h ${POSTGRES_SERVER} 		

init_app:
	docker compose down && \
	docker volume rm oc-backend_db && \
	docker compose up -d && \
	sleep 2 && \
	uv run alembic upgrade head && \
	uv run python -m app.scripts.init