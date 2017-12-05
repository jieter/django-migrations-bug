makemigrations:
	./manage.py --version
	./manage.py makemigrations app

migrate:
	dropdb migrate-bug
	createdb migrate-bug
	./manage.py --version
	./manage.py migrate

clean:
	rm -rf app/migrations
