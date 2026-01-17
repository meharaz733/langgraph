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
    runs: int
    balls: int
    sixes: int
    fours: int
    sr: float
    bp: float
    bpb: float
    summary: str

def sr_calculate(state: MainState) -> MainState:
    sr = (state['runs']/state['balls'])*100
    return {'sr': sr}

def bp_calculate(state: MainState)->MainState:
    bp = (((state['fours']*4) + (state['sixes']*6)) / state['runs'])*100
    return {'bp': bp}

def bpb_calculate(state: MainState)->MainState:
    bpb = state['balls']/(state['fours']+state['sixes'])
    return {'bpb': bpb}

def summary(state: MainState)->MainState:
    state['summary'] = f"""
        Strike Rate(sr): {state['sr']},
        Balls per Boundary(bpb): {state['bpb']},
        Boundary Percent(bp): {state['bp']}
    """
    return state

main_graph = StateGraph(MainState)


#Add nodes to graph
main_graph.add_node('sr_cal', sr_calculate)
main_graph.add_node('bp_cal', bp_calculate)
main_graph.add_node('bpb_cal', bpb_calculate)
main_graph.add_node('summary', summary)

#Add edges to graph
main_graph.add_edge(START, 'sr_cal')
main_graph.add_edge(START, 'bp_cal')
main_graph.add_edge(START, 'bpb_cal')
main_graph.add_edge('sr_cal', 'summary')
main_graph.add_edge('bp_cal', 'summary')
main_graph.add_edge('bpb_cal', 'summary')
main_graph.add_edge('summary', END)

# compile the graph
workflow = main_graph.compile()

final_state = workflow.invoke({
                                  'runs':100,
                                  'balls':50,
                                  'sixes':4,
                                  'fours':6
                              })

print(final_state)

png_bytes = workflow.get_graph().draw_mermaid_png()

with open("demo_parallel_workflow.png", "wb") as f:
    f.write(png_bytes)
