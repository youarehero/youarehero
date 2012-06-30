dirs:
	install -d -m 0755 coverage
	install -d -m 0755 media 
env:
	python virtualenv.py --distribute --no-site-packages env
deps:
	. env/bin/activate && pip install -r deploy/requirements.txt
clean:
	rm -f env
syncdb:
	. env/bin/activate && src/manage.py syncdb
migrate:
	. env/bin/activate && src/manage.py migrate
static:
	rm -rf static
	install -d -m 0755 static 
	. env/bin/activate && src/manage.py collectstatic
test:
	. env/bin/activate && src/manage.py test

bootstrap: dirs env deps static syncdb migrate test


