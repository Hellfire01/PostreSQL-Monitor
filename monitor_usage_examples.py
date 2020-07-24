from monitor import Monitor

# these arguments send the arguments directly

# you need to put in the right values to be able to correctly connect to your database
authentication_string = "dbname=tests user=postgres password=pswd host=127.0.0.1 port=5432"

# example to get the 10 queries that have the longest average time and the 10 queries that have longest accumulated time
# + display the queries used by the Monitor class
# + display ALL queries
monitor = Monitor()
monitor.displayUsedQueries = True  # display the queries used by the program to get it's information
monitor.useIgnore = False  # display ALL queries
monitor.run(authentication_string, 'longestTimeOnAverage', 'longestTimeAccumulated', 10)

# example to display the 10 most used queries
# + ignore only BEGIN, COMMIT and pg_stat_statements
# + do not write to file
monitor = Monitor()
monitor.ignore = [  # ignore only BEGIN and COMMIT
    "BEGIN",
    "COMMIT",
    "pg_stat_statements"
]
monitor.writeToFile = False  # do not write to a file
monitor.run(authentication_string, 'mostUsed', 10)

# example to display a query
monitor = Monitor()
monitor.run(authentication_string, 19846765274300731)  # this id will need to be replaced with an id as display by the Monitor class from your database in order to work
