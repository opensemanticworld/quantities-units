git:
	@echo "Initializing git..."
	git init
	git switch --create main

git_remote:
	@echo "Adding remote..."
	git remote add origin git@gitlab.cc-asp.fraunhofer.de:ISC/ISC-Digital/osw/apps/python-lvl2/quantities-units
	git add .
	@echo "Committing initially..."
	git commit -m "Auto initial commit"
	@echo "Pushing to remote..."
	git push --set-upstream origin main
	
install: 
	@echo "Installing..."
	poetry install --no-root

activate:
	@echo "Activating virtual environment"
	poetry shell

setup: install git activate

# Remote Setup 
rsetup: install git git_remote activate 

test:
	pytest

docs_serve:
	@echo View API documentation... 
	pdoc src/quantities-units -h localhost -p 5678

docs_save:
	@echo Save documentation to docs... 
	pdoc src/quantities-units -o docs

clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	rm -rf .pytest_cache
	rm -rf poetry.lock
	poetry env remove --all
