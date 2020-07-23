# pip install psycopg2-binary
import psycopg2  # import that needs to be downloaded
import os  # system import
import re  # system import
import sys  # system import


# ============================
# ========== CONFIG ==========
# ============================

# bool to choose to use ( True ) the ignore array or not ( False )
useIgnore = True
# array of strings used to ignore queries that have at least one of these strings
ignore = [
    "pg_stat_statements",  # ignoring these requests as they are generated while looking or relevant information
    "ALTER TABLE",
    "TRUNCATE TABLE",
    "CREATE TABLE"
        ]

# === output configuration ===

# bool used to determine if the output is to be written on the console or not
writeOnConsole = True
# bool used to determine if the output is to be written in a file or not
writeToFile = True
# path of the file in witch the output can be written. Must include the file name
filename = "output.txt"

# === display ===

# Size of the truncated query being displayed ( must be an integer > 5 to work properly )
truncatedQuerySize = 60
# size of the alignment for the queries ( must me a positive integer to work )
indentBeforeQuery = 55
# size of the alignment for calls ( must me a positive integer to work )
indentBeforeCalls = 10

# === debug ===

# bool used to display the used queries to get the displayed values ( True ) or not ( False )
# this bool is to be set to True should you ever think there may be an issue with the queries used in this script
displayUsedQueries = False


# ============================
# ========== SCRIPT ==========PostgreSQL database dump
# ============================


# prepares the file
def prep_file():
    if writeToFile:
        try:
            os.remove(filename)
        except OSError:
            pass
        return open(filename, "w+")
    else:
        return None


# gets the query results
def get_records(query):
    cursor.execute(query)
    return cursor.fetchall()


# writes the text to either the console nad / or the output file
def output_text(text):
    if writeOnConsole:
        print(text)
    if writeToFile:
        output_file.write(text)


# adds a '0' in from of values < 0 in order to make the time values as easy to read as possible
def format_time_value(value):
    if value < 10:
        return '0' + str(value)
    else:
        return str(value)


# formats a time duration in order to make it easier to read
def milliseconds_to_time(duration):
    milliseconds = (duration % 1000) / 100
    seconds = (duration / 1000) % 60
    minutes = (duration / (1000 * 60)) % 60
    hours = (duration / (1000 * 60 * 60)) % 24
    dispRest = False
    if int(hours) != 0:
        hours_s = format_time_value(int(hours)) + "h "
        dispRest = True
    else:
        hours_s = ''
    if int(minutes) != 0 or dispRest:
        minutes_s = format_time_value(int(minutes)) + "m "
        dispRest = True
    else:
        minutes_s = ''
    if int(seconds) != 0 or dispRest:
        seconds_s = format_time_value(int(seconds)) + "s "
        dispRest = True
    else:
        seconds_s = ''
    if dispRest:
        return hours_s + minutes_s + seconds_s + "{0:.2f}".format(milliseconds) + "ms"
    else:
        return hours_s + minutes_s + seconds_s + "{0:.4f}".format(milliseconds) + "ms"


# only formats the value if it a time value
def format_time_values(value, timeValue):
    if timeValue:
        return milliseconds_to_time(value)
    else:
        return str(value)


# formats the id to make sure it lines up correctly
def format_id(id):
    i = 0
    value = 9
    buff = ''
    ref = 10
    while i < value:
        if ref >= id:
            break
        i += 1
        ref = ref * 10
    value = value - i
    while value > -1:
        value -= 1
        buff += ' '
    return buff + str(id)


# displays just the start of the query
def print_start_of_query(query):
    buff = re.sub(' +', ' ', ''.join(query.splitlines()))
    if len(buff) > truncatedQuerySize:
        buff = buff[0 : truncatedQuerySize - 4] + " ..."
    return buff


