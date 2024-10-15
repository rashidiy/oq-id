extract:
	@test -d translations || mkdir translations
	pybabel extract -o translations/messages.pot .

init:
	pybabel init -i translations/messages.pot -d translations -l $(lang)

compile:
	pybabel compile -d translations

autogenerate:
	alembic revision --autogenerate -m $(m)

upgrade:
	alembic upgrade head

mig:
	make autogenerate m=$(m)
	make upgrade