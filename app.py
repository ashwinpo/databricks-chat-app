import logging
import os
import streamlit as st
from model_serving_utils import query_endpoint
import base64
import fitz  # PyMuPDF
from docx import Document
import io

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

os.environ["SERVING_ENDPOINT"] = "databricks-llama-4-maverick"

# Ensure environment variable is set correctly
assert os.getenv('SERVING_ENDPOINT'), "SERVING_ENDPOINT must be set in app.yaml."

# Function to encode image to base64
def get_image_as_base64(path):
    with open(path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Function to extract text from various document types
def extract_text_from_doc(uploaded_file):
    if uploaded_file.name.endswith(".pdf"):
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            return "".join(page.get_text() for page in doc)
    elif uploaded_file.name.endswith(".docx"):
        doc = Document(io.BytesIO(uploaded_file.read()))
        return "\n".join([para.text for para in doc.paragraphs])
    elif uploaded_file.name.endswith((".txt", ".md")):
        return uploaded_file.read().decode("utf-8")
    return None

# Custom CSS for ChatGPT-like styling
st.set_page_config(
    page_title="Plastipak AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded"
)

# Get image paths
logo_path = "Plastipak-Official-Logo-Blue-PNG.png"

# Encode images to base64
try:
    logo_base64 = get_image_as_base64(logo_path)
except FileNotFoundError:
    logo_base64 = None

# Custom CSS
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Birthstone&display=swap');

    /* Main container styling */
    .main .block-container {{
        padding: 0;
        max-width: 100%;
    }}
    
    body {{
        background-color: #f7f7f8;
    }}
    
    /* Header styling */
    .header-container {{
        background: white;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        border-bottom: 1px solid #e0e0e0;
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }}
    
    .header-logo {{
        display: flex;
        align-items: center;
        gap: 1rem;
        justify-content: center;
    }}

    .header-logo img {{
        height: 60px;
    }}

    .header-logo-text {{
        font-family: 'Birthstone', cursive;
        font-size: 2.5rem;
        font-weight: 500;
        color: #009bd9;
        padding-bottom: 5px; /* Adjust for vertical alignment */
    }}
    
    /* Chat container */
    .chat-container {{
        max-width: 800px;
        margin: 0 auto;
        background: white;
        border-radius: 15px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        overflow: hidden;
        display: flex;
        flex-direction: column;
    }}
    
    /* Messages area */
    .messages-area {{
        flex: 1;
        padding: 2rem;
        overflow-y: auto;
        background: white;
    }}
    
    /* Welcome message */
    .welcome-container {{
        text-align: center;
        padding: 4rem 2rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }}

    .welcome-logo img {{
        height: 60px;
        margin-bottom: 1.5rem;
    }}

    .welcome-title {{
        font-size: 1.8rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.5rem;
    }}

    .welcome-subtitle {{
        font-size: 1.1rem;
        color: #666;
        max-width: 500px;
    }}
    
    /* Message styling */
    .message {{
        margin-bottom: 1.5rem;
        display: flex;
        align-items: flex-start;
        gap: 1rem;
    }}
    
    .message.user {{
        flex-direction: row-reverse;
    }}
    
    .message.assistant {{
        flex-direction: row;
    }}
    
    .avatar {{
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        font-size: 1.2rem;
        flex-shrink: 0;
    }}
    
    .avatar.user {{
        background: linear-gradient(135deg, #0058cc, #00a5e0);
        color: white;
    }}
    
    .avatar.assistant {{
        background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
        color: #666;
    }}
    
    .message-content {{
        background: #f8f9fa;
        padding: 1rem 1.5rem;
        border-radius: 18px;
        max-width: 70%;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        line-height: 1.6;
    }}
    
    .message.user .message-content {{
        background: linear-gradient(135deg, #0058cc, #00a5e0);
        color: white;
        border-radius: 18px 18px 4px 18px;
    }}
    
    .message.assistant .message-content {{
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 18px 18px 18px 4px;
        max-width: 85%;
    }}
    
    /* Input area */
    .input-container {{
        background: white;
        border-top: 1px solid #e9ecef;
        padding: 1.5rem 2rem;
    }}
    
    .stTextInput > div > div > input {{
        border-radius: 25px;
        border: 2px solid #e9ecef;
        padding: 1rem 1.5rem;
        font-size: 1rem;
        background: #f8f9fa;
        transition: all 0.3s ease;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: #0058cc;
        box-shadow: 0 0 0 3px rgba(0, 88, 204, 0.1);
        background: white;
    }}
    
    /* Hide default Streamlit elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Responsive design */
    @media (max-width: 768px) {{
        .message-content {{
            max-width: 85%;
        }}
        .header-title {{
            font-size: 2rem;
        }}
    }}

    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background-color: #f0f2f6;
        border-right: 1px solid #e0e0e0;
    }}

    [data-testid="stSidebar"] .stButton button {{
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        color: #333;
        text-align: left;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        font-weight: 500;
        transition: background-color 0.3s, color 0.3s, border-color 0.3s;
    }}

    [data-testid="stSidebar"] .stButton button:hover {{
        background-color: #e8eaf0;
        border-color: #c0c5d0;
    }}
    
    [data-testid="stSidebar"] .stButton button.primary {{
        background-color: #0058cc;
        color: white;
        border-color: #0058cc;
    }}
    
    [data-testid="stSidebar"] h3 {{
        color: #666;
        font-weight: 600;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        padding: 0 0.5rem;
        margin-top: 1rem;
    }}
</style>
""", unsafe_allow_html=True)

def get_user_info():
    headers = st.context.headers
    return dict(
        user_name=headers.get("X-Forwarded-Preferred-Username"),
        user_email=headers.get("X-Forwarded-Email"),
        user_id=headers.get("X-Forwarded-User"),
    )

user_info = get_user_info()

# --- Sidebar ---
with st.sidebar:
    if logo_base64:
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin-bottom: 1rem;">
            <img src="data:image/png;base64,{logo_base64}" width="200" style="display: block;">
        </div>
        """, unsafe_allow_html=True)
    
    if st.button("➕ New Chat", use_container_width=True):
        # Clear chat history and uploaded file state
        st.session_state.messages = []
        if "uploaded_file_name" in st.session_state:
            del st.session_state.uploaded_file_name
        if "document_text" in st.session_state:
            del st.session_state.document_text
        st.rerun()
    
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload a document",
        type=["pdf", "txt", "md", "docx"],
        help="Upload a document for the assistant to analyze."
    )
    
    if uploaded_file:
        st.session_state.uploaded_file_name = uploaded_file.name
        with st.spinner(f"Extracting text from {uploaded_file.name}..."):
            extracted_text = extract_text_from_doc(uploaded_file)
            if extracted_text:
                st.session_state.document_text = extracted_text
                st.success(f"✅ Ready to analyze: {uploaded_file.name}")
            else:
                st.error("❌ Could not extract text from this file type.")
    else:
        # Clear the file name and text if the uploader is cleared
        if "uploaded_file_name" in st.session_state:
            del st.session_state.uploaded_file_name
        if "document_text" in st.session_state:
            del st.session_state.document_text

