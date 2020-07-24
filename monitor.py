# pip install psycopg2-binary
import psycopg2
import os
import re

class Monitor:
    # prepares the file
    def prep_file(self):
        if self.writeToFile:
            try:
                os.remove(self.filename)
            except OSError:
                pass
            return open(self.filename, "w+")
        else:
            return None

    # gets the query results
    def get_records(self, query):
        self.cursor.execute(query)
        return self.cursor.fetchall()

    # writes the text to either the console nad / or the output file
    def output_text(self, text):
        if self.writeOnConsole:
            print(text)
        if self.writeToFile:
            self.output_file.write(text)

    # adds a '0' in from of values < 0 in order to make the time values as easy to read as possible
    def format_time_value(self, value):
        if value < 10:
            return '0' + str(value)
        else:
            return str(value)

    # formats a time duration in order to make it easier to read
    def milliseconds_to_time(self, duration):
        milliseconds = (duration % 1000) / 100
        seconds = (duration / 1000) % 60
        minutes = (duration / (1000 * 60)) % 60
        hours = (duration / (1000 * 60 * 60)) % 24
        dispRest = False
        if int(hours) != 0:
            hours_s = self.format_time_value(int(hours)) + "h "
            dispRest = True
        else:
            hours_s = ''
        if int(minutes) != 0 or dispRest:
            minutes_s = self.format_time_value(int(minutes)) + "m "
            dispRest = True
        else:
            minutes_s = ''
        if int(seconds) != 0 or dispRest:
            seconds_s = self.format_time_value(int(seconds)) + "s "
            dispRest = True
        else:
            seconds_s = ''
        if dispRest:
            return hours_s + minutes_s + seconds_s + "{0:.2f}".format(milliseconds) + "ms"
        else:
            return hours_s + minutes_s + seconds_s + "{0:.4f}".format(milliseconds) + "ms"

    # only formats the value if it a time value
    def format_time_values(self, value, timeValue):
        if timeValue:
            return self.milliseconds_to_time(value)
        else:
            return str(value)

    # formats the id to make sure it lines up correctly
    def format_id(self, id):
        ref_id = id
        if ref_id < 0:
            ref_id = ref_id * -1  # ensures that the buffering will correctly take into account the length of the id
            ref_id = ref_id * 10  # to take into account the '-' at the start of a negative number
        i = 0
        value = 20
        buff = ''
        ref = 10
        while i < value:
            if ref >= ref_id:
                break
            i += 1
            ref = ref * 10
        value = value - i
        while value > -1:
            value -= 1
            buff += ' '
        return buff + str(id)

    # displays just the start of the query
    def print_start_of_query(self, query):
        buff = re.sub(' +', ' ', ''.join(query.splitlines()))
        if len(buff) > self.truncatedQuerySize:
            buff = buff[0 : self.truncatedQuerySize - 4] + " ..."
        return buff

    # gets the rows of the queries as tuples and makes them more user friendly
    def tuple_to_readable_string(self, _tuple, timeValue):
        buff = "Query id : " + self.format_id(_tuple[0]) + " => "
        indent = self.format_time_values(_tuple[2], timeValue)
        while len(indent) < self.indentBeforeCalls:
            indent += ' '
        buff += indent + " | " + str(_tuple[3])
        if _tuple[3] > 1:
            buff += " calls"
        else:
            buff += " call"
        if len(buff) < self.indentBeforeQuery:
            while len(buff) < self.indentBeforeQuery:
                buff += ' '
        buff += " Query : " + self.print_start_of_query(_tuple[1]) + "\n"
        return buff

    # makes a human-readable display of the query results
    def format_and_display(self, results, test, timeFormat):
        buff = "\n"
        buff += " =========\n"
        buff += test + "\n"
        buff += " =========\n"
        buff += "\n"
        for x in results:
            buff += self.tuple_to_readable_string(x, timeFormat)
        self.output_text(buff)

    # generates the instruction that is added to the query in order to only get the relevant information
    def generate_ignore_queries(self):
        if self.useIgnore is False:
            return ""
        i = 0
        buff = " WHERE query NOT LIKE "
        for x in self.ignore:
            if i != 0:
                buff += " AND query NOT LIKE "
            buff += "'%" + x + "%'"
            i += 1
        return buff

    # generates the query while taking into account the parameters
    def get_query(self, query, orderBy):
        buff = "SELECT queryid, query, "
        buff += query + self.generate_ignore_queries() + " " + orderBy + " limit " + str(self.limit) + ";"
        if self.displayUsedQueries:
            self.output_text("\nused query : " + buff + "\n")
        return buff
    
    # gets the most used queries
    def get_most_used(self):
        self.format_and_display(self.get_records(self.get_query("mean_time, calls FROM pg_stat_statements", "ORDER BY calls DESC")),
                                'Queries that where the most used by amount', True)
    
    # gets the queries that required the most time accumulated
    def get_biggest_time_accumulated(self):
        self.format_and_display(self.get_records(self.get_query("total_time, calls FROM pg_stat_statements", "ORDER BY total_time DESC")),
                                'Queries that required the most time accumulated', True)
    
    # gets the queries that required the most time on average
    def get_biggest_time_average(self):
        self.format_and_display(self.get_records(self.get_query("mean_time, calls FROM pg_stat_statements", "ORDER BY mean_time DESC")),
                                'Queries that required the most time per use on average', True)
    
    # gets the queries that returned the most rows on average
    def get_most_rows_returned_average(self):
        self.format_and_display(self.get_records(self.get_query("rows / calls, calls FROM pg_stat_statements", "ORDER BY rows / calls DESC")),
                                'Queries that returned the most rows on average', False)
    
    # gets the queries that returned the most rows accumulated
    def get_most_rows_returned_accumulated(self):
        self.format_and_display(self.get_records(self.get_query("rows, calls FROM pg_stat_statements", "ORDER BY rows DESC")),
                                'Queries that returned the most rows accumulated', False)
    
    # adds the view to the database should it not exist ( needed in order to get the stats )
    def init_the_database(self):
        self.cursor.execute('CREATE EXTENSION IF NOT EXISTS pg_stat_statements;')
        self.dbConnexion.commit()
   
    # checks if the string is an int
    def is_int(self, string):
        try:
            int(string)
            return True
        except ValueError:
            return False

    # parses all of the arguments given to the script in order to know what to display
    def parse_instructions(self, argv):
        i = 0
        for x in argv:
            i += 1
            if i < 2:  # ignoring the first argument ( connection string )
                continue
            if i == len(argv):  # extracting the amount of required queries
                if self.is_int(x) is False:
                    self.output_text("The limit ( last argument ) was not recognised as an integer. Got '" + x + "'")
                    return False
                self.limit = int(x)
                if self.limit <= 0:
                    self.output_text("Error : the limit should not be <= 0, got : " + str(self.limit))
                    return False
                continue
            if x == "mostUsed":
                self.displayMostUsed = True
                continue
            if x == "longestTimeAccumulated":
                self.displayLongestTimeAccumulated = True
                continue
            if x == "longestTimeOnAverage":
                self.displayLongestTimeOnAverage = True
                continue
            if x == "mostRowsReturnedAccumulated":
                self.displayMostRowsReturnedAccumulated = True
                continue
            if x == "mostRowsReturnedAverage":
                self.displayMostRowsReturnedAverage = True
                continue
            if x == "all":
                self.displayMostUsed = True
                self.displayLongestTimeAccumulated = True
                self.displayLongestTimeOnAverage = True
                self.displayMostRowsReturnedAccumulated = True
                self.displayMostRowsReturnedAverage = True
                continue
            self.output_text("Error : unknown argument '" + x + "'\n'")
            self.output_text("Known arguments are : 'mostUsed', 'longestTimeAccumulated', 'longestTimeOnAverage', 'mostRowsReturnedAccumulated', 'mostRowsReturnedAverage' and 'all' \n")
            return False
        return True
    
    # prints the query from the given id
    def print_query_from_id(self, argv):
        if self.is_int(argv[1]) is False:
            self.output_text("Error : unknown argument '" + argv[1] + "\nExpected a query id as argument if no other instructions are given")
            return False
        buff = "\n"
        buff += " =========\n"
        buff += "displaying query of queryid " + str(argv[1]) + "\n"
        buff += " =========\n"
        buff += "\n"
        self.cursor.execute("SELECT query FROM pg_stat_statements WHERE queryid = %s", (str(argv[1]),))
        res = self.cursor.fetchall()
        if len(res) == 0:
            buff += "Error : there is no queries matching that id"
        else:
            buff += res[0][0]
        buff += "\n"
        self.output_text(buff)
        return

    # runs the display print
    def exec_instructions(self):
        if self.displayMostUsed:
            self.get_most_used()
        if self.displayLongestTimeAccumulated:
            self.get_biggest_time_accumulated()
        if self.displayLongestTimeOnAverage:
            self.get_biggest_time_average()
        if self.displayMostRowsReturnedAverage:
            self.get_most_rows_returned_average()
        if self.displayMostRowsReturnedAccumulated:
            self.get_most_rows_returned_accumulated()
    
    # executes the instruction with the given arguments
    def run(self, *argv):
        if len(argv) < 2:
            self.output_text("This class needs at least 2 arguments to be able to run")
            exit(0)
        try:
            # get a connection, if a connect cannot be made an exception will be raised here
            self.dbConnexion = psycopg2.connect(argv[0])
            self.cursor = self.dbConnexion.cursor()
            self.init_the_database()
        except Exception as e:
            self.output_text("Error : could not connect to the database with connection string \"" + argv[0] + "\"")
            self.output_text("Message is : " + str(e))
            exit(2)
        if len(argv) == 2:
            self.print_query_from_id(argv)
        else:
            if self.parse_instructions(argv):
                self.exec_instructions()

    def __init__(self):
        # ============================
        # ========== CONFIG ==========
        # ============================

        # bool to choose to use ( True ) the ignore array or not ( False )
        self.useIgnore = True
        # array of strings used to ignore queries that have at least one of these strings
        self.ignore = [
            "pg_stat_statements",  # ignoring these requests as they are generated while looking or relevant information
            "pg_catalog",  # ignoring these requests as they are generated while looking or relevant information
            "ALTER TABLE",
            "TRUNCATE TABLE",
            "CREATE TABLE"
        ]

        # === output configuration ===

        # bool used to determine if the output is to be written on the console or not
        self.writeOnConsole = True
        # bool used to determine if the output is to be written in a file or not
        self.writeToFile = True
        # path of the file in witch the output can be written. Must include the file name
        self.filename = "output.txt"

        # === display ===

        # Size of the truncated query being displayed ( must be an integer > 5 to work properly )
        # Will not truncate queries that are shorter than the truncatedQuerySize
        self.truncatedQuerySize = 60
        # size of the alignment ( start of line until the Query keyword ) for the queries ( must me a positive integer to work )
        self.indentBeforeQuery = 65
        # size of the alignment for calls ( from end of '=>' until '|', must me a positive integer to work )
        self.indentBeforeCalls = 10

        # === debug ===

        # bool used to display the queries that the program uses itself to get the displayed information ( True ) or not ( False )
        self.displayUsedQueries = False

        # ============================
        # ==== RUNTIME VARIABLES =====
        # ============================

        # preparing the output file
        self.output_file = self.prep_file()
        # booleans used to determine what needs printing ( set to true with arguments of the same name passed to the script )
        # these values are NOT configuration related, they are overwritten by user input by command line
        self.displayMostUsed = False
        self.displayLongestTimeAccumulated = False
        self.displayLongestTimeOnAverage = False
        self.displayMostRowsReturnedAccumulated = False
        self.displayMostRowsReturnedAverage = False
        self.limit = -1
