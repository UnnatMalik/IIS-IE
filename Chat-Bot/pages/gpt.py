import PIL.Image
import google.generativeai as genai
import streamlit as st
import time
import os
import re
import PyPDF2  # Add this import
import os
import pandas
import docx
# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API'))
genai.GenerationConfig.temperature = 0.7
model = genai.GenerativeModel("gemini-2.0-flash", system_instruction="You are a kind assistant",)

# Ensure the 'files' directory exists
if not os.path.exists("files"):
    os.makedirs("files")

st.set_page_config(
    page_title="Code-GPT",
    layout="centered",
    page_icon="🤖",
    
)

# Add custom CSS for typewriter animation and centered layout
st.markdown("""
<style>
@keyframes typewriter {
    from { width: 0; }
    to { width: 100%; }
}

@keyframes blink {
    from, to { border-color: transparent; }
    50% { border-color: #ff6b6b; }
}

.typewriter-text {
    font-size: 24px;
    font-weight: 600;
    color: white;
    white-space: nowrap;
    overflow: hidden;
    border-right: 3px solid #ff6b6b;
    animation: typewriter 3s steps(30) 1s both, blink 1s infinite;
    margin: 20px 0;
    text-align: center;
}

.greeting-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100px;
    margin: 20px 0;
}



.stFileUploader {
    width: 100% !important;
}
</style>
""", unsafe_allow_html=True)

# Show greeting message with typewriter animation only if no messages exist
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "user_name" not in st.session_state:
    st.session_state["user_name"] = None

if st.session_state["user_name"] is None:
    # Add some vertical spacing
    st.write("")
    st.write("")
    st.write("")
    
    # Create centered container
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Welcome message using streamlit elements
        st.markdown("### 🤖 Welcome to Code-GPT")
        st.markdown("##### Please enter your name to get started")
        st.write("")
        
        # Create a form for name input
        with st.form("name_form", clear_on_submit=True):
            name_input = st.text_input("Your Name:", placeholder="Enter your name here...")
            submit_button = st.form_submit_button("Let's Chat! 🚀", use_container_width=True, type="primary")
            
            if submit_button and name_input.strip():
                st.session_state["user_name"] = name_input.strip()
                st.rerun()
            elif submit_button and not name_input.strip():
                st.error("Please enter your name to continue!")
    
    # Stop execution here if name is not provided
    st.stop()

st.markdown(f"""
    <div class="greeting-container">
        <div class="typewriter-text">
            Hello {st.session_state["user_name"]}👋🏻!. How can I help you today?
        </div>
    </div>
    """, unsafe_allow_html=True)

def sanitize_filename(filename):
    """Sanitize filename to only contain lowercase letters, numbers, and dashes."""
    sanitized = re.sub(r'[^a-z0-9-]', '', filename.lower())
    sanitized = sanitized.strip('-')  # Remove leading/trailing dashes
    return sanitized if sanitized else 'file'

def save_uploaded_file(uploadedfile):
    """Save uploaded file after sanitizing its name."""
    safe_filename = sanitize_filename(os.path.splitext(uploadedfile.name)[0])
    file_extension = os.path.splitext(uploadedfile.name)[1].lower()
    full_filename = f"{safe_filename}{file_extension}"
    file_path = os.path.join("files", full_filename)

    with open(file_path, "wb") as f:
        f.write(uploadedfile.getbuffer())
    
    return file_path, file_extension

def chat_bro(prompt, uploadedfile, chat_history):
    """Handles chat with optional image, PDF, or video inputs."""
    input_data = [prompt, chat_history]

    if uploadedfile:
        file_path, file_extension = save_uploaded_file(uploadedfile)

        if file_extension in ['.png', '.jpg', '.jpeg']:
            st.image(file_path, width=400)
            try:
                image = PIL.Image.open(file_path)  # ✅ Open the image correctly
                input_data.insert(1, image)  # ✅ Add image to model input
            except Exception as e:
                st.error(f"Error opening image: {e}")

        elif file_extension == ".md":
            st.success(f"Uploaded PDF: {uploadedfile.name}")
            try:
                md_text = ""
                with open(file_path, "r", encoding='utf-8') as md_file:
                    for content in md_file:
                        md_text += content + "\n"
                if md_text.strip():
                    prompt_with_md = f"Here's the content from the md file: \n\n{md_text}\n\n{prompt}"
                    input_data[0] = prompt_with_md
                else:
                    st.warning("The MD appears to be empty or unreadable")
            except Exception as e:
                st.error(f"Error processing MD: {e}")
        
        elif file_extension == ".pdf":
            st.success(f"Uploaded PDF: {uploadedfile.name}")
            try:
                pdf_text = ""
                with open(file_path, "rb") as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    for page in pdf_reader.pages:
                        pdf_text += page.extract_text() + "\n"
                
                if pdf_text.strip():
                    prompt_with_pdf = f"Here's the content from the PDF:\n\n{pdf_text}\n\n{prompt}"
                    input_data[0] = prompt_with_pdf
                else:
                    st.warning("The PDF appears to be empty or unreadable")
            except Exception as e:
                st.error(f"Error processing PDF: {e}")
        
        elif file_extension in [".csv",".xlsx"]:
            st.success(f"Uploaded Data-set : {uploadedfile.name}")
            try:
                if file_extension == ".csv":
                    df = pandas.read_csv(file_path)
                else:
                    df = pandas.read_csv(file_path)
                st.dataframe(df.head())
                prompt_with_df = f"Here's the content of the CSV/xlsx: \n\n{df.to_string()}\n\n{prompt}"
                input_data[0] = prompt_with_df

            except Exception as e:
                st.error(f"The Dataframe is not avaliable due to: {e}")

        elif file_extension == ".docx":
            st.success(f"Uploaded DOCX: {uploadedfile.name}")
            try:
                doc = docx.Document(file_path)
                docx_text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
                if docx_text.strip():
                    input_data[0] = f"Here's the content from the DOCX file:\n\n{docx_text}\n\n{prompt}"
                else:
                    st.warning("The DOCX file appears to be empty.")
            except Exception as e:
                st.error(f"Error reading DOCX file: {e}")

        elif file_extension == ".mp4":
            st.video(file_path)
            with open(file_path, "rb") as video_file:
                video_content = video_file.read()
            video_data = {"mime_type": "video/mp4", "data": video_content}
            input_data.insert(1, video_data)

    response = model.generate_content(input_data)
    return response.text

uploaded_file = st.file_uploader("Upload an image, PDF, or video", type=["jpg", "jpeg", "png", "mp4", "pdf", ".md",".csv",".xlsx"])

user_input = st.chat_input(placeholder="Enter your message")


with st.container(height=400,border=False ):
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message('User', avatar="user"):
            st.markdown(user_input)

        # Generate chat history after adding user input
        chat_history = "\n".join([f"{msg['role']}: {msg['content']}" for msg in st.session_state["messages"]])

        if uploaded_file:
            st.session_state["messages"].append({"role": "user", "content": f"Uploaded: {uploaded_file.name}"})

        with st.spinner("Bot is typing..."):
            response_text = chat_bro(user_input, uploaded_file, chat_history)
            with st.chat_message('assistant', avatar="ai"):
                response_container = st.empty()
                streamed_response = ""

                for chunk in response_text:
                    streamed_response += chunk
                    response_container.markdown(streamed_response)
                    time.sleep(0.01)

        st.session_state["messages"].append({"role": "ai", "content": streamed_response})

# uploaded_file = st.file_uploader("Upload an image, PDF, or video", type=["jpg", "jpeg", "png", "mp4", "pdf"])