# --- Main Page ---

# Header with Plastipak branding
if logo_base64:
    st.markdown(f"""
    <div class="header-container">
        <div class="header-logo">
            <img src="data:image/png;base64,{logo_base64}" alt="Plastipak Logo">
            <span class="header-logo-text">AI Assistant</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <div class="header-container">
        <h1 class="header-title">Plastipak AI Assistant</h1>
    </div>
    """, unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Main chat container
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display chat messages or welcome screen
if not st.session_state.messages:
    if logo_base64:
        st.markdown(f"""
        <div class="welcome-container">
            <div class="welcome-logo">
                <img src="data:image/png;base64,{logo_base64}" alt="Plastipak Logo">
            </div>
            <h2 class="welcome-title">How can I help you today?</h2>
            <p class="welcome-subtitle">Ask me anything about Plastipak's innovative<br>and sustainable packaging solutions.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
         st.markdown("""
        <div class="welcome-container">
            <h2 class="welcome-title">How can I help you today?</h2>
            <p class="welcome-subtitle">Ask me anything about Plastipak's innovative<br>and sustainable packaging solutions.</p>
        </div>
        """, unsafe_allow_html=True)
else:
    # Messages area
    st.markdown('<div class="messages-area">', unsafe_allow_html=True)

    # Display chat messages from history
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.markdown(f"""
            <div class="message user">
                <div class="avatar user">👤</div>
                <div class="message-content">{content}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message assistant">
                <div class="avatar assistant">🤖</div>
                <div class="message-content">{content}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# Determine placeholder text for chat input
chat_placeholder = "Ask me anything about packaging solutions..."
if "uploaded_file_name" in st.session_state:
    chat_placeholder = f"Ask a question about {st.session_state.uploaded_file_name}..."

# Accept user input
if prompt := st.chat_input(chat_placeholder):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Prepare messages for the API call
    api_messages = []

    # Add document context if it exists
    if "document_text" in st.session_state:
        context = f"Here is the content of the document '{st.session_state.uploaded_file_name}':\n\n{st.session_state.document_text}"
        api_messages.append({"role": "system", "content": context})
    
    # Add the rest of the chat history
    api_messages.extend(st.session_state.messages)

    # Query the Databricks serving endpoint
    # Note: We display the response in the next run to ensure proper layout
    with st.spinner("🤖 Thinking..."):
        assistant_response = query_endpoint(
            endpoint_name=os.getenv("SERVING_ENDPOINT"),
            messages=api_messages,
            max_tokens=800,
        )["content"]
        st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    
    # Rerun to update the display
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)