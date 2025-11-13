# Import necessary libraries
import os
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from flask import Flask, render_template, request, redirect, flash, session
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import traceback
import tempfile
import uuid
import warnings

# Suppress LangChain deprecation warnings for cleaner logs
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

# Load environment variables from .env file
load_dotenv()

# Get Google API key from environment
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your-google-api-key-here":
    print("⚠️  WARNING: Please set your Google API key in the .env file or GOOGLE_API_KEY environment variable.")
    print("   Get an API key from: https://makersuite.google.com/app/apikey")
else:
    os.environ['GOOGLE_API_KEY'] = GOOGLE_API_KEY
    print("✅ Google API key loaded successfully")

# Flask App Configuration
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', os.urandom(24))  # Secure random key
app.config['SESSION_TYPE'] = 'filesystem'  # Use filesystem for session storage
app.config['SESSION_PERMANENT'] = True  # Make sessions permanent
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour session lifetime
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create temp directory for storing FAISS indices
TEMP_DIR = tempfile.mkdtemp()
print(f"✅ Temporary directory for FAISS indices: {TEMP_DIR}")

# Health check endpoint for monitoring
@app.route('/health')
def health_check():
    """Health check endpoint for deployment monitoring"""
    return {'status': 'healthy', 'service': 'TeleCare AI Assistant'}, 200

# ============================================================
# SESSION MANAGEMENT FUNCTIONS
# ============================================================

def save_vectorstore_to_session(vectorstore):
    """Save FAISS vectorstore to session using file path"""
    try:
        # Generate unique filename for this session
        session_id = session.get('session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            session['session_id'] = session_id
        
        # Save FAISS index to file
        faiss_path = os.path.join(TEMP_DIR, f"faiss_{session_id}")
        vectorstore.save_local(faiss_path)
        session['faiss_path'] = faiss_path
        print(f"✅ Vector store saved: {faiss_path}")
        return True
    except Exception as e:
        print(f"❌ Error saving vectorstore: {e}")
        return False

def load_vectorstore_from_session():
    """Load FAISS vectorstore from session file path"""
    try:
        faiss_path = session.get('faiss_path')
        if not faiss_path or not os.path.exists(faiss_path):
            print("❌ No vectorstore found in session")
            return None
        
        # Recreate embeddings with same model
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        
        # Load FAISS index from file
        vectorstore = FAISS.load_local(
            faiss_path, 
            embeddings,
            allow_dangerous_deserialization=True
        )
        print(f"✅ Vector store loaded: {faiss_path}")
        return vectorstore
    except Exception as e:
        print(f"❌ Error loading vectorstore: {e}")
        return None

def save_chat_history_to_session(chat_history):
    """Save chat history to session"""
    try:
        # Chat history is already in dictionary format
        session['chat_history'] = chat_history
        print(f"✅ Chat history saved: {len(chat_history)} messages")
        return True
    except Exception as e:
        print(f"❌ Error saving chat history: {e}")
        return False

def load_chat_history_from_session():
    """Load chat history from session"""
    try:
        chat_history = session.get('chat_history', [])
        return chat_history
    except Exception as e:
        print(f"❌ Error loading chat history: {e}")
        return []

# ============================================================
# PDF PROCESSING FUNCTIONS
# ============================================================

def get_pdf_text(pdf_docs):
    """Extract text from PDF files"""
    text = ""
    for i, pdf in enumerate(pdf_docs):
        try:
            pdf_reader = PdfReader(pdf)
            print(f"   📄 PDF {i+1}: {pdf.filename} ({len(pdf_reader.pages)} pages)")
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
        except Exception as e:
            print(f"   ❌ Error reading {pdf.filename}: {e}")
    
    return text

def get_text_chunks(text):
    """Split text into chunks for processing"""
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

def get_vectorstore(text_chunks):
    """Create FAISS vector store with Google embeddings"""
    # Limit chunks for better performance (Render has memory constraints)
    MAX_CHUNKS = 50
    if len(text_chunks) > MAX_CHUNKS:
        print(f"   ⚠️  Limiting {len(text_chunks)} chunks to {MAX_CHUNKS}")
        text_chunks = text_chunks[:MAX_CHUNKS]
    
    try:
        # Initialize Google embeddings
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        
        # Test embeddings
        test_result = embeddings.embed_query("test")
        print(f"   ✅ Embeddings ready (dimension: {len(test_result)})")
        
        # Create FAISS vector store
        vectorstore = FAISS.from_texts(texts=text_chunks, embedding=embeddings)
        print(f"   ✅ Vector store created ({len(text_chunks)} chunks)")
        return vectorstore
        
    except Exception as e:
        error_str = str(e)
        if "quota" in error_str.lower() or "429" in error_str:
            raise Exception("Google API quota exceeded. Please check your usage.")
        raise Exception(f"Vector store creation failed: {error_str}")

# ============================================================
# FLASK ROUTES
# ============================================================

@app.route('/')
def index():
    """Landing page"""
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_documents():
    """Process uploaded PDF documents"""
    print("\n" + "="*60)
    print("📄 DOCUMENT PROCESSING STARTED")
    print("="*60)
    
    try:
        # Clear previous session data for fresh start
        session.pop('faiss_path', None)
        session.pop('chat_history', None)
        session.pop('conversation_ready', None)
        
        # Get uploaded files
        pdf_docs = request.files.getlist('pdf_docs')
        
        if not pdf_docs or pdf_docs[0].filename == '':
            flash("Please select PDF files to upload.")
            return redirect('/')
        
        print(f"📥 Processing {len(pdf_docs)} file(s):")
        
        # Step 1: Extract text from PDFs
        print("🔄 Step 1: Extracting text...")
        raw_text = get_pdf_text(pdf_docs)
        
        if not raw_text.strip():
            flash("No text could be extracted. Ensure PDFs contain readable text.")
            return redirect('/')
        
        print(f"   ✅ Extracted {len(raw_text)} characters")
        
        # Step 2: Create text chunks
        print("🔄 Step 2: Creating text chunks...")
        text_chunks = get_text_chunks(raw_text)
        
        if not text_chunks:
            flash("Could not process the PDF content.")
            return redirect('/')
        
        print(f"   ✅ Created {len(text_chunks)} chunks")
        
        # Step 3: Create vector store
        print("🔄 Step 3: Creating vector store...")
        vectorstore = get_vectorstore(text_chunks)
        
        # Step 4: Save to session
        print("🔄 Step 4: Saving to session...")
        if save_vectorstore_to_session(vectorstore):
            session['conversation_ready'] = True
            print("   ✅ Session ready")
        else:
            raise Exception("Failed to save vector store")
        
        print("="*60)
        print("✅ PROCESSING COMPLETED SUCCESSFULLY")
        print("="*60 + "\n")
        
        flash("Documents processed successfully! You can now ask questions.")
        return redirect('/chat')
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}\n")
        flash(f"Error: {str(e)}")
        return redirect('/')

