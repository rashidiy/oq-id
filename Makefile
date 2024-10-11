extract:
	@test -d translations || mkdir translations
	pybabel extract -o translations/messages.pot .

init:
	pybabel init -i translations/messages.pot -d translations -l $(lang)

compile:
	pybabel compile -d translations

mig:
	alembic revision --autogenerate
	alembic upgrade head