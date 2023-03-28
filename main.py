from imessage_reader import fetch_data
import datetime
import sqlite3
from sqlite3 import Error

# -m pip install mysql-connector-python


conn = None
messages = []
daylength = 15
index = 0

# Simple break line for console
def line():
    print("\n")
    print("...")
    print("\n")

# Creating connectin to database
def create_connection(db_file):
    line()
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Database connection success")
    except Error as e:
        print(e)
    return conn

# Prompts user if they want to delete this message. Continues until user answers Y,N, or STOP. Returns answer as String.
def promptUser(message):
    line()
    print(str(count) + " of " + str(get_number_addresses(messages)))
    print("ADDRESS: " + message[0])
    print("Messages from address: " + str(count_messages_from_address(message[0])))
    print("Most recent message on " + str(message[2]) + ": ") 
    print("\n")
    print(message[1])
    print("\n")
    print("Delete all messages from this address?:  (y/n)")
    answer = input()
    while(answer != "y" and answer != "n" and answer != "STOP"):
        print("Please enter y or n or STOP to end program")
        answer = input()
    return answer

# Deletes all tasks from address using SQLite3
def delete_task(conn, address):
    line()
    task = "DELETE FROM main.chat WHERE guid LIKE ?;"
    cur = conn.cursor()
    cur.execute(task, ('%' + address + '%',))
    conn.commit()

    # print number of rows deleted 
    print ("Messages Deleted: " + str(cur.rowcount) + " from " + address)

# Gets number of messages from a specific address
def count_messages_from_address(address):
    num = 0
    for message in messages:
        if message[0] == address:
            num += 1
    return num


# Gets messages that are from a unique number. (A number that only has ever sent you 1 message ever. Ex. NOT Venmo)
def get_unique_number_tuples(messages):
    number_count = {}
    for message in messages:
        number = message[0]
        if number not in number_count:
            number_count[number] = 1
        else:
            number_count[number] += 1
    unique_numbers = [message for message in messages if number_count[message[0]] == 1]
    return unique_numbers

# Gets number of addresses(senders) in list
def get_number_addresses(messages):
    number_count = {}
    for message in messages:
        number = message[0]
        if number not in number_count:
            number_count[number] = 1
        else:
            number_count[number] += 1
    unique_numbers = [message for message in messages if number_count[message[0]] == 1]
    return len(unique_numbers)

# Returns a list of message objects that contain spam messages in the last 30 days
def get_spam_messages():
    fd = fetch_data.FetchData()
    global messages
    messages = fd.get_messages() #Getting all messages in chat.db file on Mac. Fetch Data takes from main chat.db file, not test.

    #Filtering to only messages the day range
    date_threshold = datetime.datetime.now() - datetime.timedelta(days=daylength)
    messages = [message for message in messages if datetime.datetime.strptime(message[2], '%Y-%m-%d %H:%M:%S') > date_threshold]
    
    #Filtering to only messages sent with SMS
    messages = [message for message in messages if str(message[3]) == "SMS"]

    #Filters to only messages with a unique phone number (where the phone number appears once throughout all messages)
    messages = get_unique_number_tuples(messages) #This filter does not remove spam messages that come from the same number multiple times(example: Venmo)

    #Filtering to remove 'none' messages
    messages = [message for message in messages if message[1] is not None]

    return messages

def main():
    # database = r"/Users/maccooley/Desktop/copy chat.db" # Path to test chat.db file
    database = r"/Users/maccooley/Library/Messages/chat.db" # Path to chat.db file 
    
    # create a database connection
    global conn
    conn = create_connection(database)
    def after_delete_message_plugin():
        print("message deleted")
    conn.create_function("after_delete_message_plugin", -1, after_delete_message_plugin) # Creating missing after_delete_message function. Program will stop without this.

    # Getting list of spam messages
    spamMessages = get_spam_messages()

    global index
    index += 1

    # Running main program
    print("\nFound: " + str(len(spamMessages)) + " spam messages from " + str(get_number_addresses(spamMessages)) + " addresses " + "in last " + str(daylength) + " days" )
    while(len(spamMessages) != 0):
        global count
        count = 0
        dict = {} # Dictionary to store addresses already prompted (used to skip over asking messages from same address)
        for message in spamMessages[index:]:
            if(dict.get(message[0]) is None): # If address has not been prompted yet
                count += 1
                userAnswer = promptUser(message)
                dict[message[0]] = userAnswer
                if userAnswer== "y":
                    delete_task(conn, message[0])
                    break
                elif userAnswer == "STOP":
                    return
            else:
                userAnswer = dict.get(message[0])
        spamMessages = get_spam_messages()
        line()
        print("\nFound: " + str(len(spamMessages)) + " spam messages from " + str(get_number_addresses(spamMessages)) + " addresses")

# Message object contains (in tuple order): 
# [0]: user id (sender's or recipient's phone number or email address)
# [1]: text message (String)
# [2]: date and time
# [3]: service (iMessage or SMS)
# [4]: account (destination caller id)
# [5]: is the message from me

if __name__ == '__main__':
    main()