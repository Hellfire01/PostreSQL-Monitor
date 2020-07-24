# PostreSQL-Monitor
This is a simple script that aims to be able to diagnose heavy SQL queries and show them in an easy to understand manner 

# What does it do ?
This script was designed to be either used as a command line or for a slack / discord bot and can also write to a file<br/>
The script will display queries that :
- are the most used
- required the most accumulated time for all usages
- required the most time on average
- returned the most rows with one usage
- returned the most rows on average
For each of these criteria, the 10 queries that had the biggest result are displayed

# How to use
First, the database needs to be configured in order to allow the monitoring. This can be done at the following link : <a href='https://gist.github.com/troyk/4462899'>https://gist.github.com/troyk/4462899</a>

Next, the script uses the following library to connect to the database and requires it to work : `psycopg2`

The following instructions use the `monitor_main.py` file but all instructions can be directly given to the `Monitor` class in the same order

The script uses the following arguments : <br/>
authentication string + display instruction(s) + quantity<br/>
or :<br/>
authentication string + query id

The authentication string is just as described in the `psycopg2` documentation<br/>
Example of authentication string :<br />
`"dbname=test user=user password=my-password host=127.0.0.1 port=5432"`

The variables ( can be placed in any order ) are as follow :
- **dbname** => the name of the database you with to diagnose
- **user** => the username
- **password** => the password of the user
- **host** => IP address of the database server
- **port** => port used to connect to the database of the database server

The instructions that can be given are :
- authentication string + query id => Will display the full SQL query of the associated id<br/>
The ids are displayed using any of the other instructions
- authentication string + `mostUsed` + quantity => will show the the most used queries
- authentication string + `longestTimeAccumulated` + quantity => queries that required the most accumulated time
- authentication string + `longestTimeOnAverage` + quantity => queries that required the most time on average
- authentication string + `mostRowsReturnedAccumulated` + quantity => queries that returned the most rows accumulated
- authentication string + `mostRowsReturnedAverage` + quantity => queries that returned the most rows on average
- authentication string + `all` + quantity => will show all of the queries just as if you had call all 5 instructions

`quantity` is a positive integer used for the maximum displayed queries

`query id` is one of the ids displayed by one of the other instructions. It is used to see the entire, indented and non truncated query

**Note** : the previously shown arguments arguments can be used simultaneously. Therefor the following instruction is valid :<br/>
`[authentification string] mostUsed longestTimeOnAverage mostRowsReturnedAccumulated 10`<br/>
It will display just the queries for `mostUsed`, `longestTimeOnAverage` and `mostRowsReturnedAccumulated` one after an other<br/>
Using the same argument twice will not display it twice

**Note** : the queries that are used by this program are not displayed by default. See the configurations variables to display them

# Configuration

The following class instance variables are used to configure the monitor to your needs :
- `useIgnore` ( boolean ) is used to determine if queries possessing the substrings in the `ignore` variable should be ignored or not<br/>
- `ignore` ( string array ) this array of strings / substrings is used to exclude queries from the displayed query list<br/>
By default, the following are ignored : "pg_stat_statements", "pg_catalog", "ALTER TABLE", "TRUNCATE TABLE" and "CREATE TABLE"<br/>
- `writeOnConsole` ( boolean ) to allow ( True ) or forbid ( False ) the monitor to output on the console<br/>
- `writeToFile` ( boolean ) to allow ( True ) or forbid ( False ) the monitor to output on a file<br/>
- `filename` ( string ) is the file name that is used by the monitor ( will be overwritten )<br/>
- `truncatedQuerySize` ( integer ) is used to shorted the query lengths. It is mostly used for long queries or small terminals
- `indentBeforeQuery` and `indentBeforeCalls` ( integer ) are used to insert blank spaces and try to get all the data displayed as neatly as possible <br/>
- `displayUsedQueries` ( boolean ) is used to display the queries that the program is using to gather the displayed data

# Troubleshooting
**Important** : the script will only show everything *from the moment the postgresql options are enabled* ***and*** *the server restarted*. Anything prior will not be shown as the database was not
saving the required data

Should this script not work, please make sure that :
- make sure that the postgresql is correctly configured as shown here : https://gist.github.com/troyk/4462899
- the chosen file name is correct with write permissions
- the connection string is correct ( host + database name + user + password )

Should it still not work, please set the console display ( `writeOnConsole` ) to True in order to see any other possible errors<br/>
Details on the working of this table here : https://www.postgresql.org/docs/9.6/static/pgstatstatements.html

# Example :
The following output was obtained with the following instruction : `"dbname=test_database user=user password=my-password host=127.0.0.1 port=5432" all 10`<br />
Note : some queries can be very long, this is why the query id is displayed. This allows the output to not be cluttered with very long queries and allow you to display the important queries using the id directly
<br />

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
