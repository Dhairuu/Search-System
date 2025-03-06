# Search-System
# **Dual Research Agent**

## **Overview**
The **Dual Research Agent** is an AI-powered system designed to **fetch relevant research results from the web**, store them in a **vector database**, and generate structured answers using an **LLM (Large Language Model)**. The system ensures transparency by **citing sources** and optimizes efficiency by reusing stored responses when relevant.

## **Features**
- **Web Search Integration**: Fetches search results from **Tavily API**.
- **Vector Database Memory**: Stores and retrieves past results using **ChromaDB**.
- **AI-Powered Answers**: Uses **Gemini (Google Generative AI)** for answer generation.
- **Source Citation**: Provides metadata (URLs, titles) for transparency.
- **Efficient Query Handling**: Prevents redundant searches by checking stored results.
- **Scalable Graph-Based Execution**: Built using **LangChain & LangGraph**.

## **How It Works**
1. **User inputs a query**.
2. The system **checks the vector database (ChromaDB)** for relevant past responses.
   - If found and **recent**, it retrieves and returns the answer.
   - If not, it **fetches new results** from the web.
3. The search results are **embedded using Sentence Transformers** and stored.
4. The **LLM (Gemini)** generates a structured response with cited sources.
5. The system **returns the answer to the user**.

## **Tech Stack**
- **Python**
- **LangChain & LangGraph** (for structured execution)
- **Tavily API** (for web search)
- **ChromaDB** (for vector storage)
- **Sentence Transformers** (for text embeddings)
- **Google Gemini AI** (for answer generation)

## **Installation & Setup**
### **1. Clone the Repository**
```sh
git clone https://github.com/yourusername/dual-research-agent.git
cd dual-research-agent
```

### **2. Create a Virtual Environment**
```sh
python -m venv venv
source venv/bin/activate  # For MacOS/Linux
venv\Scripts\activate    # For Windows
```

### **3. Install Dependencies**
```sh
pip install -r requirements.txt
```

### **4. Set Up Environment Variables**
Create a `.env` file in the root directory and add your API keys:
```ini
TAVILY_API_KEY=your_tavily_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### **5. Run the System**
```sh
python main.py
```

## **Usage**
1. **Start the script**: It will prompt for user input.
2. **Enter a query**: The system will process the request and return an answer.
3. **Exit**: Type `exit` to terminate the program.

## **Future Improvements**
- **Hybrid NLP-LLM Approach**: Enhance retrieval using traditional NLP techniques.
- **Better Data Management**: Implement an expiration policy for stored data.
- **GUI or API Integration**: Build a web-based interface or API for easier access.

## **Contributing**
Feel free to **fork the repo** and submit pull requests for enhancements!


## **Contact**
For any queries, reach out at [dhairyasharma16@gmail.com](mailto:dhairyasharma16@gmail.com).

