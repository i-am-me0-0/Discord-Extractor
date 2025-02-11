@echo off
:: Turn off command echoing to keep console clean
:: Only final commands and outputs will be displayed

echo Starting HTTP server... 

setlocal
:: Create a local environment for this script
:: Any environment changes will be discarded when script ends

cd Webpage
:: Change directory to where server.py is located
:: This becomes our working directory for the server

..\python\python.exe server.py
:: Execute python.exe from the parent directory's python folder
:: The .. notation means "go up one directory level"
:: This keeps Python separate from the Program directory while allowing execution

cd ..
:: Move back up one directory level to where we started
:: Returns us to the original batch file location

pause
:: Keep console window open after completion
:: Allows viewing of any output or error messages