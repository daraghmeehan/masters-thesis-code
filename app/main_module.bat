call conda activate universalearn

:loop
rem Run your code here
python main_module.py

rem Prompt the user for input
set /p continue=Run again? (y/n): 

rem Check user input
if /i "%continue%"=="y" (
    rem Continue the loop
    goto loop
) else (
    call conda deactivate
    exit
)
