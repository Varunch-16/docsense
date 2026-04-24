📄 DocSense: Semantic Document QA using RAG
📌 Overview
DocSense is an AI-powered document assistant that allows users to upload a PDF and ask questions about it in a chat-like interface.

Instead of manually reading long documents, users can simply ask questions and get accurate answers directly from the content. The system uses a Retrieval-Augmented Generation (RAG) pipeline to ensure that answers are grounded in the uploaded document, along with source references for transparency.

❓ What Problem Does It Solve?
Working with large documents like research papers, reports, or manuals can be time-consuming. Traditional search methods rely on keywords and often fail to understand the actual meaning of a query.

DocSense solves this by:
Understanding the context of questions
Retrieving relevant sections of the document
Generating accurate answers based only on the document
Providing source references for verification

⚙️ How It Works
The system follows a simple pipeline:
User uploads a PDF
The system extracts text and tables
Content is split into smaller chunks
Each chunk is converted into embeddings
Embeddings are stored in a vector database (ChromaDB)
User asks a question
Relevant chunks are retrieved using semantic search
OpenAI generates an answer based on retrieved content
The system returns the answer with source references


🛠️ Requirements
Make sure you have:
Python 3.11
Node.js (for frontend)
Git (optional, for cloning)

⚡ Setup Instructions

1. Clone the repository
git clone https://github.com/Varunch-16/docsense.git
cd docsense

2. Create virtual environment
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1

3. Install backend dependencies
pip install -r requirements.txt

4. Set OpenAI API Key
$env:OPENAI_API_KEY="your_api_key_here"
⚠️ Important:
Do NOT share your API key
Each user must use their own key

▶️ Running the Project

Start Backend (FastAPI)
uvicorn app.main:app --reload

Backend will run at:
http://127.0.0.1:8000

API Docs:
http://127.0.0.1:8000/docs

Start Frontend (React)
Open a new terminal:
cd frontend
npm install
npm run dev

Frontend will run at:
http://localhost:5173

💬 How to Use
Open the frontend in your browser
Upload a PDF file
Wait for processing
Ask questions in the chat
View answers with source references

📌 Example Questions
What are the three paradigms of RAG?
What is the difference between Naive RAG and Modular RAG?
What criteria are used for judging good AI research?

Out-of-scope example:
What is the weather today? → System will not answer 
(correct behavior)

📎 Project Report & Presentation
📄 Final Report: [Download Report](docs/project_report.pdf)  
📊 Presentation Slides: [View Slides](docs/project_PPT.pptx)

🧠 Tech Stack
FastAPI (Backend)
React + Vite (Frontend)
ChromaDB (Vector Database)
Sentence Transformers (Embeddings)
OpenAI API (LLM)

👥 Team Members
Sai Varun Chetrypally – Core pipeline (parsing, embeddings, RAG flow, system integration)
Sriyashveer Reddy Pulapalli – Backend & API development
Rishitha Challa – Vector database & retrieval system

⚠️ Important Notes
The system processes one PDF at a time
Each new upload replaces the previous data
API key is required to generate answers
No API keys are stored in this repository

🚀 Future Improvements
Multi-document support
Better UI/UX design
Faster indexing for large files
Advanced retrieval techniques

✅ Final Note
This project demonstrates how combining retrieval with language models can create a reliable and explainable document assistant. It focuses on practical implementation and real-world usability rather than just theory.
