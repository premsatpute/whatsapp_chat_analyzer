import streamlit as st
import helper
import io
import matplotlib.pyplot as plt
import pandas as pd
import re
import preprocessor
import seaborn as sns


st.sidebar.title("Whatsapp_Chat_Analyzer")
st.sidebar.subheader("Analyze your chats in one click")
st.sidebar.divider()

uploaded_file = st.sidebar.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    df = preprocessor.preprocess(data)

    st.dataframe(df)

    # fetch unique users
    user_list = df['users'].unique().tolist()
    user_list.remove('group notification')

    user_list.insert(0, "Overall")

     # creating the selectbox

    selected_user = st.sidebar.selectbox("Show analysis wrt", user_list)

    if st.sidebar.button("Show Analysis"):
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)

        st.markdown('<h1 style="color: #FF6347;">Top Statitics</h1>', unsafe_allow_html=True)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.header("Total Messages")
            st.subheader(num_messages)
        with col2:
            st.header("Total Words")
            st.subheader(words)
        with col3:
            st.header("Media Shared")
            st.subheader(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.subheader(num_links)



# top active users

        if selected_user=="Overall":
            st.divider()
            st.markdown('<h1 style="color: #FF6347;">Top 5 Active Users</h1>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            top_active= helper.top_5_active(df)

            with col1:

                fig, ax = plt.subplots(figsize=(10, 7))
                sns.barplot(x=top_active.index[:5], y=top_active.pct_contribution[:5], hue=top_active.messages[:5],palette='viridis')
                ax.set_xlabel('Users')
                ax.set_ylabel('Percentage Contribution')
                ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
                st.pyplot(fig)
            with col2:
                st.dataframe(top_active)

            st.divider()
            st.markdown('<h1 style="color: #FF6347;">Most deleted messages </h1>', unsafe_allow_html=True)

            col1,col2=st.columns(2)
            user_max_del=helper.most_deleted_msges(df)

            with col1:
                fig,ax=plt.subplots()
                sns.barplot(x=user_max_del.index, y=user_max_del.pct_deleted, hue=user_max_del.msg_deleted,palette='viridis')
                plt.xticks(rotation=45)
                st.pyplot(fig)
            with col2:
                st.dataframe(user_max_del)



        # most inactive users
        if selected_user == "Overall":
            st.divider()
            st.markdown('<h1 style="color: #FF6347;">Most Inactive Users</h1>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            top_inactive = helper.top_inactive(df)

            with col1:
                fig, ax = plt.subplots(figsize=(10, 7))
                sns.barplot(x=top_inactive.index[:5], y=top_inactive.pct_contribution[:5], hue=top_inactive.messages[:5],
                            palette='viridis')
                ax.set_xlabel('Users')
                ax.set_ylabel('Percentage Contribution')
                ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
                st.pyplot(fig)
            with col2:
                st.dataframe(top_inactive)


        # WordCloud
        st.divider()
        st.markdown('<h1 style="color: #FF6347;">Wordcloud</h1>', unsafe_allow_html=True)
        col1 ,col2 = st.columns(2)

        with col1:
            df_wc,most_common_df = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(df_wc, interpolation='bilinear')
            ax.axis('off')  # Hide the axes
            st.pyplot(fig)

        st.divider()
        st.markdown('<h1 style="color: #FF6347;">Most Common Words</h1>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            df_wc, most_common_df = helper.create_wordcloud(selected_user, df)
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.barplot(x=most_common_df['word'],y=most_common_df['count'],palette='viridis')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)
        with col2:
            st.dataframe(most_common_df)


        st.divider()

        col1, col2 = st.columns(2)
        monthly_timeline_df=helper.monthly_timeline(selected_user,df)
        daily_timeline_df= helper.daily_timeline(selected_user,df)

        with col1:
            st.markdown('<h1 style="color: #FF6347;">Monthly Timeline</h1>', unsafe_allow_html=True)

            timeline = helper.monthly_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(timeline['times'], timeline['messages'], color='green')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.markdown('<h1 style="color: #FF6347;">Daily Timeline</h1>', unsafe_allow_html=True)

            daily_timeline = helper.daily_timeline(selected_user, df)
            fig, ax = plt.subplots()
            ax.plot(daily_timeline['date'], daily_timeline['messages'], color='blue')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.divider()   # activity map
        col1, col2 = st.columns(2)

        with col1:

            st.markdown('<h1 style="color: #FF6347;">Most Busy days </h1>', unsafe_allow_html=True)
            busy_day = helper.week_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=busy_day.index, y=busy_day.values, palette='viridis')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:

            st.markdown('<h1 style="color: #FF6347;">Most Busy months </h1>', unsafe_allow_html=True)
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            sns.barplot(x=busy_month.index, y=busy_month.values, palette='viridis')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        st.divider()
        st.markdown('<h1 style="color: #FF6347;">Weekly Activity Map</h1>', unsafe_allow_html=True)
        col1,col2=st.columns(2)
        with col1:
            user_heatmap = helper.activity_heatmap(selected_user, df)
            fig, ax = plt.subplots(figsize=(3,4))
            ax = sns.heatmap(user_heatmap)
            st.pyplot(fig)

        st.divider()
        st.markdown('<h1 style="color: #FF6347;">Emoji Analysis</h1>', unsafe_allow_html=True)

        # emoji analysis
        emoji_df = helper.emoji_helper(selected_user, df)

        col1, col2, col3 = st.columns(3)

        with col2:
            st.dataframe(emoji_df.head(10))
        with col1:
            fig, ax = plt.subplots(figsize=(4, 4))
            colors = sns.color_palette("viridis", len(emoji_df.head()))
            ax.pie(emoji_df[1].head(), labels=emoji_df[0].head(), autopct="%0.2f", colors=colors)
            st.pyplot(fig)











