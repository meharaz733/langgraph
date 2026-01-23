from langgraph.graph import StateGraph, START, END
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from typing import TypedDict
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

llm_model = HuggingFaceEndpoint(
    repo_id = "meta-llama/Llama-3.1-8B-Instruct",
    task = "text_generation"
)

model = ChatHuggingFace(llm = llm_model)


class MainState(TypedDict):
    questions: str
    answer: str

def chat_func(state: MainState) -> MainState:
    response = model.invoke(state['questions'])
    state['answer'] = response.content
    return state
def get_query(state: MainState)->MainState:
    state['questions'] = input("Write a query: ")
    return state

main_graph = StateGraph(MainState)

checkpointer = MemorySaver()


#Add nodes to graph
main_graph.add_node('chat', chat_func)
main_graph.add_node('get_query', get_query)

#Add edges to graph
main_graph.add_edge(START, 'get_query')
main_graph.add_edge('get_query', 'chat')
main_graph.add_edge('chat', END)

# compile the graph
workflow = main_graph.compile(checkpointer=checkpointer)
config = {
    'configurable':{
        'thread_id':'thread_id'
    }
}

final_state = workflow.invoke({}, config=config)

print(workflow.get_state(config=config))

# png_bytes = workflow.get_graph().draw_mermaid_png()

# with open("simple_llm_workflow.png", "wb") as f:
#     f.write(png_bytes)
