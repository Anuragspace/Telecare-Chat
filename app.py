# Import necessary libraries
import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from flask import Flask, render_template, request, redirect, flash
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import traceback
import threading

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables from .env file
load_dotenv()

# Get Google API key from environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your-google-api-key-here":
    print("WARNING: Please set your Google API key in the .env file or GOOGLE_API_KEY environment variable.")
    print("You can get an API key from: https://makersuite.google.com/app/apikey")
else:
    os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
    print("✓ Google API key loaded successfully")

#Flask App
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-for-flash-messages')  # For flash messages

# Health check endpoint for monitoring
@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    return {'status': 'healthy', 'service': 'TeleCare AI Assistant'}, 200

# Fix for async event loop issue in threads
def ensure_event_loop():
    """Ensure there's an event loop in the current thread"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop

def run_sync(async_func, *args, **kwargs):
    """Run async function synchronously"""
    try:
        loop = ensure_event_loop()
        if loop.is_running():
            # If loop is running, create a new one in a thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, async_func(*args, **kwargs))
                return future.result()
        else:
            return loop.run_until_complete(async_func(*args, **kwargs))
    except Exception as e:
        print(f"Error in run_sync: {e}")
        # Fallback: try to run directly
        return async_func(*args, **kwargs)

vectorstore = None
conversation_chain = None
chat_history = []

def get_pdf_text(pdf_docs):
    text = ""
    print(f"Processing {len(pdf_docs)} PDF files...")
    for i, pdf in enumerate(pdf_docs):
        try:
            print(f"Reading PDF {i+1}: {pdf.filename}")
            pdf_reader = PdfReader(pdf)
            print(f"PDF {i+1} has {len(pdf_reader.pages)} pages")
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                text += page_text
                print(f"  Page {page_num+1}: extracted {len(page_text)} characters")
        except Exception as e:
            print(f"Error reading PDF {pdf.filename}: {e}")
    print(f"Total text extracted: {len(text)} characters")
    return text

def get_text_chunks(text):
    print("Splitting text into chunks...")
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    print(f"Created {len(chunks)} text chunks")
    return chunks

def get_vectorstore(text_chunks):
    print("Creating vector store with embeddings...")
    try:
        print("Initializing Google embeddings...")
        
        # Try to create embeddings with explicit configuration
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/embedding-001",
            google_api_key=os.environ.get('GOOGLE_API_KEY')
        )
        print("✓ Embeddings model initialized")
        
        print(f"Creating FAISS vector store from {len(text_chunks)} text chunks...")
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        print("✓ Vector store created successfully")
        return vectorstore
    except Exception as e:
        print(f"Error creating vector store: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise

def get_conversation_chain(vectorstore):
    print("Creating conversation chain...")
    try:
        print("Initializing ChatGoogleGenerativeAI...")
        
        # Try to create LLM with explicit configuration
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash", 
            temperature=0.3,
            google_api_key=os.environ.get('GOOGLE_API_KEY')
        )
        print("✓ LLM initialized")
        
        memory = ConversationBufferMemory(
            memory_key='chat_history', return_messages=True)
        print("✓ Memory initialized")
        
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(),
            memory=memory
        )
        print("✓ Conversation chain created successfully")
        return conversation_chain
    except Exception as e:
        print(f"Error creating conversation chain: {e}")
        print(f"Full traceback: {traceback.format_exc()}")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test_upload():
    return render_template('test_upload.html')

@app.route('/process', methods=['POST'])
def process_documents():
    global vectorstore, conversation_chain, chat_history
    print("=== Processing documents ===")
    try:
        # Reset chat history for new document processing
        chat_history = []
        
        pdf_docs = request.files.getlist('pdf_docs')
        print(f"Received {len(pdf_docs)} files")
        
        if not pdf_docs:
            print("No files received")
            flash("No files were uploaded. Please select PDF files.")
            return redirect('/')
            
        if pdf_docs[0].filename == '':
            print("Empty filename received")
            flash("Please select valid PDF files.")
            return redirect('/')
        
        # Log file details
        for i, pdf in enumerate(pdf_docs):
            print(f"File {i+1}: {pdf.filename} ({pdf.content_type})")
        
        print("Extracting text from PDFs...")
        raw_text = get_pdf_text(pdf_docs)
        
        if not raw_text.strip():
            print("No text extracted from PDFs")
            flash("No text could be extracted from the PDF files. Please ensure they contain readable text.")
            return redirect('/')
        
        print("Creating text chunks...")
        text_chunks = get_text_chunks(raw_text)
        
        if not text_chunks:
            print("No text chunks created")
            flash("Could not process the PDF content. Please try a different file.")
            return redirect('/')
        
        print("Creating vector store...")
        vectorstore = get_vectorstore(text_chunks)
        
        print("Creating conversation chain...")
        conversation_chain = get_conversation_chain(vectorstore)
        
        print("✓ Document processing completed successfully!")
        flash("Documents processed successfully! You can now ask questions.")
        return redirect('/chat')
        
    except Exception as e:
        error_msg = f"Error processing documents: {str(e)}"
        print(error_msg)
        print(f"Full traceback: {traceback.format_exc()}")
        flash(f"Error processing documents: {str(e)}")
        return redirect('/')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    global vectorstore, conversation_chain, chat_history

    print(f"=== Chat route accessed ===")
    print(f"Conversation chain exists: {conversation_chain is not None}")
    print(f"Vector store exists: {vectorstore is not None}")
    print(f"Current chat history length: {len(chat_history)}")

    if conversation_chain is None:
        print("No conversation chain found, redirecting to home")
        flash("Please upload and process a PDF file first.")
        return redirect('/')

    if request.method == 'POST':
        user_question = request.form.get('user_question', '').strip()
        print(f"User question: {user_question}")
        
        if user_question:
            try:
                print("Sending question to conversation chain...")
                response = conversation_chain({'question': user_question})
                chat_history = response['chat_history']
                print(f"Response received. New chat history length: {len(chat_history)}")
            except Exception as e:
                error_msg = f"Error in chat: {str(e)}"
                print(error_msg)
                print(f"Full traceback: {traceback.format_exc()}")
                flash(f"Error processing your question: {str(e)}")

    return render_template('chat.html', chat_history=chat_history)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)