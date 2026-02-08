import streamlit as st
from backend_langgraph import workflow, title_flow, retrieve_all_threads
from langchain.messages import HumanMessage, AIMessage
import uuid

# utility func
def reset():
    st.session_state["thread_id"] = str(uuid.uuid4())
    st.session_state["message_history"] = []
    add_thread(st.session_state["thread_id"])


def add_thread(thread_id):
    if thread_id not in st.session_state["chat_threads"]:
        st.session_state["chat_threads"].append(thread_id)


def retrieve_history(thread_id):
    st.session_state["message_history"] = []
    try:
        # checking value
        
        # print(
        #     "Thread id: ",
        #     thread_id,
        # )

        state = workflow.get_state({"configurable": {"thread_id": thread_id}})
        # print(f"Point 3:Workflow state: {state}\n")

        for msg in state.values["messages"]:
            # print(msg)
            if isinstance(msg, HumanMessage):
                st.session_state["message_history"].append(
                    {"role": "user", "content": msg.content}
                )
            else:
                st.session_state["message_history"].append(
                    {"role": "assistant", "content": msg.content}
                )

        st.session_state["title"][thread_id] = state.values["chat_title"]
        # print(state.values["chat_title"])

    except Exception as e:
        print(f"Point 1: {e}")
        return


def get_titles(threads):
    try:
        for thread in threads:
            st.session_state["title"][thread] = workflow.get_state(
                {"configurable": {"thread_id": thread}}
            ).values["chat_title"]
    except Exception as e:
        print(f"Point 2: {e}")


# config

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads() or []
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []
if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = str(uuid.uuid4())
if "title" not in st.session_state:
    st.session_state["title"] = {}

get_titles(st.session_state["chat_threads"])
add_thread(st.session_state["thread_id"])

CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}


# Sidebar
st.sidebar.title("ChatBot")

if st.sidebar.button("New Chat"):
    reset()

st.sidebar.header("My Conversation")

for thread_id in reversed(st.session_state["chat_threads"]):
    if st.sidebar.button(
        "New Conversation"
        if thread_id not in st.session_state["title"]
        else st.session_state["title"][thread_id],
        key=thread_id,
    ):
        # print(f"Point 4: {thread_id}")
        st.session_state["thread_id"] = thread_id
        retrieve_history(thread_id)


# main part
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("type here...")

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


# print("Point 11: \nSession State: ", st.session_state)