# gets the rows of the queries as tuples and makes them more user friendly
def tuple_to_readable_string(_tuple, timeValue, qt):
    buff = ""
    if qt == 1:
        buff += "Query id : " + format_id(_tuple[0]) + " => "
        indent = format_time_values(_tuple[2], timeValue)
        while len(indent) < indentBeforeCalls - 2:
            indent += ' '
        buff += indent + " | avg time : " + format_time_values(_tuple[3], True)
    else:
        buff += "Query id : " + format_id(_tuple[0]) + " => "
        indent = format_time_values(_tuple[2], timeValue)
        while len(indent) < indentBeforeCalls:
            indent += ' '
        buff += indent + " | " + str(_tuple[3])
        if _tuple[3] > 1:
            buff += " calls"
        else:
            buff += " call"
    if len(buff) < indentBeforeQuery:
        while len(buff) < indentBeforeQuery:
            buff += ' '
    buff += " Query : " + print_start_of_query(_tuple[1]) + "\n"
    return buff


# makes a human-readable display of the query results
def format_and_display(results, test, timeFormat, qt):
    buff = "\n"
    buff += " =========\n"
    buff += test + "\n"
    buff += " =========\n"
    buff += "\n"
    for x in results:
        buff += tuple_to_readable_string(x, timeFormat, qt)
    output_text(buff)


# generates the instruction that is added to the query in order to only get the relevant information
def generate_ignore_queries():
    if useIgnore is False:
        return ""
    i = 0
    buff = " WHERE query NOT LIKE "
    for x in ignore:
        if i != 0:
            buff += " AND query NOT LIKE "
        buff += "'%" + x + "%'"
        i += 1
    return buff


# generates the query while taking into account the parameters
def get_query(query, orderBy):
    buff = "SELECT queryid, query, "
    buff += query + generate_ignore_queries() + " " + orderBy + " LIMIT " + str(limit) + ";"
    if displayUsedQueries:
        output_text("\nused query : " + buff + "\n")
    return buff


# gets the most used queries
def get_most_used():
    format_and_display(get_records(get_query("calls, mean_time FROM pg_stat_statements", "ORDER BY calls DESC")),
                               'Queries that where the most used by amount', False, 1)


# gets the queries that required the most time accumulated
def get_biggest_time_accumulated():
    format_and_display(get_records(get_query("total_time, calls FROM pg_stat_statements", "ORDER BY total_time DESC")),
                               'Queries that required the most time accumulated', True, 2)


# gets the queries that required the most time on average
def get_biggest_time_average():
    format_and_display(get_records(get_query("mean_time, calls FROM pg_stat_statements", "ORDER BY mean_time DESC")),
                               'Queries that required the most time per use on average', True, 2)


# gets the queries that returned the most rows on average
def get_most_rows_returned_average():
    format_and_display(get_records(get_query("rows / calls, calls FROM pg_stat_statements", "ORDER BY rows / calls DESC")),
                               'Queries that returned the most rows on average', False, 2)


# gets the queries that returned the most rows accumulated
def get_most_rows_returned_accumulated():
    format_and_display(get_records(get_query("rows, calls FROM pg_stat_statements", "ORDER BY rows DESC")),
                               'Queries that returned the most rows accumulated', False, 2)


# adds the view to the database should it not exist ( needed in order to get the stats )
def init_the_database():
    cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_stat_statements;')
    dbConnexion.commit()


# checks if the string is an int
def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


# prints help / instructions
def printHelp():
    buff = ""
    buff += "\n"
    buff += "\n"
    buff += "This script's purpose is to give statistics of the database in order to know witch are queries that need " \
            "to be tweaked or watched\n"
    buff += "It is possible to change the output file's name among other things at the top of this script under the " \
            "CONFIG title\n"
    buff += "\n"
    buff += "\n"
    buff += "to display the query associated to a query id :\n"
    buff += "python thisScript [queryid]\n"
    buff += "\n"
    buff += "to display the statistics on the queries, the program understands the following instructions " \
            "( they can be put one after an other )\n"
    buff += "\n"
    buff += "mostUsed => displays the most used queries\n"
    buff += "longestTimeAccumulated => displays the queries that required the most time accumulated\n"
    buff += "longestTimeOnAverage => displays the queries that required the most time on average\n"
    buff += "mostRowsReturnedAccumulated => displays the queries that returned the most rows accumulated\n"
    buff += "mostRowsReturnedAverage => displays the queries that returned the most rows on average\n"
    buff += "all => displays all of the options above\n"
    buff += "\n"
    buff += "the instructions should be followed by a positive integer > 0 to determine the amount of queries to " \
            "display or they will not be recognized as instructions\n"
    buff += "\n"
    buff += "Ex :\n"
    buff += "python thisScript mostUsed mostRowsReturnedAverage 30\n"
    buff += "Will display the 30 queries that where the most used and the 30 queries that returned the most" \
            " rows on average\n"
    buff += "\n"
    buff += "\n"
    buff += "This script was made by the following person : Matthieu Raynaud de Fitte\n"
    buff += "please refer to him should there ever be an issue with this script\n"
    buff += "\n"
    output_text(buff)


