import sys
from monitor import Monitor

# using the argv as input for the monitor
buffer = sys.argv
buffer.pop(0)  # remove 'python' ( or similar ) if used
buffer.pop(0)  # remove the file name
monitor = Monitor()
monitor.displayUsedQueries = True
monitor.run(*buffer)  # arguments should not be passed as one array but as strings
