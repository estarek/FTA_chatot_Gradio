# E-Invoice Chatbot: Gradio UI Design

## Overview
This document outlines the design for converting the Streamlit-based e-invoice chatbot to a Gradio-based application while maintaining all existing functionality and improving the user experience.

## Architecture Comparison

### Streamlit vs. Gradio Components

| Streamlit Component | Gradio Equivalent | Notes |
|---------------------|-------------------|-------|
| `st.sidebar` | `gr.Blocks` with column layout | Sidebar will be implemented as a left column |
| `st.session_state` | Client-side state + `gr.State` | Store chat history and settings in state objects |
| `st.selectbox` | `gr.Dropdown` | For table and domain filtering |
| `st.text_input` | `gr.Textbox` | For API key and chat input |
| `st.button` | `gr.Button` | For language selection, clear chat, etc. |
| `st.plotly_chart` | `gr.Plot` | For interactive visualizations |
| `st.cache_data` | Function caching with Python `@functools.lru_cache` | For data loading optimization |

## UI Components

### 1. Header Section
- Application title in both English and Arabic
- Brief description of the chatbot's capabilities
- Language selector buttons (English/Arabic)

### 2. Left Panel (Sidebar Equivalent)
- **Data Filter Panel**:
  - Dropdown to select specific data tables (Invoices, Items, Taxpayers, Audit Logs)
  - Dropdown to filter by domain area (Tax Compliance, Fraud Detection, Revenue Analysis, Geographic Distribution)
- **API Configuration**:
  - Text input for ChatGPT API key
  - Model selection dropdown (GPT-3.5, GPT-4)
  - Temperature/creativity slider

### 3. Main Chat Interface
- Chat history display area (scrollable)
- Message input box with send button
- Clear conversation button
- Example questions accordion

### 4. Visualization Area
- Dynamic area for displaying interactive plots
- Options to download visualizations
- Toggle between different visualization types when applicable

## User Experience Flow

1. **Initial State**:
   - User is greeted with welcome message in selected language
   - Brief instructions on how to use the chatbot
   - Suggestion to enter API key in left panel

2. **Query Processing**:
   - User enters a question
   - System analyzes question to determine relevant data tables/domains
   - If ambiguous, system may ask for clarification on which table to query
   - Loading indicator while processing

3. **Response Display**:
   - Text response in selected language
   - Relevant interactive visualization when applicable
   - Options to ask follow-up questions

4. **Error Handling**:
   - Clear error messages for missing API key
   - Guidance when questions are outside the domain scope
   - Fallback responses when data is insufficient

## Multilingual Support

### English UI Text
- All UI elements will have English labels and instructions
- Example questions in English
- System messages in English

### Arabic UI Text
- All UI elements will have Arabic translations
- Right-to-left (RTL) layout support
- Arabic example questions
- System messages in Arabic

## Interactive Visualization Integration

Gradio supports Plotly visualizations through the `gr.Plot` component, which will be used to display:

1. **Time Series Charts**:
   - For questions about trends over time
   - Interactive zoom and hover details

2. **Bar/Column Charts**:
   - For comparative questions (e.g., "Which emirate has the highest fraud rate?")
   - Color-coded by risk level or category

3. **Pie/Donut Charts**:
   - For distribution questions (e.g., "What's the distribution of invoice types?")
   - Interactive segment selection

4. **Geographic Maps**:
   - For location-based questions
   - Interactive zoom and region selection

## Module Structure

The Gradio application will maintain the same modular structure as the Streamlit version:

1. **app_gradio.py**: Main Gradio application and UI
2. **data_router.py**: Routes queries to appropriate data tables (unchanged)
3. **response_handler.py**: Handles multilingual responses and domain constraints (unchanged)
4. **response_generator.py**: Integrates with ChatGPT API for response generation (unchanged)
5. **visualization_generator.py**: Creates interactive visualizations (unchanged)

## State Management

Gradio handles state differently from Streamlit. We'll use:

1. **gr.State()** for storing:
   - Chat history
   - Selected language
   - Selected table/domain filters

2. **Function parameters** for passing state between UI interactions

## GitHub Hosting and Deployment

The Gradio application can be hosted using:

1. **Hugging Face Spaces**:
   - Free hosting for Gradio apps
   - Direct integration with GitHub repositories
   - Custom domain support

2. **GitHub Pages + Gradio Share**:
   - Host static files on GitHub Pages
   - Use Gradio Share for temporary demos

3. **Self-hosted options**:
   - Deploy as a Flask application
   - Use Docker containers
