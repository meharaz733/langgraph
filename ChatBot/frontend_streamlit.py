import streamlit as st
from backend_langgraph import workflow, title_flow, retrieve_all_threads
from langchain.messages import HumanMessage, AIMessage
import uuid


# utility func
def reset():
    st.session_state["thread_id"] = uuid.uuid4()
    st.session_state["message_history"] = []
    add_thread(st.session_state["thread_id"])


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def retrieve_history(thread_ids):
    st.session_state["message_history"] = []
    try:
        for thread_id in thread_ids:
            # checking value
            print(workflow.get_state({"configurable": {"thread_id": thread_id}}))

            for msg in workflow.get_state(
                {"configurable": {"thread_id": thread_id}}
            ).values["messages"]:
                # print(msg)
                if isinstance(msg, HumanMessage):
                    st.session_state["message_history"].append(
                        {"role": "user", "content": msg.content}
                    )
                else:
                    st.session_state["message_history"].append(
                        {"role": "assistant", "content": msg.content}
                    )

            for msg in workflow.get_state(
                {"configurable": {"thread_id": thread_id}}
            ).values["chat_title"]:
                # print(msg)
                if isinstance(msg, str):
                    st.session_state["title"][thread_id] = msg

    except Exception as e:
        print(e)
        return


# config

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = uuid.uuid4()
if "title" not in st.session_state:
    st.session_state["title"] = {}

retrieve_history(st.session_state["chat_threads"])
add_thread(st.session_state['thread_id'])

CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}


# Sidebar
st.sidebar.title("ChatBot")

if st.sidebar.button("New Chat"):
    reset()

st.sidebar.header("My Conversation")

for thread_id in reversed(st.session_state["chat_threads"]):
    if st.sidebar.button(
        "New Chat"
        if thread_id not in st.session_state["title"]
        else st.session_state["title"][thread_id],
        key=str(thread_id),
    ):
        st.session_state["thread_id"] = thread_id
        retrieve_history([thread_id])


# main part
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("type here...")

# normal way to print llm response
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


# streaming llm response
#
if user_input:
    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    response = workflow.stream(
        {
            "messages": [HumanMessage(content=user_input)],
        },
        config=CONFIG,
        stream_mode="messages",
    )
    # for msg, metadata in response:
    #     print(f"msg: {msg}\n\n")
    #     print(f"Metadata: {metadata}")

    with st.chat_message("assistant"):
        ai_msg = st.write_stream(msg.content for msg, metadata in response)
    st.session_state["message_history"].append({"role": "assistant", "content": ai_msg})

    if st.session_state["thread_id"] not in st.session_state["title"]:
        print("Point 10", st.session_state["message_history"])
        title = title_flow.invoke(
            {
                "query_for_title": st.session_state["message_history"],
            },
            CONFIG,
        )["chat_title"]
        st.session_state["title"][st.session_state["thread_id"]] = title
