import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime
import google.generativeai as genai

# Initialize session state
if 'iterations' not in st.session_state:
    st.session_state.iterations = []
if 'ai_generated_code' not in st.session_state:
    st.session_state.ai_generated_code = []

# Main app title
st.title("Code Generator")

# Configuration section
with st.expander("Configuration", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        app_version = st.text_input("App Version", "1.0.0")
        interpreter = st.text_input("Interpreter", "Python 3.9")
    with col2:
        ide = st.text_input("IDE", "VS Code")
        framework = st.text_input("Framework", "Streamlit")
    google_api_key = st.text_input("Google AI API Key", type="password")

# Iteration input section
st.header("Iterations")
def create_iteration_input(index):
    return st.text_area(
        f"Iteration #{index + 1}",
        value="# ",
        key=f"iteration_{index}"
    )

if st.button("Add Iteration"):
    st.session_state.iterations.append("")

for i in range(len(st.session_state.iterations)):
    st.session_state.iterations[i] = create_iteration_input(i)

# Action buttons
col1, col2, col3 = st.columns(3)
with col1:
    export_pdf = st.button("Export PDF")
with col2:
    generate_code = st.button("Generate Code")
with col3:
    generate_ai = st.button("Generate AI Code")

# PDF generation
def generate_pdf():
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    y = height - 50
    c.drawString(100, y, f"App Version: {app_version}")
    y -= 20
    c.drawString(100, y, f"Interpreter: {interpreter}")
    y -= 20
    c.drawString(100, y, f"IDE: {ide}")
    y -= 20
    c.drawString(100, y, f"Framework: {framework}")
    y -= 40
    
    for i, content in enumerate(st.session_state.iterations):
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(100, y, f"Iteration #{i + 1}")
        y -= 20
        for line in content.split('\n'):
            if y < 50:
                c.showPage()
                y = height - 50
            c.drawString(120, y, line[:80])
            y -= 15
    
    c.save()
    buffer.seek(0)
    return buffer

# Code generation
def generate_codebase():
    code = f"""
# App Configuration
# Version: {app_version}
# Interpreter: {interpreter}
# IDE: {ide}
# Framework: {framework}

import streamlit as st

"""
    for i, content in enumerate(st.session_state.iterations):
        first_line = content.split('\n')[0].strip()[1:].strip()
        code += f"# Iteration #{i + 1}\n"
        for line in content.split('\n')[1:]:
            if line.strip():
                code += f"st.write('{line.strip()}')\n"
    return code

# AI code generation
def generate_ai_code(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        base_code = generate_codebase()
        prompt = f"""
        Generate improved Python code based on this:
        ```python
        {base_code}
        ```
        Use {framework} framework and add detailed comments.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"AI generation failed: {str(e)}")
        return None

# Handle button actions
if export_pdf and st.session_state.iterations:
    pdf_buffer = generate_pdf()
    st.download_button(
        "Download PDF",
        pdf_buffer,
        f"config_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        "application/pdf"
    )

if generate_code and st.session_state.iterations:
    code = generate_codebase()
    st.subheader("Generated Code")
    st.code(code, language="python")

if generate_ai and st.session_state.iterations and google_api_key:
    ai_code = generate_ai_code(google_api_key)
    if ai_code:
        st.session_state.ai_generated_code.append(ai_code)
        st.subheader("AI Generated Code")
        st.code(ai_code, language="python")

# Display all AI generated codes
if st.session_state.ai_generated_code:
    st.header("Previous AI Generations")
    for i, code in enumerate(st.session_state.ai_generated_code):
        with st.expander(f"AI Generation #{i + 1}"):
            st.code(code, language="python")
            if st.button("Delete", key=f"delete_{i}"):
                st.session_state.ai_generated_code.pop(i)
                st.rerun()

if st.button("Clear All Iterations"):
    st.session_state.iterations = []
    st.session_state.ai_generated_code = []
    st.rerun()
