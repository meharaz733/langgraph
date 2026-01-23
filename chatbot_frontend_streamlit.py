import streamlit as st
from chatbot_langGraph import workflow
from langchain.messages import HumanMessage
import uuid


#utility func
def gen_thread_id():
    return uuid.uuid4()


#config
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = gen_thread_id()

CONFIG = {'configurable':{'thread_id':st.session_state['thread_id']}}



#Sidebar
st.sidebar.title("ChatBot")

st.sidebar.button('New Chat')

st.sidebar.header("My Conversation")

st.sidebar.text(st.session_state['thread_id'])


#main part


for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('type here...')

#normal way to print llm response
#
# 
# if user_input:
#     st.session_state['message_history'].append(
#         {
#             'role':'user',
#             'content':user_input
#         }
#     )
#     with st.chat_message('user'):
#         st.text(user_input)

#     response = workflow.invoke(
#         {
#             'messages':[HumanMessage(content=user_input)]
#         },
#         config=CONFIG
#     )

#     st.session_state['message_history'].append(
#         {
#             'role':'assistant',
#             'content':response['messages'][-1].content
#         }
#     )

#     with st.chat_message('assistant'):
#         st.text(response['messages'][-1].content)



#streaming llm response
# 
if user_input:
    st.session_state['message_history'].append(
        {
            'role':'user',
            'content':user_input
        }
    )
    with st.chat_message('user'):
        st.text(user_input)

    response = workflow.stream(
        {
            'messages':[HumanMessage(content=user_input)]
        },
        config=CONFIG,
        stream_mode='messages'
    )
    
    with st.chat_message('assistant'):
        ai_msg = st.write_stream(
                        msg.content for msg, metadata in response
                    )
    
    st.session_state['message_history'].append(
        {
            'role':'assistant',
            'content': ai_msg
        }
    )
