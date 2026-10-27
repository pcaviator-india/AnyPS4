@echo off
set "JAVA_HOME=C:\Program Files\Android\Android Studio\jbr"
set "PATH=%JAVA_HOME%\bin;%PATH%"
call "C:\PersonalProjects\ghidra\ghidra_12.1.4_PUBLIC\support\analyzeHeadless.bat" "C:\PersonalProjects\ghidra_proj" "TempProject" -process "eboot.elf" -noanalysis -scriptPath "C:\PersonalProjects\AnyPs4\tools-fetch" -postScript "DumpCallSites.java"
