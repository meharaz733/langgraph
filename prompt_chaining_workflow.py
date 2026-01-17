from langgraph.graph import StateGraph, START, END
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from typing import TypedDict
from dotenv import load_dotenv

load_dotenv()

llm_model = HuggingFaceEndpoint(
    repo_id = "meta-llama/Llama-3.1-8B-Instruct",
    task = "text_generation"
)

model = ChatHuggingFace(llm = llm_model)


class MainState(TypedDict):
    query: str
    story: str
    sumamry: str

def get_story(state: MainState) -> MainState:
    response = model.invoke(state['query'])
    state['story'] = response.content
    return state

def get_query(state: MainState)->MainState:
    state['query'] = input("Write a query: ")
    return state

def get_summary(state: MainState)->MainState:
    state['sumamry'] = model.invoke(f"Summarize the story in 3 sentences. Story:{state['story']}").content
    return state

main_graph = StateGraph(MainState)


#Add nodes to graph
main_graph.add_node('get_story', get_story)
main_graph.add_node('get_query', get_query)
main_graph.add_node('get_summary', get_summary)

#Add edges to graph
main_graph.add_edge(START, 'get_query')
main_graph.add_edge('get_query', 'get_story')
main_graph.add_edge('get_story', 'get_summary')
main_graph.add_edge('get_summary', END)

# compile the graph
workflow = main_graph.compile()

final_state = workflow.invoke({})

print(final_state)

png_bytes = workflow.get_graph().draw_mermaid_png()

with open("simple_Prompt_chaining_workflow.png", "wb") as f:
    f.write(png_bytes)
