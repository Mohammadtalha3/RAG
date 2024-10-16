import streamlit as st
import fitz  # PyMuPDF for PDF rendering
from io import BytesIO
import base64
import requests

# Function to display PDF in Streamlit (left column)
def show_pdf(file):
    with fitz.open(stream=BytesIO(file), filetype="pdf") as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            pix = page.get_pixmap()
            img_bytes = pix.tobytes("jpeg")

            # Convert to base64 for streamlit
            img_base64 = base64.b64encode(img_bytes).decode("utf-8")
            img_display = f'<img src="data:image/jpeg;base64,{img_base64}" width="100%"/>'
            st.markdown(img_display, unsafe_allow_html=True)

# Function to send the PDF to FastAPI backend for processing
def upload_pdf_to_backend(uploaded_file):
    api_endpoint = "http://127.0.0.1:8000/upload_pdf"  # Your FastAPI endpoint for uploading PDFs
    files = {'file': uploaded_file}
    response = requests.post(api_endpoint, files=files)

    if response.status_code == 200:
        return response.json().get("message", "PDF uploaded successfully.")
    else:
        return "Error uploading PDF to backend."

# Function to query FastAPI backend with the user's question
def query_api(question):
    print('this is question recieved:', question)
    api_endpoint = "http://127.0.0.1:8000/chat"  # Your FastAPI chat endpoint
    response = requests.post(api_endpoint, json={'question': question})
    print('this is si response', response)

    if response.status_code == 200:
        return response.json().get("answer", "No answer found.")
    else:
        return "Error querying the API."

# Streamlit UI
st.set_page_config(layout="wide")

st.title("PDF Viewer and Chat Interface")

# Create two columns: left for PDF and right for chat interface
col1, col2 = st.columns([2, 1])

# PDF Upload and Display (Left Column)
with col1:
    uploaded_file = st.file_uploader("Upload a PDF document", type=["pdf"])

    if uploaded_file is not None:
        # Read the PDF file content once and reuse it
        file_content = uploaded_file.read()

        # Display the PDF
        st.header("Uploaded PDF")
        show_pdf(file_content)

        # Upload the PDF to the FastAPI backend
        st.write("Processing the PDF...")
        upload_message = upload_pdf_to_backend(uploaded_file)
        st.write(upload_message)

# Chat Interface (Right Column)
with col2:
    st.header("Ask a Question")
    user_question = st.text_input("Enter your question")

    if user_question:
        st.write("Question Submitted:", user_question)
        st.write("Querying the API...")

        # Get answer from API
        answer = query_api(user_question)
        st.write("Answer from API:", answer)
