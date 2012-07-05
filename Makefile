dirs:
	install -d -m 0755 coverage
	install -d -m 0755 media 
env:
	# if env fails a new make should redo the env bootstrap 
	python virtualenv.py  env
deps:
	. env/bin/activate && pip install -r deploy/requirements.txt
test-deps:
	. env/bin/activate && pip install -r deploy/test-requirements.txt
clean:
	rm -f env
syncdb:
	. env/bin/activate && src/manage.py syncdb --noinput
migrate:
	. env/bin/activate && src/manage.py migrate --noinput
static:
	install -d -m 0755 static 
	. env/bin/activate && src/manage.py collectstatic --noinput
test:
	. env/bin/activate && src/manage.py test
bootstrap: dirs env deps static syncdb migrate test

jenkins: dirs env deps test-deps 
	. env/bin/activate && DJANGO_SETTINGS_MODULE=youarehero.settings.jenkins src/manage.py jenkins

deploy: dirs env deps static syncdb migrate test
	service apache2 reload


.PHONY: env syncdb migrate static jenkins deploy
