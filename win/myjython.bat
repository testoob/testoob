@echo off
set JYTHON_OPTS=-Dpython.path=src -Dpython.executable="%~f0"
c:\jython2.5a3\bin\jython.bat %*
