push:
	git add .
	git commit -m "update"
	git push
pushf:
	git push
setup:
	rm -r venv
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt
update:
	git pull
	pyton3 main.py
start:
	pyton3 main.py
