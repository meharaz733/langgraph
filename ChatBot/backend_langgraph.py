from langgraph.graph import StateGraph, START, END, add_messages
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3


def retrieve_all_threads():
    threads = set()
    for item in memory.list(None):
        threads.add(item.config["configurable"]["thread_id"])

    return list(threads)


class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    query_for_title: str
    chat_title: str


llm_model = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct", task="text_generation"
)

model = ChatHuggingFace(llm=llm_model)


def chat(state: ChatState) -> ChatState:
    response = model.invoke(state["messages"])

    return {"messages": [response]}


def get_title(state: ChatState) -> ChatState:
    response = model.invoke(
        f"Write a title for the following chat. Title must be less then 5 words and you only rosponse the title such as LngGraph Error query, Albert Law Explain, Summary of [subject] \n chat:\n{state['query_for_title']}"
    )

    return {"chat_title": response.content}


# def check_func(state: ChatState):
#     if state['chat_title'] == 'New Chat':
#         return 'get_title'
#     else:
#         return 'ok'

main_graph = StateGraph(ChatState)
title_graph = StateGraph(ChatState)

conn = sqlite3.connect("chatbot.db", check_same_thread=False)

memory = SqliteSaver(conn)

main_graph.add_node("chat", chat)
# main_graph.add_node('get_title', get_title)

main_graph.add_edge(START, "chat")
# main_graph.add_conditional_edges('chat', check_func, {
#                                      'get_title':'get_title',
#                                      'ok': END
#                                  })
main_graph.add_edge("chat", END)

# title graph node and edge
title_graph.add_node("get_title", get_title)

title_graph.add_edge(START, "get_title")
title_graph.add_edge("get_title", END)


workflow = main_graph.compile(checkpointer=memory)
title_flow = title_graph.compile(checkpointer=memory)


# *************TEST*****************
#
# ans = workflow.invoke({
#                 'messages':"What is the name of Bangladeshi primeminister?"
#               })
# print(ans)
# thread_id = 'thread-1'
# CONFIG = {'configurable':{'thread_id':thread_id}}

# while True:
#     user_msg = input("User:")
#     if user_msg.strip().lower() in ['bye', 'exit', 'quit']:
#         break

#     response = workflow.invoke({
#         'messages':[HumanMessage(content=user_msg)]
#     }, config=CONFIG)

#     print('AI:',response['messages'][-1].content)


# print(workflow.get_state(config=CONFIG))
# png_bytes = workflow.get_graph().draw_mermaid_png()

# with open("ChatBot.png", "wb") as f:
#     f.write(png_bytes)
