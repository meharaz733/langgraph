from langgraph.graph import StateGraph, START,END
from typing import TypedDict
from langchain_huggingface import(
        HuggingFaceEndpoint,
        ChatHuggingFace
    )
from dotenv import load_dotenv
from langgraph.checkpoint.memory import InMemorySaver

load_dotenv()

llm_model = HuggingFaceEndpoint(
    repo_id = "meta-llama/Llama-3.1-8B-Instruct",
    task = "text-generation"
)

model = ChatHuggingFace(llm=llm_model)

class MainState(TypedDict):
    topic: str
    joke: str
    explanation: str

def generate_joke(state: MainState)->MainState:
    prompt = f"Generate a joke on the topic {state['topic']}."
    response = model.invoke(prompt).content

    return {
        'joke':response
    }

def gen_explanation(state: MainState)->MainState:
    prompt = f"Write an explanation for the joke - {state['joke']}"
    response = model.invoke(prompt).content

    return {
        'explanation':response
    }


graph = StateGraph(MainState)

graph.add_node('generate_joke', generate_joke)
graph.add_node('gen_explanation', gen_explanation)

graph.add_edge(START, 'generate_joke')
graph.add_edge('generate_joke', 'gen_explanation')
graph.add_edge('gen_explanation', END)

checkpointer = InMemorySaver()

workflow = graph.compile(checkpointer=checkpointer)

config = {
    "configurable":{
        "thread_id":"1"
    }
}

ans = workflow.invoke({'topic':'Human'}, config=config)

print(ans)

state__ = workflow.get_state(config)
state_history = workflow.get_state_history(config)
update = workflow.update_state({"configurable": {"thread_id": "1", "checkpoint_id": "1f06cc6e-7232-6cb1-8000-f71609e6cec5", "checkpoint_ns": ""}}, {'topic':'samosa'})
