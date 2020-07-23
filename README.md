# PostreSQL-Monitor
This is a simple script that aims to be able to diagnose heavy SQL queries and show them in an easy to understand manner 

### What does it do ?
The script will display queries that :
- are the most called
- required the most accumulated time for all usages
- required the most time for one usage
- required the most time on average
- returned the most rows with one usage
For each of these criteria, the 10 queries that had the biggest result are displayed

### How to use
This script was designed to be either used as a command line or for a slack / discord bot and can also write to a file<br/>
Using it as a bot allows for daily / hourly / ... health checks of your database

### Troubleshooting
Should this script not work, please make sure that :
- make sure that the postgresql is correctly configured as shown here : https://gist.github.com/troyk/4462899
- the chosen file name is correct with write permissions
- the connection string is correct ( host + database name + user + password )

Should it still not work, please set the console display ( writeOnConsole ) to True in order to see any other possible errors<br/>
Details on the working of this table here : https://www.postgresql.org/docs/9.6/static/pgstatstatements.html

script author : Matthieu Raynaud de Fitte

### Example output :
The following output was obtained with the following instruction : `"dbname=test_database user=user password=my-password host=127.0.0.1 port=5432" all 10`<br />

     =========
    Queries that where the most used by amount
     =========
    
    Query id :    2397681704071010949 => 15       | avg time : 0.0000ms Query : BEGIN
    Query id :    3694949039461716331 => 8        | avg time : 0.0000ms Query : COMMIT
    Query id :   -5232434073356610674 => 1        | avg time : 0.0007ms Query : SELECT d.datname as "Name", pg_catalog.pg_get_userbyid(d ...
    Query id :    4346420983535608038 => 1        | avg time : 0.0005ms Query : select * from test

     =========
    Queries that required the most time accumulated
     =========
    
    Query id :   -5232434073356610674 => 0.0007ms   | 1 call Query : SELECT d.datname as "Name", pg_catalog.pg_get_userbyid(d ...
    Query id :    4346420983535608038 => 0.0005ms   | 1 call Query : select * from test
    Query id :    2397681704071010949 => 0.0001ms   | 15 calls Query : BEGIN
    Query id :    3694949039461716331 => 0.0001ms   | 8 calls Query : COMMIT
    
     =========
    Queries that required the most time per use on average
     =========
    
    Query id :   -5232434073356610674 => 0.0007ms   | 1 call Query : SELECT d.datname as "Name", pg_catalog.pg_get_userbyid(d ...
    Query id :    4346420983535608038 => 0.0005ms   | 1 call Query : select * from test
    Query id :    3694949039461716331 => 0.0000ms   | 8 calls Query : COMMIT
    Query id :    2397681704071010949 => 0.0000ms   | 15 calls Query : BEGIN
    
     =========
    Queries that returned the most rows on average
     =========
    
    Query id :    4346420983535608038 => 27         | 1 call Query : select * from test
    Query id :   -5232434073356610674 => 4          | 1 call Query : SELECT d.datname as "Name", pg_catalog.pg_get_userbyid(d ...
    Query id :    3694949039461716331 => 0          | 8 calls Query : COMMIT
    Query id :    2397681704071010949 => 0          | 15 calls Query : BEGIN
    
     =========
    Queries that returned the most rows accumulated
     =========
    
    Query id :    4346420983535608038 => 27         | 1 call Query : select * from test
    Query id :   -5232434073356610674 => 4          | 1 call Query : SELECT d.datname as "Name", pg_catalog.pg_get_userbyid(d ...
    Query id :    3694949039461716331 => 0          | 8 calls Query : COMMIT
    Query id :    2397681704071010949 => 0          | 15 calls Query : BEGIN


