
import pandas as pd
import re



def preprocess (data ):
    # Define the pattern to match date-time format
    pattern = '\d{2}/\d{2}/\d{2},\s\d{1,2}:\d{2}\s[ap]m'

    # Split the data into messages and dates
    messages = re.split(pattern, data)[1:]

    dates = re.findall(pattern, data)

    chat = pd.DataFrame({'messages': messages, 'date_time': dates})

    # Convert the series to a datetime column, ensure format matches
    chat['date_time'] = pd.to_datetime(chat['date_time'], format='%d/%m/%y, %I:%M %p')

    # Format the datetime column to the desired format
    chat['date_time_12_hrs'] = chat['date_time'].dt.strftime('%d/%m/%y, %I:%M %p')

    users = []
    messages = []

    for msg in chat['messages']:
        # Check if the message contains ':', indicating a user name
        if ':' in msg:
            # Split the message into user name and actual message
            user, message_text = msg.split(':', 1)
            users.append(user.strip())  # Add the user name to the users list
            messages.append(message_text.strip())  # Add the message to the messages list
        else:
            users.append('group notification')  # Label as group notification if ':' is not present
            messages.append(msg.strip())  # Add the message to the messages list

    # Add users and messages as new columns to the DataFrame
    chat['users'] = users
    chat['messages'] = messages
    # separating year , month , day , hour and storing them to new column


    chat['year'] = chat['date_time'].dt.year
    chat['month'] = chat['date_time'].dt.month_name()
    chat['hour'] = chat['date_time'].dt.hour
    chat['minute'] = chat['date_time'].dt.minute
    chat['month_num'] = chat['date_time'].dt.month
    chat['date'] = chat['date_time'].dt.date
    chat['day_name']=chat['date_time'].dt.day_name()

    # heatmap
    period = []

    for hour in chat['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str("00"))
        elif hour == 0:
            period.append(str("00") + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))
    chat['period'] = period
    chat_new_order = ['messages', 'users', 'date_time_12_hrs', 'date_time',"date", 'year', 'month', 'hour', 'minute',
                      'month_num','day_name','period']
    chat = chat[chat_new_order]

    return chat




