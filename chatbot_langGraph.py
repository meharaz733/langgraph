from langgraph.graph import StateGraph, START, END, add_messages
from typing import TypedDict, Annotated, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from langgraph.checkpoint.memory import MemorySaver

class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]

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

main_graph = StateGraph(ChatState)

checkpoint = MemorySaver()

main_graph.add_node('chat', chat)

main_graph.add_edge(START, 'chat')
main_graph.add_edge('chat', END)

workflow = main_graph.compile(checkpointer=checkpoint)

# ans = workflow.invoke({
                    # 'messages':[HumanMessage(content="What is the name of Bangladeshi primeminister?")]
                # })
# print(ans)
thread_id = '1'

while True:
    user_msg = input("Type here:")
    print('User:', user_msg)
    if user_msg.strip().lower() in ['bye', 'exit', 'quit']:
        break
    config = {'configurable':{'thread_id':thread_id}}
    
    response = workflow.invoke({
        'messages':[HumanMessage(content=user_msg)]
    }, config=config)

    print('AI:',response['messages'][-1].content)
