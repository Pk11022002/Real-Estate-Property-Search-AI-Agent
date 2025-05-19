# Real Estate Property Search Assistant
**Technologies:** Streamlit · MongoDB · Azure AI

A conversational AI assistant that helps users search for real estate properties by converting natural language queries into MongoDB filters.

## Features

- **Natural Language Processing**: Understands property search queries
- **Interactive Clarification**: Asks specific questions when search criteria are incomplete
- **MongoDB Integration**: Converts queries into efficient momgodb database filters
- **Streamlit Web Interface**: User-friendly web application for property search

## Components

1. **Agent Module (`agent.py`)**
   - Core logic for query analysis and property search
   - Uses LiteLLM to interface with Azure's language model
   - Converts natural language to MongoDB queries
   - Handles incomplete queries with clarification questions

2. **Web Application (`app.py`)**
   - Streamlit-based web interface
   - Maintains conversation state
   - Displays property results in a clean format
   - Handles clarification flow

## Installation

1. Clone the repository:
   git clone https://github.com/Pk11022002/Real-Estate-Property-Search-AI-Agent.git
   cd real-estate-assistant

2. Create and activate a virtual environment:
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. Install dependencies:
    pip install -r requirements.txt

4. Add your API and database keys in a `.env` file (see the provided `.env` example):
    - LITELLM_API_KEY
    - LITELLM_BASE_URL
    - MONGO_DATABASE
    - MONGODB_URI
    - AZURE_DEPLOYMENT_ID
    - AZURE_API_VERSION

5. Usage
    streamlit run app.py



