:: Activate the conda environment - replace with your environment name
call conda activate universalearn

:loop
:: Run the Python script
python main_module.py

:: Prompt the user for input to determine if the script should run again
set /p continue=Run again? (y/n): 

:: Check if the user input is 'y'
if /i "%continue%"=="y" (
    :: If 'y', repeat the loop
    goto loop
) else (
    :: If not 'y', deactivate the conda environment and exit the script
    call conda deactivate
    exit
)
