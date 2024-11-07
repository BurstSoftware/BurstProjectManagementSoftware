import streamlit as st
from io import BytesIO
import base64
from streamlit_ace import st_ace
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Function to create download PDF link
def create_download_link_pdf(pdf_data, download_filename):
    b64 = base64.b64encode(pdf_data).decode()
    href = f'<a href="data:application/pdf;base64,{b64}" download="{download_filename}">Download PDF</a>'
    return href

# Initialize session states
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'link_dict' not in st.session_state:
    st.session_state.link_dict = {}
if 'file_dict' not in st.session_state:
    st.session_state.file_dict = {}
if 'text_dict' not in st.session_state:
    st.session_state.text_dict = {}
if 'code_dict' not in st.session_state:
    st.session_state.code_dict = {}
if 'custom_inputs' not in st.session_state:
    st.session_state.custom_inputs = {}
if 'input_counter' not in st.session_state:
    st.session_state.input_counter = 0

# Function to add new custom input field
def add_custom_input():
    st.session_state.input_counter += 1
    st.session_state.custom_inputs[st.session_state.input_counter] = {
        'label': '',
        'value': ''
    }

# Function to save custom input
def save_custom_input(counter, app_version):
    input_data = st.session_state.custom_inputs[counter]
    if input_data['label'] and input_data['value']:
        if app_version not in st.session_state.text_dict:
            st.session_state.text_dict[app_version] = []
        st.session_state.text_dict[app_version].append(
            f"{input_data['label']}: {input_data['value']}"
        )

# Main app layout
st.title("Enhanced Testing Documentation App")

# Sidebar for adding new input fields
with st.sidebar:
    st.header("Custom Input Fields")
    if st.button("Add New Input Field"):
        add_custom_input()

# Input fields
app_version = st.text_input("App Version:")
if st.button("Save App Version"):
    if app_version and app_version not in st.session_state.task_list:
        st.session_state.task_list.append(app_version)

if app_version:
    # Default inputs
    regression_notes = st.text_area("Enter Regression Testing Notes:")
    if st.button("Save Regression Testing Notes"):
        if app_version not in st.session_state.text_dict:
            st.session_state.text_dict[app_version] = []
        st.session_state.text_dict[app_version].append(f"Regression Notes: {regression_notes}")

    # Custom input fields
    st.header("Custom Input Fields")
    for counter in st.session_state.custom_inputs:
        col1, col2, col3 = st.columns([2, 3, 1])
        with col1:
            st.session_state.custom_inputs[counter]['label'] = st.text_input(
                "Field Label", key=f"label_{counter}"
            )
        with col2:
            st.session_state.custom_inputs[counter]['value'] = st.text_input(
                "Field Value", key=f"value_{counter}"
            )
        with col3:
            if st.button("Save", key=f"save_{counter}"):
                save_custom_input(counter, app_version)

    # Multiple code editors
    st.header("Code Input Sections")
    if 'code_sections' not in st.session_state:
        st.session_state.code_sections = 1

    if st.button("Add Another Code Section"):
        st.session_state.code_sections += 1

    for i in range(st.session_state.code_sections):
        st.subheader(f"Code Section {i+1}")
        code = st_ace(
            language="python",
            theme="monokai",
            key=f"ace-editor-{i}",
            placeholder="Enter your code here..."
        )
        if st.button(f"Save Code Section {i+1}"):
            if app_version not in st.session_state.code_dict:
                st.session_state.code_dict[app_version] = []
            st.session_state.code_dict[app_version].append(code)

# Display saved items
st.write("## Saved Items")
for app_version in st.session_state.task_list:
    st.write(f"### App Version: {app_version}")

    # Display text inputs
    if app_version in st.session_state.text_dict:
        st.write("#### Notes and Custom Fields:")
        for text in st.session_state.text_dict[app_version]:
            st.write(f"- {text}")

    # Display code sections
    if app_version in st.session_state.code_dict:
        st.write("#### Code Sections:")
        for i, code in enumerate(st.session_state.code_dict[app_version]):
            st.write(f"Code Section {i+1}:")
            st.code(code, language="python")

# Generate PDF
if st.button("Generate PDF"):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
    styles = getSampleStyleSheet()

    pdf_elements = []
    
    for app_version in st.session_state.task_list:
        pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))

        # Add text content
        if app_version in st.session_state.text_dict:
            pdf_elements.append(Paragraph("Notes and Custom Fields:", styles['Heading2']))
            for text in st.session_state.text_dict[app_version]:
                pdf_elements.append(Paragraph(f"- {text}", styles['Normal']))
            pdf_elements.append(Spacer(1, 10))

        # Add code content
        if app_version in st.session_state.code_dict:
            pdf_elements.append(Paragraph("Code Sections:", styles['Heading2']))
            for i, code in enumerate(st.session_state.code_dict[app_version]):
                pdf_elements.append(Paragraph(f"Code Section {i+1}:", styles['Heading3']))
                code_paragraph_style = ParagraphStyle(
                    name='CodeStyle',
                    fontName='Courier',
                    fontSize=8,
                    leftIndent=10,
                    rightIndent=10,
                    leading=8,
                    wordWrap='CJK'
                )
                code_paragraph = Preformatted(code, code_paragraph_style, maxLineLength=65)
                pdf_elements.append(code_paragraph)
                pdf_elements.append(Spacer(1, 10))

    # Build the PDF document
    doc.build(pdf_elements)
    
    # Output the PDF content
    pdf_buffer.seek(0)
    pdf_data = pdf_buffer.read()
    
    # Create download link
    st.markdown(create_download_link_pdf(pdf_data, "documentation.pdf"), unsafe_allow_html=True)
