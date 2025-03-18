import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from datetime import datetime
import google.generativeai as genai

# Initialize session state
if 'iteration_history' not in st.session_state:
    st.session_state.iteration_history = []  # List of all iteration states
if 'current_iteration' not in st.session_state:
    st.session_state.current_iteration = ""  # Current working iteration
if 'ai_generated_code' not in st.session_state:
    st.session_state.ai_generated_code = []  # AI-generated versions

# Main app title
st.title("Iterative Code Generator")

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

# Current iteration input
st.header("Current Iteration")
current_iteration = st.text_area(
    "Current Iteration (starts with # for app name)",
    value=st.session_state.current_iteration or "# MyApp",
    key="current_iteration"
)

# Action buttons
col1, col2, col3, col4 = st.columns(4)
with col1:
    save_iteration = st.button("Save Iteration")
with col2:
    export_pdf = st.button("Export PDF")
with col3:
    generate_code = st.button("Generate Code")
with col4:
    generate_ai = st.button("Generate AI Code")

# Save current iteration to history
if save_iteration and current_iteration.strip():
    st.session_state.iteration_history.append(current_iteration)
    st.session_state.current_iteration = current_iteration  # Keep current for further editing
    st.rerun()

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
    
    # Document all iterations from history
    for i, content in enumerate(st.session_state.iteration_history):
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
    
    # Add current iteration if not yet saved
    if current_iteration not in st.session_state.iteration_history:
        if y < 50:
            c.showPage()
            y = height - 50
        c.drawString(100, y, f"Iteration #{len(st.session_state.iteration_history) + 1} (Current)")
        y -= 20
        for line in current_iteration.split('\n'):
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

# Current Iteration
"""
    for line in current_iteration.split('\n')[1:]:  # Skip the #AppName line
        if line.strip():
            code += f"st.write('{line.strip()}')\n"
    return code

# AI code generation
def generate_ai_code(api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        base_code = generate_codebase()
        # Use regular string concatenation instead of f-string with backslashes
        prompt = (
            "Generate improved Python code based on this current iteration:\n"
            "```python\n" +
            base_code +
            "\n```\n" +
            f"Use {framework} framework and add detailed comments. Preserve the app name from the first line: {current_iteration.split('\n')[0]}"
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"AI generation failed: {str(e)}")
        return None

# Handle button actions
if export_pdf:
    if st.session_state.iteration_history or current_iteration.strip():
        pdf_buffer = generate_pdf()
        st.download_button(
            "Download PDF",
            pdf_buffer,
            f"iterations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "application/pdf"
        )
    else:
        st.warning("Add some content first!")

if generate_code and current_iteration.strip():
    code = generate_codebase()
    st.subheader("Generated Code (Current Iteration)")
    st.code(code, language="python")

if generate_ai and current_iteration.strip() and google_api_key:
    ai_code = generate_ai_code(google_api_key)
    if ai_code:
        st.session_state.ai_generated_code.append(ai_code)
        st.subheader("AI Generated Code (Current Iteration)")
        st.code(ai_code, language="python")

# Display iteration history
if st.session_state.iteration_history:
    st.header("Iteration History")
    for i, iteration in enumerate(st.session_state.iteration_history):
        with st.expander(f"Iteration #{i + 1}"):
            st.text_area(f"Iteration #{i + 1}", iteration, disabled=True)
            if st.button("Load to Current", key=f"load_{i}"):
                st.session_state.current_iteration = iteration
                st.rerun()

# Display AI generated codes
if st.session_state.ai_generated_code:
    st.header("AI Generated Versions")
    for i, code in enumerate(st.session_state.ai_generated_code):
        with st.expander(f"AI Version #{i + 1}"):
            st.code(code, language="python")
            if st.button("Delete", key=f"delete_{i}"):
                st.session_state.ai_generated_code.pop(i)
                st.rerun()

# Clear everything
if st.button("Clear All"):
    st.session_state.iteration_history = []
    st.session_state.current_iteration = ""
    st.session_state.ai_generated_code = []
    st.rerun()
