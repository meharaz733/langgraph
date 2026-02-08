from PIL.ImageFont import load
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv

load_dotenv()

model = init_chat_model(
    "meta-llama/Llama-3.1-8B-Instruct",
    model_provider="huggingface",
)

print(model.invoke("Hi, this is Meharaz, you?"))
print(type(model.invoke("Hi, this is Meharaz, you?")))
