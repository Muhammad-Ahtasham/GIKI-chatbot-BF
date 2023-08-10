from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.document_loaders import TextLoader
from langchain.memory import ConversationBufferMemory
import os
from fastapi import FastAPI, Request, HTTPException
import json
from langchain import PromptTemplate
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
#from pydantic import BaseModel

# os.environ["OPENAI_API_KEY"] = "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"
# os.environ["OPENAI_API_KEY"] = "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"
#os.environ["OPENAI_API_KEY"] = "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"


class UserData:
  def __init__(self, users):
    self.users = users


loader = TextLoader("scrapped_Data.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
documents = text_splitter.split_documents(documents)

#embeddings = OpenAIEmbeddings()
#vectorstore = FAISS.from_documents(documents, embeddings)

#memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)

#qa = ConversationalRetrievalChain.from_llm(
#  OpenAI(temperature=0.5), 
#  vectorstore.as_retriever(), 
#  memory=memory, 
#  max_tokens_limit=4000)

chat_history = []
def QuestionAnswers(que, chat_history):
  query = que
  result = qa({"question": query, "chat_history": chat_history})
  return result["answer"]

app = FastAPI()
#origins = ["http://localhost"]  # Add the URL of your React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a templates object using Jinja2Templates
templates = Jinja2Templates(directory="./templates")

@app.get("/",response_class=HTMLResponse)
async def root(request: Request):
   return templates.TemplateResponse("index.html",context={"request":request,})
  


def read_database():
    try:
        with open("./database.json", "r") as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        return {"users": {}}

def write_database(data):
    database_file_path = os.path.join(os.getcwd(), "database.json")
    print("write: ", database_file_path, data)
    with open(database_file_path, "w") as file:
        json.dump(data, file)

def store_in_database(user_id: str, query: str, answer: str):
  data = read_database()
  print("database: ", data)
    
  if user_id not in data["users"]:
    data["users"][user_id] = []
    
  if isinstance(data["users"][user_id], list):
    data["users"][user_id].append({"question": query, "answer": answer})
  else:
    existing_entry = {
      "question": data["users"][user_id]["question"],
      "answer": data["users"][user_id]["answer"]
    }
    data["users"][user_id] = [existing_entry, {"question": query, "answer": answer}]
  write_database(data)
  print("dataLLLL", data)

def get_user_history(user_id: str):
    data = read_database()
    if user_id in data["users"]:
        return UserData(users=data["users"])  # Pass the whole data["users"] as the argument
    else:
        return UserData(users={user_id: []})

default_user_id = "123"
def process_query(user_id: str, query: str, user_history: UserData):
    if not query:
        return None

    user_chat_history = user_history.users[user_id]
    print("321: ",user_chat_history)

    chat_history = list()
    for chat in user_chat_history:
      chat_history.append(chat)

    print("Chat history2: ",chat_history)
    
    result = QuestionAnswers(query, chat_history)
    store_in_database(user_id, query, result)

    return result
    #return chat_history

@app.get("/chat_me", response_class=HTMLResponse)
async def get_chat_me(request: Request, query: str = None, user_id: str = default_user_id):
    #return { "result": f"{user_id} {query}" }
    # print(f"Received User ID: {user_id}")

    user_history = get_user_history(user_id)
    #print("user_history:\t", user_history.users)
    response_text = "khan ahtesham" #process_query(user_id, query, user_history)

    return templates.TemplateResponse("index.html", {
        "user_id": user_id,
        "request": request, 
        "response_text": response_text, 
        "chat_history": user_history.users[user_id] 
    })




@app.post("/chat")
async def chat(request_data:list):
    
    user_id = "123"  
    user_history = get_user_history(user_id)
    
    for item in request_data:
        query = item.get("content")
        role = item.get("role")
        if query:
            response_text = "OpenAI Key isnt working thats why this response is hardcoded. Just uncomment the code next to it to get bot responses" #process_query(user_id, query, user_history)
            item["response"] = response_text
            item["role"] = role

    return request_data






