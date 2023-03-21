# from imessage_reader import fetch_data
import datetime
import sqlite3
from sqlite3 import Error
import fetch_data


# -m pip install mysql-connector-python


#Convertstring to date time object

# for message in messages:
#     senderNumber = message[0]
#     date = datetime.datetime.strptime(message[2].split(' ')[0], '%Y-%m-%d')
#     text = message[1]
#     service = message[3]
#     isFromMe = message[5]

#     if date > date_threshold:
#         if text is not None:
#             if str(service) == "SMS":
#                 if isFromMe == 0:
#                     print(text)

## FUNCTIONS TO DELETE MESSAGES FROM DATABASE
def create_connection(db_file):
    # create a database connection to the SQLite database
    # specified by the db_file
    # :param db_file: database file
    # :return: Connection object or None
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Database connection success")
    except Error as e:
        print(e)
    return conn

def promptUser(message):
    # Prompts the user if they want to delete this message
    # :message: text message to be prompted
    # :return: true if user wants to delete message, false otherwise
    # print("\n")
    print("\n")
    print(message)
    print("Are you sure you want to delete this message?:  (Y/N)")
    answer = input()
    while(answer != "Y" and answer != "N" and answer != "STOP"):
        print("Please enter Y or N or STOP to end program")
        answer = input()
    return answer

def delete_task(conn, id):
    # Delete a task by task id
    # :param conn:  Connection to the SQLite database
    # :param id: id of the task
    # :return: none

    cur = conn.cursor()

    temp = "DELETE FROM main.chat WHERE guid LIKE ?;"

    
    cur.execute(temp, ('%' + id + '%',))    
    conn.commit()
    print ("Total number of rows deleted :" + str(conn.total_changes))

## FUNCTIONS TO GET ONLY SPAM MESSAGES
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

# Returns a list of message objects that contain spam messages in the last 30 days
def get_spam_messages():
    fd = fetch_data.FetchData()
    messages = fd.get_messages() #Getting all messages in chat.db file on Mac

    #Filtering to only messages in the last 30 days
    date_threshold = datetime.datetime.now() - datetime.timedelta(days=30)
    messages = [message for message in messages if datetime.datetime.strptime(message[2], '%Y-%m-%d %H:%M:%S') > date_threshold]
    
    #Filtering to only messages sent with SMS
    messages = [message for message in messages if str(message[3]) == "SMS"]

    #Filters to only messages with a unique phone number (where the phone number appears once throughout all messages)
    # messages = get_unique_number_tuples(messages) #This filter does not remove spam messages that come from the same number multiple times(example: Venmo)

    #Filtering to remove 'none' messages
    messages = [message for message in messages if message[1] is not None]

    return messages

def main():
    # database = r"/Users/maccooley/Desktop/chat.db" # Path to test file
    database = r"/Users/maccooley/Library/Messages/chat.db" # Path to chat.db file 
    
    # Getting list of spam messages
    spamMessages = get_spam_messages()

    for temp in spamMessages:
        print("\n" + str(temp))

    # create a database connection
    conn = create_connection(database)
    def after_delete_message_plugin():
        print("message deleted")
    conn.create_function("after_delete_message_plugin", -1, after_delete_message_plugin)

    
    for message in spamMessages:
        userAnswer = promptUser(message[1])
        if userAnswer== "Y":
            delete_task(conn, message[0])
        elif userAnswer == "STOP":
            break


if __name__ == '__main__':
    main()


# Message object contains (in tuple order): 
# user id (sender's or recipient's phone number or email address)
# message
# date and time
# service (iMessage or SMS)
# account (destination caller id)
# is the message from me