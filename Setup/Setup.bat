@echo.
@echo.
@echo ********************Initial Project SetUp has began***********************
@echo off
start cmd /k mongod
pip install pymongo
pip install flask
pip install tweepy
pip install openpyxl
mongoimport --db tweetsDB --collection xboxone --type json --file xboxone.json
mongoimport --db tweetsDB --collection galaxys6 --type json --file galaxys6.json
pause