@app.route('/chat', methods=['GET', 'POST'])
def chat():
    """Chat interface with AI assistant"""
    # Check if document has been processed
    if not session.get('conversation_ready'):
        flash("Please upload and process a PDF file first.")
        return redirect('/')

    # Load chat history from session
    chat_history = load_chat_history_from_session()

    if request.method == 'POST':
        user_question = request.form.get('user_question', '').strip()
        
        if user_question:
            try:
                # Load vectorstore from session
                vectorstore = load_vectorstore_from_session()
                if vectorstore is None:
                    raise Exception("Failed to load vector store from session")
                
                # Create conversation chain
                llm = ChatGoogleGenerativeAI(
                    model="gemini-2.0-flash", 
                    temperature=0.3
                )
                
                memory = ConversationBufferMemory(
                    memory_key='chat_history', 
                    return_messages=True
                )
                
                # Restore previous chat history into memory
                for msg in chat_history:
                    if msg['type'] == 'HumanMessage':
                        memory.chat_memory.add_message(HumanMessage(content=msg['content']))
                    elif msg['type'] == 'AIMessage':
                        memory.chat_memory.add_message(AIMessage(content=msg['content']))
                
                # Create conversation chain
                conversation_chain = ConversationalRetrievalChain.from_llm(
                    llm=llm,
                    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
                    memory=memory
                )
                
                # Get response from AI
                response = conversation_chain({'question': user_question})
                
                # Get ALL messages from memory (accumulated history)
                chat_history = []
                for msg in memory.chat_memory.messages:
                    chat_history.append({
                        'type': type(msg).__name__,
                        'content': msg.content if hasattr(msg, 'content') else str(msg)
                    })
                
                # Save updated chat history to session
                save_chat_history_to_session(chat_history)
                print(f"✅ Response generated. Total messages: {len(chat_history)}")
                
            except Exception as e:
                print(f"❌ Chat error: {str(e)}")
                flash(f"Error processing your question: {str(e)}")

    return render_template('chat.html', chat_history=chat_history)

# ============================================================
# APPLICATION STARTUP
# ============================================================


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)