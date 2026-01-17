"""
Key Points:
    1. iterative workflow
"""

from langgraph.graph import StateGraph, START, END
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from typing import TypedDict, Literal, Annotated, List
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from pydantic import BaseModel, Field
import operator

load_dotenv()

llm_model = HuggingFaceEndpoint(
    repo_id="meta-llama/Llama-3.1-8B-Instruct", task="text_generation"
)

model = ChatHuggingFace(llm=llm_model)


class EvaluateDataModel(BaseModel):
    evaluation: Literal["approved", "need_optimize"] = Field(
        ..., description="Final evaluation of the tweet."
    )
    feedback: str = Field(..., description="Feedback for the tweet.")


structured_model = model.with_structured_output(EvaluateDataModel)


class MainState(TypedDict):
    topic: str
    evaluation: Literal["approved", "need_improve"]
    tweet: str
    feedback: str
    iteration: int
    max_iteration: int
    tweet_history: Annotated[List[str], operator.add]
    feedback_history: Annotated[List[str], operator.add]


def tweet(state: MainState) -> MainState:
    messages = [
        SystemMessage(content="You are a funny and clever Twitter/X influencer."),
        HumanMessage(
            content=f"""
Write a short, original, and hilarious tweet on the topic: "{state["topic"]}".

Rules:
- Do NOT use question-answer format.
- Max 280 characters.
- Use observational humor, irony, sarcasm, or cultural references.
- Think in meme logic, punchlines, or relatable takes.
- Use simple, day to day english.
"""
        ),
    ]

    response = model.invoke(messages).content

    return {"tweet": response, "tweet_history": [response]}


def evaluate(state: MainState) -> MainState:
    messages = [
        SystemMessage(
            content="You are a ruthless, no-laugh-given Twitter critic. You evaluate tweets based on humor, originality, virality, and tweet format."
        ),
        HumanMessage(
            content=f"""
Evaluate the following tweet:

Tweet: "{state["tweet"]}"\n

Instruction:
Use the criteria below to evaluate the tweet:

1. Originality – Is this fresh, or have you seen it a hundred times before?  
2. Humor – Did it genuinely make you smile, laugh, or chuckle?  
3. Punchiness – Is it short, sharp, and scroll-stopping?  
4. Virality Potential – Would people retweet or share it?  
5. Format – Is it a well-formed tweet (not a setup-punchline joke, not a Q&A joke, and under 280 characters)?

Auto-reject if:
- It's written in question-answer format (e.g., "Why did..." or "What happens when...")
- It exceeds 280 characters
- It reads like a traditional setup-punchline joke
- Dont end with generic, throwaway, or deflating lines that weaken the humor (e.g., “Masterpieces of the auntie-uncle universe” or vague summaries)

### Respond ONLY in structured format:
- evaluation: "approved" or "needs_improvement"  
- feedback: One paragraph explaining the strengths and weaknesses 
"""
        ),
    ]

    response = structured_model.invoke(messages)

    return {
        "evaluation": response.evaluation,
        "feedback": response.feedback,
        "feedback_history": [response.feedback],
    }


def optimize(state: MainState) -> MainState:
    messages = [
        SystemMessage(
            content="You punch up tweets for virality and humor based on given feedback."
        ),
        HumanMessage(
            content=f"""
Improve the tweet based on this feedback:
"{state["feedback"]}"\n

Topic: "{state["topic"]}"\n
Original Tweet:
{state["tweet"]}\n

Re-write it as a short, viral-worthy tweet. Avoid Q&A style and stay under 280 characters.
"""
        ),
    ]
    res = model.invoke(messages).content
    iteration = state["iteration"] + 1

    return {"tweet": res, "iteration": iteration, "tweet_history": res}


def check_condition(state: MainState) -> MainState:
    if (
        state["evaluation"] == "approved"
        or state["iteration"] >= state["max_iteration"]
    ):
        return "approved"
    else:
        return "optimize_tweet"


def approved_tweet(state: MainState) -> MainState:
    pass


main_graph = StateGraph(MainState)


# Add nodes to graph
main_graph.add_node("get_tweet", tweet)
main_graph.add_node("evaluate_tweet", evaluate)
main_graph.add_node("optimize_tweet", optimize)

# Add edges to graph
main_graph.add_edge(START, "get_tweet")
main_graph.add_edge("get_tweet", "evaluate_tweet")
main_graph.add_conditional_edges(
    "evaluate_tweet",
    check_condition,
    {"approved": END, "optimize_tweet": "optimize_tweet"},
)
main_graph.add_edge("optimize_tweet", "evaluate_tweet")

# compile the graph
workflow = main_graph.compile()

final_state = workflow.invoke(
    {"topic": "AI Rise in Bnagladesh.", "iteration": 1, "max_iteration": 5}
)

print(final_state)

png_bytes = workflow.get_graph().draw_mermaid_png()

with open("Coditional_workflow_with_LLM.png", "wb") as f:
    f.write(png_bytes)
