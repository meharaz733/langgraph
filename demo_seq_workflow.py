from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class BMIState(TypedDict):
    weight_kg: float
    height_m: float
    bmi: float
    bmi_status: str

def calculate_bmi(state: BMIState) -> BMIState:
    weight = state['weight_kg']
    height = state['height_m']

    bmi = weight/(height**2)

    state['bmi'] = round(bmi)

    return state

def bmi_status(state: BMIState) -> BMIState:
    if state['bmi'] < 18.5:
        state['bmi_status'] = "Underweight"
    elif state['bmi'] < 25:
        state['bmi_status'] = "Normal"
    else:
        state['bmi_status'] = "Overweight"
    return state

graph = StateGraph(BMIState)


#Add nodes to graph
graph.add_node('calculate_bmi', calculate_bmi)
graph.add_node('check_bmi_status', bmi_status)

#Add edges to graph
graph.add_edge(START, 'calculate_bmi')
graph.add_edge('calculate_bmi', 'check_bmi_status')
graph.add_edge('check_bmi_status', END)

# compile the graph
workflow = graph.compile()

final_state = workflow.invoke({
                              'weight_kg': 64,
                              'height_m': 1.73,
                              })

print(final_state)

png_bytes = workflow.get_graph().draw_mermaid_png()

with open("bmi.png", "wb") as f:
    f.write(png_bytes)