# parses all of the arguments given to the script in order to know what to display
def parse_instructions():
    global displayMostUsed
    global displayLongestTimeAccumulated
    global displayLongestTimeOnAverage
    global displayMostRowsReturnedAccumulated
    global displayMostRowsReturnedAverage
    global limit
    i = 0
    for x in sys.argv:
        i += 1
        if i < 3:  # ignoring the 2 first arguments ( file name and connection string )
            continue
        if i == len(sys.argv):  # extracting the amount of required queries
            if is_int(x) is False:
                output_text("The limit ( last argument ) was not recognised as an integer. Got '" + x + "'")
                return False
            limit = int(x)
            if limit <= 0:
                output_text("Error : the limit should not be <= 0, got : " + str(limit))
                return False
            continue
        if x == "mostUsed":
            displayMostUsed = True
            continue
        if x == "longestTimeAccumulated":
            displayLongestTimeAccumulated = True
            continue
        if x == "longestTimeOnAverage":
            displayLongestTimeOnAverage = True
            continue
        if x == "mostRowsReturnedAccumulated":
            displayMostRowsReturnedAccumulated = True
            continue
        if x == "mostRowsReturnedAverage":
            displayMostRowsReturnedAverage = True
            continue
        if x == "all":
            displayMostUsed = True
            displayLongestTimeAccumulated = True
            displayLongestTimeOnAverage = True
            displayMostRowsReturnedAccumulated = True
            displayMostRowsReturnedAverage = True
            continue
        output_text("Error : unknown argument '" + x + "'\n'-h' or '--help' for instructions")
        return False
    return True


# prints the query from the given id
def print_query_from_id():
    if is_int(sys.argv[2]) is False:
        output_text("Error : unknown argument '" + sys.argv[2] + "', was expecting an integer for only argument\n"
                                                                 "'-h' or '--help' for instructions")
        return False
    buff = "\n"
    buff += " =========\n"
    buff += "displaying query of queryid " + sys.argv[2] + "\n"
    buff += " =========\n"
    buff += "\n"
    cursor.execute("SELECT query FROM pg_stat_statements WHERE queryid = %s", (int(sys.argv[2]),))
    res = cursor.fetchall()
    if len(res) == 0:
        buff += "Error : there is no queries matching that id"
    else:
        buff += res[0][0]
    buff += "\n"
    output_text(buff)
    return


# runs the display print
def exec_instructions():
    if displayMostUsed:
        get_most_used()
    if displayLongestTimeAccumulated:
        get_biggest_time_accumulated()
    if displayLongestTimeOnAverage:
        get_biggest_time_average()
    if displayMostRowsReturnedAverage:
        get_most_rows_returned_average()
    if displayMostRowsReturnedAccumulated:
        get_most_rows_returned_accumulated()


# preparing the output file
output_file = prep_file()
# booleans used to determine what needs printing ( set to true with arguments of the same name passed to the script )
displayMostUsed = False
displayLongestTimeAccumulated = False
displayLongestTimeOnAverage = False
displayMostRowsReturnedAccumulated = False
displayMostRowsReturnedAverage = False
limit = -1

if len(sys.argv) == 2:  # just print the query from the id
    if sys.argv[1] == "-h" or sys.argv[1] == "--help":
        printHelp()
        exit(0)
    else:
        output_text("unrecognised argument '" + sys.argv[1] + "'. Use -h for help")
        exit(1)
try:
    # get a connection, if a connect cannot be made an exception will be raised here
    dbConnexion = psycopg2.connect(sys.argv[1])
    cursor = dbConnexion.cursor()
    init_the_database()
except Exception:
    output_text("Error : could not connect to the database with connection string \"" + sys.argv[1] + "\"")
    exit(2)

if len(sys.argv) == 3:
    print_query_from_id()
else:
    if parse_instructions():
        exec_instructions()
