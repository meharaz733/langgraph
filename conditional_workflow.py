"""
    Key points:
        1. Conditional Workflow
            i. Non llm based
            ii. llm based workflow
"""


from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

class MainState(TypedDict):
    a: int
    b: int
    c: int
    equation: str
    discriminant: float
    result: str

def show_equ(state: MainState)->MainState:
    equ = f"{state['a']}x2{state['b']}x{state['c']}"

    return {
        'equation':equ
    }

def cal_dis(state:MainState)->MainState:
    dis = state['b']**2 - (4*state['a']*state['c'])

    return {
        'discriminant':dis
    }

def real_root(state: MainState)->MainState:
    root1 = (-state['b'] + state['discriminant']**0.5)/(2*state['a'])
    root2 = (-state['b'] - state['discriminant']**0.5)/(2*state['a'])

    return {'result': f"The roots are {root1} and {root2}."}

def repeated_root(state: MainState)->MainState:
    root = (-state['b'])/(2*state['a'])

    return {'result' : f"The repeated root is {root}."}

def no_real_root(state: MainState) -> MainState:
    return {'result': "No real root"}

def check_condition(state: MainState)->Literal['real_root', 'no_real_root', 'repeated_root']:
    if state['discriminant'] > 0:
        return "real_root"
    elif state['discriminant'] == 0:
        return "repeated_root"
    else:
        return "no_real_root"
    
    
main_graph = StateGraph(MainState)



#Add nodes to graph
main_graph.add_node('show_equ', show_equ)
main_graph.add_node('cal_dis', cal_dis)
main_graph.add_node('real_root', real_root)
main_graph.add_node('repeated_root', repeated_root)
main_graph.add_node('no_real_root', no_real_root)

#Add edges to graph
main_graph.add_edge(START, 'show_equ')
main_graph.add_edge('show_equ', 'cal_dis')
main_graph.add_conditional_edges('cal_dis', check_condition)
main_graph.add_edge('real_root', END)
main_graph.add_edge("repeated_root", END)
main_graph.add_edge("no_real_root", END)

# compile the graph
workflow = main_graph.compile()

final_state = workflow.invoke({
                                  'a':4,
                                  'b':-5,
                                  'c':-4
                              })

print(final_state)

png_bytes = workflow.get_graph().draw_mermaid_png()

with open("coditional_workflow.png", "wb") as f:
    f.write(png_bytes)
