from imessage_reader import fetch_data
import datetime
import sqlite3
from sqlite3 import Error


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
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("Database connection success")
    except Error as e:
        print(e)

    return conn


def delete_task(conn, id):
    """
    Delete a task by task id
    :param conn:  Connection to the SQLite database
    :param id: id of the task
    :return:
    """
    sql = 'DELETE FROM main.message WHERE rowid=?'

    def function():
        print("message deleted")
    
    conn.create_function("after_delete_message_plugin", 0, function)


    temp = "DELETE FROM main.message WHERE _rowid_ IN ('9040');"

    cur = conn.cursor()
    # cur.execute(sql, (id,))
    cur.execute(temp)
    conn.commit()
    # print ("Total number of rows deleted :" + conn.total_changes)


def delete_all_tasks(conn):
    """
    Delete all rows in the tasks table
    :param conn: Connection to the SQLite database
    :return:
    """
    sql = 'DELETE FROM tasks'
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()

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
    messages = fd.get_messages() #Getting all messages in chat.db file

    #Filtering to only messages in the last 30 days
    date_threshold = datetime.datetime.now() - datetime.timedelta(days=30)
    messages = [message for message in messages if datetime.datetime.strptime(message[2], '%Y-%m-%d %H:%M:%S') > date_threshold]
    
    #Filtering to only messages sent with SMS
    messages = [message for message in messages if str(message[3]) == "SMS"]

    #Filters to only messages with a unique phone number (where the phone number appears once throughout all messages)
    # messages = get_unique_number_tuples(messages) #This filter does not remove spam messages that come from the same number multiple times(example: Venmo)

    return messages

def main():
    database = r"/Users/maccooley/Desktop/chat copy.db"
    
    spamMessages = get_spam_messages()

    for temp in spamMessages:
        print("\n" + str(temp))

    # create a database connection
    conn = create_connection(database)
    with conn:
        delete_task(conn, 2)
    #     # delete_all_tasks(conn);


if __name__ == '__main__':
    main()


# Message object contains (in tuple order): 
# user id (sender's or recipient's phone number or email address)
# message
# date and time
# service (iMessage or SMS)
# account (destination caller id)
# is the message from me