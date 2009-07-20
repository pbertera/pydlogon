@ECHO OFF
REM ******************** TEMPORARY LOGIN SCRIPT **********************


REM **************************** SET TIME ****************************

net time \\cosmo /set /yes

REM **************************** SET PROXY ***************************

Regedit /s \\cosmo\netlogon\dlogon\commo-files\setpxy.reg
Regedit /s \\cosmo\netlogon\dlogon\common-files\my-reg.reg


