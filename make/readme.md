# Create a windows executeable + installer

 pip install -r requirements-dev.txt

 pyinstaller .\make\main.spec

 Use inno setup to create an installer of the exe + img and ui folder
 bot_installer.iss

 ---
 Todo:  
  Use main.spec to gather required files to run exe
  Test in VM

  https://www.mfitzp.com/article/packaging-pyqt5-apps-with-fbs/