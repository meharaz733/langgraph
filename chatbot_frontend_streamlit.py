import streamlit as st
from chatbot_langGraph import workflow
from langchain.messages import HumanMessage
import uuid


#utility func
def reset():
    st.session_state['thread_id'] = uuid.uuid4()
    st.session_state['message_history'] = []
    add_thread(st.session_state['thread_id'])

def add_thread(thread_id):
     if thread_id not in st.session_state['chat_threads']:
         st.session_state['chat_threads'].append(thread_id)

def retrieve_history(thread_id):
    st.session_state['message_history'] = []
    st.session_state['thread_id'] = thread_id
    try:
        for msg in workflow.get_state(
            {
                'configurable':{
                    'thread_id':thread_id
                }
            }
        ).values['messages']:
            # print(msg)
            if isinstance(msg, HumanMessage):
                st.session_state['message_history'].append(
                    {
                        'role':'user',
                        'content':msg.content
                    }
                )
            else:
                st.session_state['message_history'].append(
                    {
                        'role':'assistant',
                        'content':msg.content
                    }
                )
    except Exception as e:
        print(e)
        return

#config
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = uuid.uuid4()
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

add_thread(st.session_state['thread_id'])

CONFIG = {'configurable':{'thread_id':st.session_state['thread_id']}}



#Sidebar
st.sidebar.title("ChatBot")

if st.sidebar.button('New Chat'):
    reset()

st.sidebar.header("My Conversation")

for thread_id in reversed(st.session_state['chat_threads']):
    if st.sidebar.button(str(thread_id)):
        retrieve_history(thread_id)


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
