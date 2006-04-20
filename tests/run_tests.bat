@ echo off
rem Windows test-running helper
rem %1 should be the python executable to use
@echo on
%1% .\src\testoob\testoob tests\alltests.py suite -i 
