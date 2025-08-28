# 🏥 TeleCare AI Assistant

**AI-Driven Medical Document Analysis Platform**

A sophisticated healthcare AI kiosk application that enables medical professionals and patients to upload PDF documents and interact with an intelligent assistant for comprehensive document analysis, diagnosis insights, and treatment recommendations.

![TeleCare AI](https://img.shields.io/badge/AI-Healthcare-blue?style=for-the-badge&logo=medical)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![Google AI](https://img.shields.io/badge/Google%20AI-4285F4?style=for-the-badge&logo=google&logoColor=white)

## 🌟 Features

### 🔍 **Intelligent Document Analysis**
- **PDF Processing**: Advanced text extraction from medical documents, reports, and prescriptions
- **AI-Powered Insights**: Leverages Google Gemini AI for comprehensive document understanding
- **Vector Search**: FAISS-powered semantic search for precise information retrieval

### 💬 **Interactive Chat Interface**
- **ChatGPT-Style UI**: Modern, responsive chat interface with healthcare theming
- **Real-time Responses**: Instant AI-generated answers to medical document queries
- **Context Awareness**: Maintains conversation history for coherent multi-turn discussions

### 🏥 **Healthcare-Focused Design**
- **HIPAA-Compliant Interface**: Professional medical-grade user experience
- **Medical Terminology**: Specialized understanding of healthcare language and concepts
- **Quick Actions**: Pre-defined medical query templates for common questions

### 🔒 **Security & Privacy**
- **Secure Processing**: Local document processing with encrypted communication
- **Environment Variables**: Secure API key management
- **No Data Persistence**: Documents processed in-memory for privacy

## 🛠️ Technology Stack

### **Backend**
- **Framework**: Flask 3.0+ (Python web framework)
- **AI Engine**: Google Gemini 1.5 Flash (LLM)
- **Embeddings**: Google Generative AI Embeddings
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Document Processing**: PyPDF2 for PDF text extraction
- **Text Processing**: LangChain for AI workflow orchestration

### **Frontend**
- **Styling**: Tailwind CSS with custom healthcare color scheme
- **Icons**: Font Awesome 6.0
- **Design Pattern**: Glass morphism effects with dark healthcare theme
- **Responsive**: Mobile-first design with ChatGPT-style layout

### **Infrastructure**
- **Deployment**: Render (Cloud Platform)
- **Server**: Gunicorn WSGI server
- **Environment**: Python virtual environment
- **Configuration**: Environment variables via .env

## 🚀 Project Workflow

```
1. Document Upload 📄
   ↓
2. PDF Text Extraction 🔍
   ↓
3. Text Chunking & Vectorization 🧮
   ↓
4. FAISS Vector Store Creation 📊
   ↓
5. Chat Interface Activation 💬
   ↓
6. User Question Processing ❓
   ↓
7. Semantic Search & AI Response 🤖
   ↓
8. Real-time Answer Display 📱
```

### **Detailed Process Flow**

1. **Document Ingestion**
   - User uploads PDF via modern healthcare-themed interface
   - PyPDF2 extracts text content from all pages
   - Text validation and preprocessing

2. **AI Processing Pipeline**
   - Text split into semantic chunks (1000 chars, 200 overlap)
   - Google Generative AI creates embeddings
   - FAISS builds searchable vector index

3. **Conversational AI**
   - LangChain conversation chain initialization
   - Context-aware memory management
   - Google Gemini integration for responses

4. **Interactive Experience**
   - Real-time chat with typing indicators
   - Scrollable message history
   - Quick medical query buttons

## 📁 Project Structure

```
TeleCare-AI/
├── 📄 app.py                 # Main Flask application
├── 📋 requirements.txt       # Python dependencies
├── 🔧 Procfile              # Render deployment config
├── 🔒 .env                   # Environment variables (local)
├── 📚 README.md              # Project documentation
├── 🎨 templates/
│   ├── 🏠 index.html        # Landing page (Healthcare kiosk UI)
│   └── 💬 chat.html         # Chat interface (ChatGPT-style)
└── 📂 PDFs/                 # Sample documents directory
```

## ⚙️ Installation & Setup

### **Local Development**

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd TeleCare-AI
   ```

2. **Virtual Environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate  # macOS/Linux
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   ```bash
   # Create .env file
   GOOGLE_API_KEY=your_google_ai_api_key_here
   ```

5. **Run Application**
   ```bash
   python app.py
   ```
   Visit: `http://localhost:5000`

### **Render Deployment**

1. **Connect Repository**
   - Link your GitHub repository to Render
   - Select "Web Service" deployment type

2. **Environment Configuration**
   ```
   GOOGLE_API_KEY=your_google_ai_api_key_here
   PYTHON_VERSION=3.9.18
   ```

3. **Build Settings**
   ```
   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app
   ```

4. **Auto-Deploy**
   - Automatic deployments on git push
   - Health checks and monitoring included

## 🔑 API Keys & Configuration

### **Google AI Setup**
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Create new API key
3. Add to environment variables
4. Ensure Gemini API access is enabled

### **Environment Variables**
```env
GOOGLE_API_KEY=your_actual_api_key_here
FLASK_ENV=production
PORT=5000
```

## 📊 Usage Examples

### **Medical Document Analysis**
- Upload lab reports, prescriptions, or medical summaries
- Ask: *"What are the key findings in this report?"*
- Ask: *"Explain the diagnosis and treatment plan"*
- Ask: *"List all medications mentioned with dosages"*

### **Quick Medical Queries**
- **Diagnosis & Symptoms**: Medical conditions analysis
- **Treatment & Medications**: Prescription and therapy details
- **Test Results**: Lab values and diagnostic interpretations
- **Recommendations**: Medical advice and next steps

## 🛡️ Security Features

- **Local Processing**: Documents processed in-memory only
- **API Security**: Secure Google AI API integration
- **No Data Storage**: Zero persistence of sensitive medical data
- **HTTPS Encryption**: Secure data transmission
- **Environment Protection**: API keys in environment variables

## 🔧 Troubleshooting

### **Common Issues**

1. **Missing API Key**
   ```
   Error: Google API key not found
   Solution: Add GOOGLE_API_KEY to environment variables
   ```

2. **PDF Processing Error**
   ```
   Error: Cannot read PDF file
   Solution: Ensure PDF is text-based (not scanned images)
   ```

3. **Memory Issues**
   ```
   Error: Out of memory
   Solution: Use smaller PDF files or increase server memory
   ```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

For support and questions:
- 📧 Email: support@telecare-ai.com
- 💬 Issues: GitHub Issues tab
- 📖 Documentation: This README

## 🔄 Version History

- **v1.0.0** - Initial release with Google Gemini integration
- **v1.1.0** - Added ChatGPT-style UI and healthcare theming
- **v1.2.0** - Production deployment and security enhancements

---

**Built with ❤️ for Healthcare Professionals**

*TeleCare AI Assistant - Empowering medical decision-making through advanced AI technology*
