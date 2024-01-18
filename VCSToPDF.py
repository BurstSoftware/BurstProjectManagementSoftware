# Import the necessary modules
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
st.session_state.setdefault("task_list", [])
st.session_state.setdefault("link_dict", {})
st.session_state.setdefault("file_dict", {})
st.session_state.setdefault("text_dict", {})
st.session_state.setdefault("code_dict", {})

# Input fields
app_version = st.text_input("App Version:")
if st.button("Save App Version"):
    st.session_state.task_list.append(app_version)

regression_notes = st.text_area("Enter Regression Testing Notes:")
if st.button("Save Regression Testing Notes"):
    st.session_state.text_dict.setdefault(app_version, []).append(regression_notes)

# Ace editor for code
code = st_ace(language="python", theme="monokai", key="ace-editor")
if st.button("Save Code"):
    st.session_state.code_dict.setdefault(app_version, []).append(code)

# Display saved items
st.write("## Saved Items")
for app_version in st.session_state.task_list:
    st.write(f"### App Version: {app_version}")

    # Display text
    if app_version in st.session_state.text_dict:
        st.write("#### Regression Testing Notes:")
        for text in st.session_state.text_dict[app_version]:
            st.write(f"- {text}")

    # Display code
    if app_version in st.session_state.code_dict:
        st.write("#### Code:")
        for code in st.session_state.code_dict[app_version]:
            code_paragraph_style = ParagraphStyle(
                name='CodeStyle', fontName='Courier', fontSize=8, leftIndent=10, rightIndent=10, leading=8, wordWrap='CJK'
            )
            # Set a fixed width for code block to enable wrapping
            code_paragraph = Preformatted(code, code_paragraph_style, maxLineLength=65)  # Adjust maxLineLength as needed
            st.markdown(f"```\n{code}\n```")

# Generate PDF
if st.button("Generate PDF"):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
    styles = getSampleStyleSheet()

    # Create a list of elements for the PDF
    pdf_elements = []

    for app_version in st.session_state.task_list:
        pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))

        # Display text
        if app_version in st.session_state.text_dict:
            pdf_elements.append(Paragraph("Regression Testing Notes:", styles['Heading2']))
            for text in st.session_state.text_dict[app_version]:
                pdf_elements.append(Paragraph(f"- {text}", styles['Normal']))

        # Display code
        if app_version in st.session_state.code_dict:
            pdf_elements.append(Paragraph("Code:", styles['Heading2']))
            for code in st.session_state.code_dict[app_version]:
                code_paragraph_style = ParagraphStyle(
                    name='CodeStyle', fontName='Courier', fontSize=8, leftIndent=10, rightIndent=10, leading=8, wordWrap='CJK'
                )
                # Set a fixed width for code block to enable wrapping
                code_paragraph = Preformatted(code, code_paragraph_style, maxLineLength=65)  # Adjust maxLineLength as needed
                pdf_elements.append(code_paragraph)
                pdf_elements.append(Spacer(1, 10))  # Add spacing after code

    # Build the PDF document
    doc.build(pdf_elements)

    # Output the PDF content to the BytesIO buffer
    pdf_buffer.seek(0)
    pdf_data = pdf_buffer.read()

    # Create a download link for the PDF
    st.markdown(create_download_link_pdf(pdf_data, "your_file.pdf"), unsafe_allow_html=True)
