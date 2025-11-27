format:
	npm run format
	npm run lint

check:
	npm run lint-check
	npm run type-check
	npm run format-check
	git diff --quiet || (echo "There are uncommitted changes" && exit 1)

build:
	npx vite build --mode development

image:
	docker compose build

types:
	npm run generate-types && npm run generate-zod && npm run type-check