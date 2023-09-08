update:
	git add .
	git commit -m "update"
	git push

push:
	git push
setup:
	python3 -m venv venv
	pip install -r requirements.txt