# AI-Powered Document Drafting Assistant

An intelligent agent-based system for generating email drafts using Retrieval Augmented Generation (RAG).

## 🌟 Features

- **AI-powered Email Drafting**: Generate professional email drafts with contextual awareness
- **RAG Integration**: Retrieve relevant information from uploaded documents to enrich drafts
- **Multi-agent Workflow**: Collaborative agents for processing queries and generating content
- **Web Interface**: User-friendly Streamlit UI for interacting with the assistant
- **Docker Ready**: Containerized for easy deployment and scalability

## 🛠️ Tech Stack

- **LangGraph**: For building the multi-agent workflow
- **LangChain**: For building the RAG pipeline and Hugging Face model integration
- **Hugging Face**: For language models (Flan-T5, BART) and embeddings
- **Chroma**: Vector database for document retrieval 
- **Python**: Core programming language
- **Streamlit**: Web interface
- **Docker**: Containerization for deployment

## 🚀 Getting Started

### Prerequisites

- Hugging Face API token

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/drafter.py.git
cd drafter.py
```

2. Create a virtual environment and install dependencies:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows)
venv\Scripts\activate

# Activate virtual environment (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install additional required packages
pip install sentence-transformers langchain-chroma chromadb
```

3. Set up environment variables by creating a `.env` file:
```
HUGGINGFACEHUB_API_TOKEN=your_huggingface_token
```

### Running the Application

```bash
# Start the web interface
python run.py
```

#### Running Streamlit Directly

```bash
# Make sure you're in the project directory with virtual environment activated
# Then run streamlit with the app file
streamlit run src/app.py
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t drafter-app .
```

2. Run the container:
```bash
docker run -p 8501:8501 drafter-app
```

3. Access the application at http://localhost:8501

## 📂 Project Structure

```
drafter.py/
├── .env                  # Environment variables
├── Dockerfile            # Docker configuration
├── README.md             # Project documentation
├── requirements.txt      # Project dependencies
└── src/                  # Source code
    ├── __init__.py       # Package initialization
    ├── agent.py          # Agent implementation
    ├── app.py            # Streamlit web application
    ├── main.py           # Main entry point
    ├── models.py         # Model configurations
    ├── rag.py            # RAG implementation
    ├── tools.py          # Custom tools for agents
    └── utils.py          # Utility functions
```

## 🧠 How It Works

1. **Document Upload**: Users upload reference documents that contain information they want to include in their emails.

2. **RAG Processing**: Documents are processed, embedded, and stored in a vector database for semantic search.

3. **Query Handling**: User queries are processed by an intelligent agent that can understand intent and context.

4. **Information Retrieval**: The RAG system retrieves relevant information from the document database.

5. **Draft Generation**: The system generates an email draft incorporating the retrieved information and following best practices.

6. **Refinement**: Users can interact with the system to refine and improve the draft until satisfied.

## 📝 Usage Examples

- Generate a formal email to a potential client
- Draft a follow-up email including points from a previous meeting document
- Create a thank-you note with specific references to a shared experience
- Compose a request email with supporting information from uploaded materials

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.