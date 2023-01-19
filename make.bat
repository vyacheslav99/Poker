rd /s /q build
del /q dist\poker.exe
pipenv run pyinstaller --noconfirm --onefile --windowed --icon "resources/app.ico" --name "poker" --log-level "INFO" "poker.py"