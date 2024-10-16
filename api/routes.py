from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
import redis
from Models.Rag_model import AdvancedPDFProcessor


pdf_processor = AdvancedPDFProcessor()

app = FastAPI()

r = redis.Redis(host='127.0.0.1', port=6379, decode_responses=True)

# Mock retriever and generator functions for now
def retriever(query):
    # Retrieve relevant documents or chunks from the vector store
    return ["Relevant passage 1", "Relevant passage 2"]

def answer_generator(query, relevant_passages):
    # Generate an answer based on the query and relevant passages
    return "This is a generated answer based on the relevant passages."

# PDF upload route
@app.post("/upload_pdf")
async def upload_pdf(file: UploadFile = File(...)):
    print('this is file', file  )
    content = await file.read()
    print('this is the content ', content)
    processed_pdf = pdf_processor.process_pdf(content)
    final_text = pdf_processor.preprocess_content(processed_pdf)
    print('this is final text of the uploaded pdf', final_text)
    # TODO: Process the PDF, extract text, and store it in the vector store
    return {"message": "PDF processed and added to the vector store"}

# Chat route: process the query
class Query(BaseModel):
    question: str
    # pdf_content: str

@app.post("/chat")
async def chat(query: Query):
    print('this is query in the chat', query)
    relevant_passages = retriever(query.question)
    # Generate answer based on the query and retrieved passages
    answer = answer_generator(query.question, relevant_passages)
    return {"answer": answer}

# Redis retrieval for caching
@app.get("/retrieve")
def retrieve(data: str):
    if r.exists(data):
        return {"retrieved data from cache": r.get(data)}

    # Assuming retriever retrieves the required data from the vector store
    retrieved = retriever(data)
    r.set(data, retrieved)
    return {"retrieved doc": retrieved}

# Generate answers based on the template
@app.post("/generate")
def generate(template: str, retrieved_docs: list[str]):
    template = """
    This is the retrieved chunks and user query based on this. Provide a professional answer.
    If you don't know, just say sorry.

    User query: {template}
    Retrieved chunks: {retrieved_docs}
    """

    prompt = PromptTemplate.from_template(template)
    # TODO: Chain function to generate a response based on the template and retrieved docs
    return {"response": "Generated answer"}
