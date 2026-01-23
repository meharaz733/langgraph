from langgraph.graph import StateGraph, START, END, add_messages
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langgraph.checkpoint.memory import MemorySaver

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]
    # chat_title:str = 'New Chat'

llm_model = HuggingFaceEndpoint(
    repo_id = "meta-llama/Llama-3.1-8B-Instruct",
    task = "text_generation"
)

model = ChatHuggingFace(llm=llm_model)


def chat(state: ChatState)->ChatState:
    response = model.invoke(state['messages'])

    return {
        'messages': [response]
    }
# def get_title(state: ChatState)->ChatState:
#     response = model.invoke(f"Write a title for the following chat. Title must be less then 5 words \n chat:\n{state['messages']}")

#     return {
#         'chat_title':response.content 
#     }

# def check_func(state: ChatState):
#     if state['chat_title'] == 'New Chat':
#         return 'get_title'
#     else:
#         return 'ok'

main_graph = StateGraph(ChatState)
title_graph = StateGraph(ChatState)

checkpoint = MemorySaver()

main_graph.add_node('chat', chat)
# main_graph.add_node('get_title', get_title)

main_graph.add_edge(START, 'chat')
# main_graph.add_conditional_edges('chat', check_func, {
#                                      'get_title':'get_title',
#                                      'ok': END
#                                  })
main_graph.add_edge('chat', END)

#title graph node and edge
title_graph.add_node('chat', chat)

title_graph.add_edge(START, 'chat')
title_graph.add_edge('chat', END)


workflow = main_graph.compile(checkpointer=checkpoint)
title_flow = title_graph.compile()

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
