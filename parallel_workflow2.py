"""
    Key points:
        1. Parallel workflow
        2. structured output
        3. Reducers function
"""
from langgraph.graph import StateGraph, START, END
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from typing import TypedDict, Annotated, Union, List
from dotenv import load_dotenv
from pydantic import BaseModel, Field
import operator

load_dotenv()

llm_model = HuggingFaceEndpoint(
    repo_id = "meta-llama/Llama-3.1-8B-Instruct",
    task = "text_generation"
)

model = ChatHuggingFace(llm = llm_model)

class EvaluationSchema(BaseModel):
    feedback: Annotated[str, Field(..., description="Detailed feedback for the essay.")]
    score: Annotated[Union[int, float], Field(..., description="Rating of the essay, out of 10", ge=0, le=10)]

structured_model = llm_model.with_structured_output(EvaluationSchema)

essay = """
India in the Age of AI
As the world enters a transformative era defined by artificial intelligence (AI), India stands at a critical juncture — one where it can either emerge as a global leader in AI innovation or risk falling behind in the technology race. The age of AI brings with it immense promise as well as unprecedented challenges, and how India navigates this landscape will shape its socio-economic and geopolitical future.

India's strengths in the AI domain are rooted in its vast pool of skilled engineers, a thriving IT industry, and a growing startup ecosystem. With over 5 million STEM graduates annually and a burgeoning base of AI researchers, India possesses the intellectual capital required to build cutting-edge AI systems. Institutions like IITs, IIITs, and IISc have begun fostering AI research, while private players such as TCS, Infosys, and Wipro are integrating AI into their global services. In 2020, the government launched the National AI Strategy (AI for All) with a focus on inclusive growth, aiming to leverage AI in healthcare, agriculture, education, and smart mobility.

One of the most promising applications of AI in India lies in agriculture, where predictive analytics can guide farmers on optimal sowing times, weather forecasts, and pest control. In healthcare, AI-powered diagnostics can help address India’s doctor-patient ratio crisis, particularly in rural areas. Educational platforms are increasingly using AI to personalize learning paths, while smart governance tools are helping improve public service delivery and fraud detection.

However, the path to AI-led growth is riddled with challenges. Chief among them is the digital divide. While metropolitan cities may embrace AI-driven solutions, rural India continues to struggle with basic internet access and digital literacy. The risk of job displacement due to automation also looms large, especially for low-skilled workers. Without effective skilling and re-skilling programs, AI could exacerbate existing socio-economic inequalities.

Another pressing concern is data privacy and ethics. As AI systems rely heavily on vast datasets, ensuring that personal data is used transparently and responsibly becomes vital. India is still shaping its data protection laws, and in the absence of a strong regulatory framework, AI systems may risk misuse or bias.

To harness AI responsibly, India must adopt a multi-stakeholder approach involving the government, academia, industry, and civil society. Policies should promote open datasets, encourage responsible innovation, and ensure ethical AI practices. There is also a need for international collaboration, particularly with countries leading in AI research, to gain strategic advantage and ensure interoperability in global systems.

India’s demographic dividend, when paired with responsible AI adoption, can unlock massive economic growth, improve governance, and uplift marginalized communities. But this vision will only materialize if AI is seen not merely as a tool for automation, but as an enabler of human-centered development.

In conclusion, India in the age of AI is a story in the making — one of opportunity, responsibility, and transformation. The decisions we make today will not just determine India’s AI trajectory, but also its future as an inclusive, equitable, and innovation-driven society.
"""

class MainState(TypedDict):
    essay: str
    language_feedback: str
    analysis_feedback: str
    clearity_feedback: str
    overall_feedback: str
    individual_score: Annotated[List[Union[int, float]], operator.add] # reducer func add...
    average_score: float

def get_lang_eval(state: MainState)->MainState:
    prompt = f"Evaluate the language quality of the following essay and provide a feedback and assign a score out of 10 \n\n {state['essay']}"
    output = structured_model.invoke(prompt)
    return {
        'language_feedback': output.feedback,
        'individual_score': [output.score]
    }

def get_analysis_eval(state: MainState)->MainState:
    prompt = f"Evaluate the depth of analysis of the following essay and provide a feedback and assign a score out of 10 \n\n {state['essay']}"
    output = structured_model.invoke(prompt)
    return {
        'analysis_feedback': output.feedback,
        'individual_score': [output.score]
    }
    
def get_clarity_eval(state: MainState)->MainState:
    prompt = f"Evaluate the clearity of thought of the following essay and provide a feedback and assign a score out of 10 \n\n {state['essay']}"
    output = structured_model.invoke(prompt)
    return {
        'clearity_feedback': output.feedback,
        'individual_score': [output.score]
    }
    
def get_overall_eval(state: MainState)->MainState:
    prompt= f"""Based on the following feedbacks create a summarize feedback. \n\n
    Language Feedback: {state['language_feedback']}\n\n
    Depth of Analysis Feedback: {state['analysis_feedback']}\n\n
    Clearity of Thought Feedback: {state['clearity_feedback']}\n\n
    """
    overall_feedback = model.invoke(prompt).content

    #average calculate...
    avg = sum(state['individual_score'])/len(state['individual_score'])
    return {
        'overall_feedback': overall_feedback,
        'average_score': avg
    }
    
main_graph = StateGraph(MainState)

#Add nodes to graph
main_graph.add_node('eval_lang', get_lang_eval)
main_graph.add_node('eval_analysis', get_analysis_eval)
main_graph.add_node('eval_clearity', get_clarity_eval)
main_graph.add_node('eval_overall', get_overall_eval)


#Add edges to graph
main_graph.add_edge(START, 'eval_lang')
main_graph.add_edge(START, 'eval_analysis')
main_graph.add_edge(START, 'eval_clearity')
main_graph.add_edge('eval_lang', 'eval_overall')
main_graph.add_edge('eval_analysis', 'eval_overall')
main_graph.add_edge('eval_clearity', 'eval_overall')
main_graph.add_edge('eval_overall', END)

# compile the graph
workflow = main_graph.compile()

final_state = workflow.invoke({
                                  'essay':essay
                              })

print(final_state)

png_bytes = workflow.get_graph().draw_mermaid_png()

with open("Essay_Checker_workflow.png", "wb") as f:
    f.write(png_bytes)
