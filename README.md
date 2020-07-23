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
