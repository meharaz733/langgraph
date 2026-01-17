"""
    Key Points:
        1. llm based conditional workflow
"""

from langgraph.graph import StateGraph, START, END
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from typing import TypedDict, Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

llm_model = HuggingFaceEndpoint(
    repo_id = "meta-llama/Llama-3.1-8B-Instruct",
    task = "text_generation"
)

model = ChatHuggingFace(llm = llm_model)


class MainState(TypedDict):
    review: str
    sentiment: Literal['positive', 'negative']
    diagnosis: dict
    response: str

class data_schema(BaseModel):
    sentiment: Literal['positive', 'negative'] = Field(description="Sentiment of the review.")

structured_model = model.with_structured_output(data_schema)

def get_sentiment(state: MainState) -> MainState:
    prompt = f"What is the sentiment of the following review?\n\nReview: {state['review']}."
    res = structured_model.invoke(prompt).sentiment

    return {
        'sentiment': res
    }

def positive_res(state: MainState)->MainState:
    pass

def run_diagnosis(state: MainState)->MainState:
    pass

def negative_res(state: MainState)-> MainState:
    pass

def check_condition(state: MainState)->Literal['positive_res', 'negative_res']:
    if state['sentiment']=='positive':
        return "positive_res"
    else:
        return "run_diagnosis"
    
main_graph = StateGraph(MainState)


#Add nodes to graph
main_graph.add_node('get_sentiment', get_sentiment)
main_graph.add_node('positive_response', positive_res)
main_graph.add_node('run_diagnosis', run_diagnosis)
main_graph.add_node('negative_response', negative_res)

#Add edges to graph
main_graph.add_edge(START, 'get_sentiment')
main_graph.add_conditional_edges('get_sentiment', check_condition)
main_graph.add_edge('positive_res', END)
main_graph.add_edge('run_diagnosis', 'negative_res')
main_graph.add_edge('negative_res', END)

# compile the graph
workflow = main_graph.compile()

final_state = workflow.invoke({
                                'review': "the software isn't good."
                              })

print(final_state)

png_bytes = workflow.get_graph().draw_mermaid_png()

with open("Coditional_workflow_with_LLM.png", "wb") as f:
    f.write(png_bytes)
