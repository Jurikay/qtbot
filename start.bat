@echo off
cd %UserProfile%\qtbot
git pull
pip install pipenv
pipenv install --requirements
pipenv shell
start pythonw MAIN.pyw
exit