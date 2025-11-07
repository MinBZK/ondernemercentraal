check:
	uv run pyright app tests alembic
	uv run ruff check app tests
	uv run ruff format --check
	uv run ruff check --select I --fix-only
	bash validate_json_files.sh ./app
	git diff --quiet || (echo "There are uncommitted changes" && exit 1)	

format:
	uv run ruff check --select I --fix
	uv run ruff format app alembic