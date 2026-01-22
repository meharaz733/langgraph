import streamlit as st
from chatbot_langGraph import CONFIG, workflow
from langchain.messages import HumanMessage

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('type here...')

#normal way to print llm response
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
