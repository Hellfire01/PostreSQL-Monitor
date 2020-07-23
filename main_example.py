import sys
from monitor import Monitor

# using the argv as input for the monitor
buffer = sys.argv
#  buffer.pop(0)  # remove 'python' ( or similar ) if used
buffer.pop(0)  # remove the file name
monitor = Monitor()
monitor.displayUsedQueries = True
monitor.run(*buffer)  # arguments should not be passed as one array but as strings

# sending the arguments directly
# ( you will need to put in the correct data directly and replace the example values in the authentication string )
# Monitor("dbname=database user=postgres password=myPassword host=127.0.0.1 port=5432", 'all', 10)
