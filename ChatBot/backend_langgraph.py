import os
import sqlite3
from typing import Annotated, List, TypedDict

import requests
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph, add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langsmith import traceable

load_dotenv()


search_tool = DuckDuckGoSearchRun(region="us-en")

@tool
def get_stock_price(symbol: str)->dict:
    """
    This tool provide latest stock price of any given symbol using Alpha Vantage API key.
    This tool required symbol of the brand/product as input. e.g. MSFT, IBM
    """

    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={os.getenv('ALPHAVANTAGE_API_KEY')}"
    return requests.get(url=url).json()

tools = [search_tool, get_stock_price]


@traceable(run_type="retriever", name="retrieve func")
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
    repo_id="meta-llama/Llama-3.1-8B-Instruct",
    task="text-generation",
)

model = ChatHuggingFace(llm=llm_model)

model_with_tools = model.bind_tools(tools=tools)


def chat(state: ChatState) -> ChatState:
    response = model_with_tools.invoke(state["messages"])

    return {"messages": [response]}

tool_node = ToolNode(tools)

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
main_graph.add_node("tools", tool_node)

main_graph.add_edge(START, "chat")
main_graph.add_conditional_edges("chat", tools_condition)
main_graph.add_edge("tools", "chat")



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
