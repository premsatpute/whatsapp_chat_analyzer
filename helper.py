from urlextract import URLExtract
from wordcloud import WordCloud
import pandas as pd
from collections import Counter

import seaborn as sns
import  matplotlib as plt
import streamlit as st


extract = URLExtract()

def fetch_stats(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    # fetch the number of messages
    num_messages = df.shape[0]

    # fetch the total number of words
    words = []
    for message in df['messages']:
        words.extend(message.split())

    # fetch number of media messages
    num_media_messages = df[df['messages'] == '<Media omitted>'].shape[0]

    # fetch number of links shared
    links = []
    for message in df['messages']:
        links.extend(extract.find_urls(message))

    return num_messages, len(words), num_media_messages, len(links)

def top_5_active(df):
    # Filter out group notifications
    chat_grp_ntf_rmvd = df[df['users'] != 'group notification']

    # Count messages by user and take the top 10
    y = chat_grp_ntf_rmvd['users'].value_counts().head(10)
    top_10_active = pd.DataFrame({'users': y.index, 'messages': y.values})

    # Debugging: Print the DataFrame to check its structure
    print("Top 10 active DataFrame:")
    print(top_10_active)

    # Calculate the sum of messages for percentage contribution
    k = chat_grp_ntf_rmvd['users'].value_counts().sum()
    top_10_active['pct_contribution'] = round((top_10_active['messages'] / k) * 100, 2)

    return top_10_active


def top_inactive (df):

    chat_grp_ntf_rmvd = df[df['users'] != 'group notification']


    y = chat_grp_ntf_rmvd['users'].value_counts(ascending=True).head(10)
    top_inactive = pd.DataFrame(y).rename(columns={'users': 'messages'})

     # adding pct column

    # data frame for percentage of messages by each user

    k = chat_grp_ntf_rmvd['users'].value_counts(ascending=True).sum()  # sum of all legit msges from 87 unique users .
    top_inactive['pct_contribution'] = round((top_inactive['messages'] / k) * 100, 2)

    return top_inactive

def create_wordcloud(selected_user,df):

    f = open('stop_hinglish.txt', 'r')
    stop_words = f.read()

    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

        # Filter out group notifications and media omitted messages
    temp = df[df['users'] != 'group_notification']
    temp = temp[temp['messages'] != '<Media omitted>']
    temp = temp[temp['messages'] != 'This message was deleted']

    # Function to remove stop words
    def remove_stop_words(message):
        y = []
        for word in message.lower().split():
            if word not in stop_words:
                y.append(word)
        return " ".join(y)

    # Apply stop words removal
    temp['messages'] = temp['messages'].apply(remove_stop_words)

    # Generate word cloud
    wc = WordCloud(width=300, height=200, min_font_size=10, background_color='white')
    df_wc = wc.generate(temp['messages'].str.cat(sep=" "))

    # Calculate most common words
    words = temp['messages'].str.cat(sep=" ").split()
    most_common_df = pd.DataFrame(Counter(words).most_common(10), columns=['word', 'count'])

    return df_wc, most_common_df



def monthly_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    timeline = df.groupby(['year', 'month_num', 'month']).count()['messages'].reset_index()

    time = []
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i] + "-" + str(timeline['year'][i]))

    timeline['times'] = time

    return timeline


def daily_timeline(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    daily_timeline = df.groupby('date').count()['messages'].reset_index()

    return daily_timeline

def week_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    return df['day_name'].value_counts()

def month_activity_map(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    return df['month'].value_counts()

def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['users'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='messages', aggfunc='count').fillna(0)

    return user_heatmap

def most_deleted_msges(chat):
    # Filter for deleted messages
    deleted_msgs = chat[chat['messages'] == 'This message was deleted']
    
    # Count the number of deleted messages per user and name the Series
    user_max_del = deleted_msgs['users'].value_counts().rename('msg_deleted')
   
    
    # Convert to DataFrame
    user_max_del = user_max_del.to_frame()
   
    
    # Get the top 5 users who deleted messages
    user_max_del = user_max_del.iloc[:5]
   
    
    # Calculate the total messages sent by these users
    total_msgs_sent = chat[chat['users'].isin(user_max_del.index)]['users'].value_counts()
    total_msgs_sent = total_msgs_sent.rename('total_msges_sent')

    
    # Merge the total messages sent with the user_max_del DataFrame
    user_max_del = user_max_del.join(total_msgs_sent)
  
    
    # Fill any missing values with 0
    user_max_del.fillna(0, inplace=True)
    
    # Calculate the percentage of messages deleted out of the total messages sent
    user_max_del['pct_deleted'] = round((user_max_del['msg_deleted'] / user_max_del['total_msges_sent']) * 100, 2)
  
    
    return user_max_del
