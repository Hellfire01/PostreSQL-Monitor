# PostreSQL-Monitor
This is a simple script that aims to be able to diagnose heavy SQL queries and show them in an easy to understand manner 

## What does it do ?
This script was designed to be either used as a command line or for a slack / discord bot and can also write to a file<br/>
The script will display queries that :
- are the most used
- required the most accumulated time for all usages
- required the most time on average
- returned the most rows with one usage
- returned the most rows on average
For each of these criteria, the 10 queries that had the biggest result are displayed

## How to use
First, the database needs to be configured in order to allow the monitoring. This can be done at the following link : <a href='https://gist.github.com/troyk/4462899'>https://gist.github.com/troyk/4462899</a>

Next, the script uses the following library to connect to the database and requires it to work : `psycopg2`

Note : the script monitor.py does **NOT** store any credentials, they need to be given by argument. You can also modify the code to hard code them should you prefer to do so

The script uses the following arguments :
- `-h` to display help ( standalone argument )

All other arguments will require the authentication string<br />
The authentication string is just as described in the `psycopg2` documentation

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

**Note** : the previously shown arguments arguments can be used simultaneously. Therefor the following instruction is valid :<br/>
`[replace with authentification string] mostUsed longestTimeOnAverage mostRowsReturnedAccumulated 10`<br/>
It will display just the queries for `mostUsed`, `longestTimeOnAverage` and `mostRowsReturnedAccumulated` one after an other

**Note** : the queries that are used by this program to gather all of the displayed data will be displayed among the other queries of your database
&
## Configuration

## Troubleshooting
**Important** : the script will only show everything *from the moment the postgresql options are enabled* ***and*** *the server restarted*. Anything prior will not be shown as the database was not
saving the required data

Should this script not work, please make sure that :
- make sure that the postgresql is correctly configured as shown here : https://gist.github.com/troyk/4462899
- the chosen file name is correct with write permissions
- the connection string is correct ( host + database name + user + password )

Should it still not work, please set the console display ( `writeOnConsole` ) to True in order to see any other possible errors<br/>
Details on the working of this table here : https://www.postgresql.org/docs/9.6/static/pgstatstatements.html

## Example :
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
