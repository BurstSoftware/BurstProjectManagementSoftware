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

# Predefined options
COMPILERS = ["g++ (GNU C++)", "clang++ (LLVM)", "MSVC (Microsoft Visual C++)", "icc (Intel C++ Compiler)", "MinGW-w64", "Other"]
FRAMEWORKS = ["None", "Boost", "Qt", "SDL", "SFML", "Poco", "Cinder", "Unreal Engine", "OpenFrameworks", "Other"]
BUILD_SYSTEMS = ["Make", "CMake", "Meson", "Bazel", "MSBuild", "Ninja", "Other"]
STANDARDS = ["C++98", "C++03", "C++11", "C++14", "C++17", "C++20", "C++23"]
TESTING_FRAMEWORKS = ["None", "Google Test", "Catch2", "Boost.Test", "CppUnit", "doctest", "Other"]
COMMON_FLAGS = ["-O0", "-O1", "-O2", "-O3", "-Wall", "-Wextra", "-pedantic", "-g", "-std=c++17", "-std=c++20", "-pthread"]
COMMON_LIBS = ["-lstdc++", "-lm", "-lpthread", "-lboost_system", "-lsfml-graphics", "-lqt5", "-lz"]
DEPENDENCY_MANAGERS = ["None", "vcpkg", "Conan", "apt", "yum", "Homebrew", "Other"]

# Initialize session states
if 'task_list' not in st.session_state:
    st.session_state.task_list = []
if 'text_dict' not in st.session_state:
    st.session_state.text_dict = {}
if 'code_dict' not in st.session_state:
    st.session_state.code_dict = {}
if 'file_dict' not in st.session_state:
    st.session_state.file_dict = {}
if 'meta_dict' not in st.session_state:
    st.session_state.meta_dict = {}
if 'terminal_dict' not in st.session_state:
    st.session_state.terminal_dict = {}
if 'test_results_dict' not in st.session_state:
    st.session_state.test_results_dict = {}

# Main app layout
st.title("C++ Testing Documentation App")

# Step 1: Project Setup
st.header("Step 1: Project Setup")
col1, col2 = st.columns(2)
with col1:
    app_version = st.text_input("App Version:", placeholder="e.g., 1.0.0")
with col2:
    compiler = st.selectbox("Select Compiler:", COMPILERS, help="The compiler used to build your app.")
    if compiler == "Other":
        custom_compiler = st.text_input("Specify Custom Compiler:")

col3, col4 = st.columns(2)
with col3:
    framework = st.selectbox("Select Framework:", FRAMEWORKS, help="The framework your app relies on.")
    if framework == "Other":
        custom_framework = st.text_input("Specify Custom Framework:")
with col4:
    build_system = st.selectbox("Select Build System:", BUILD_SYSTEMS, help="Tool used to manage builds.")
    if build_system == "Other":
        custom_build_system = st.text_input("Specify Custom Build System:")

cpp_standard = st.selectbox("C++ Standard:", STANDARDS, help="The C++ standard your code adheres to.")

# Compiler Dependencies
st.subheader("Compiler Dependencies")
compiler_flags = st.multiselect("Common Compiler Flags:", COMMON_FLAGS, help="Select flags or add custom ones below.")
custom_flags = st.text_input("Custom Compiler Flags:", placeholder="e.g., -fopenmp", help="Add flags not in the list.")
compiler_libs = st.multiselect("Common Libraries:", COMMON_LIBS, help="Select libraries or add custom ones below.")
custom_libs = st.text_input("Custom Libraries:", placeholder="e.g., -lmy-lib", help="Add libraries not in the list.")

# Dependency Manager
st.subheader("Dependency Manager")
dep_manager = st.selectbox("Select Dependency Manager:", DEPENDENCY_MANAGERS, help="Tool used to manage external dependencies.")
if dep_manager == "Other":
    custom_dep_manager = st.text_input("Specify Custom Dependency Manager:")

# Build Commands
st.subheader("Build Commands")
build_commands = st.text_area(
    "Enter Build Commands:",
    placeholder="e.g., g++ -O2 main.cpp -o app -lpthread",
    help="Paste the exact commands used to build your app."
)

# Testing Framework
st.subheader("Testing Framework")
testing_framework = st.selectbox("Select Testing Framework:", TESTING_FRAMEWORKS, help="Framework for unit/integration tests.")
if testing_framework == "Other":
    custom_testing_framework = st.text_input("Specify Custom Testing Framework:")

if st.button("Save Project Setup"):
    if app_version and app_version not in st.session_state.task_list:
        st.session_state.task_list.append(app_version)
        st.session_state.meta_dict[app_version] = {
            "compiler": custom_compiler if compiler == "Other" and custom_compiler else compiler,
            "framework": custom_framework if framework == "Other" and custom_framework else framework,
            "build_system": custom_build_system if build_system == "Other" and custom_build_system else build_system,
            "cpp_standard": cpp_standard,
            "compiler_flags": " ".join(compiler_flags + ([custom_flags] if custom_flags else [])),
            "compiler_libs": " ".join(compiler_libs + ([custom_libs] if custom_libs else [])),
            "dep_manager": custom_dep_manager if dep_manager == "Other" and custom_dep_manager else dep_manager,
            "build_commands": build_commands,
            "testing_framework": custom_testing_framework if testing_framework == "Other" and custom_testing_framework else testing_framework
        }

if app_version:
    # Step 2: Testing Notes
    st.header("Step 2: Testing Notes")
    regression_notes = st.text_area("Enter Regression Testing Notes:", help="Describe test cases, outcomes, or issues.")
    if st.button("Save Regression Testing Notes"):
        if app_version not in st.session_state.text_dict:
            st.session_state.text_dict[app_version] = []
        st.session_state.text_dict[app_version].append(f"Regression Notes: {regression_notes}")

    # Step 3: Test Results
    st.header("Step 3: Test Results")
    test_results_input = st.text_area(
        "Enter Test Results Manually:",
        height=200,
        help="Paste output from running tests (e.g., Google Test summary)."
    )
    test_results_file = st.file_uploader(
        "Or Upload Test Results File (.txt, .log, .json, .xml):",
        type=["txt", "log", "json", "xml"],
        key="test_file"
    )
    if st.button("Save Test Results"):
        if app_version not in st.session_state.test_results_dict:
            st.session_state.test_results_dict[app_version] = []
        if test_results_file:
            test_content = test_results_file.read().decode("utf-8")
            st.session_state.test_results_dict[app_version].append(f"Uploaded File: {test_results_file.name}\n{test_content}")
        elif test_results_input:
            st.session_state.test_results_dict[app_version].append(test_results_input)

    # Step 4: Terminal Output
    st.header("Step 4: Terminal Output")
    terminal_output_input = st.text_area(
        "Enter Terminal Output Manually:",
        height=200,
        help="Paste compiler output, linker errors, or runtime logs here."
    )
    terminal_output_file = st.file_uploader(
        "Or Upload Terminal Output File (.txt, .log, .json, .xml):",
        type=["txt", "log", "json", "xml"],
        key="terminal_file"
    )
    if st.button("Save Terminal Output"):
        if app_version not in st.session_state.terminal_dict:
            st.session_state.terminal_dict[app_version] = []
        if terminal_output_file:
            terminal_content = terminal_output_file.read().decode("utf-8")
            st.session_state.terminal_dict[app_version].append(f"Uploaded File: {terminal_output_file.name}\n{terminal_content}")
        elif terminal_output_input:
            st.session_state.terminal_dict[app_version].append(terminal_output_input)

    # Step 5: Code Input Sections
    st.header("Step 5: C++ Code Input Sections")
    if 'code_sections' not in st.session_state:
        st.session_state.code_sections = 1

    if st.button("Add Another Code Section"):
        st.session_state.code_sections += 1

    for i in range(st.session_state.code_sections):
        st.subheader(f"Code Section {i+1}")
        file_name = st.text_input(f"File Name {i+1}:", placeholder="e.g., main.cpp", key=f"file_{i}")
        file_version = st.text_input(f"File Version {i+1}:", placeholder="e.g., 1.0.0", key=f"fversion_{i}")
        code = st_ace(
            language="cpp",
            theme="monokai",
            key=f"ace-editor-{i}",
            placeholder="Enter your C++ code here..."
        )
        if st.button(f"Save Code Section {i+1}"):
            if app_version not in st.session_state.code_dict:
                st.session_state.code_dict[app_version] = []
                st.session_state.file_dict[app_version] = []
            st.session_state.code_dict[app_version].append(code)
            st.session_state.file_dict[app_version].append(f"{file_name} (v{file_version})")

# Display saved items
st.write("## Saved Documentation")
for app_version in st.session_state.task_list:
    st.write(f"### App Version: {app_version}")
    
    # Display metadata
    if app_version in st.session_state.meta_dict:
        meta = st.session_state.meta_dict[app_version]
        st.write(f"**Compiler:** {meta['compiler']}")
        st.write(f"**Framework:** {meta['framework']}")
        st.write(f"**Build System:** {meta['build_system']}")
        st.write(f"**C++ Standard:** {meta['cpp_standard']}")
        st.write(f"**Compiler Flags:** {meta['compiler_flags']}")
        st.write(f"**Compiler Libraries:** {meta['compiler_libs']}")
        st.write(f"**Dependency Manager:** {meta['dep_manager']}")
        st.write(f"**Build Commands:** {meta['build_commands']}")
        st.write(f"**Testing Framework:** {meta['testing_framework']}")

    # Display text inputs
    if app_version in st.session_state.text_dict:
        st.write("#### Notes:")
        for text in st.session_state.text_dict[app_version]:
            st.write(f"- {text}")

    # Display test results
    if app_version in st.session_state.test_results_dict:
        st.write("#### Test Results:")
        for i, result in enumerate(st.session_state.test_results_dict[app_version]):
            with st.expander(f"Test Result {i+1}"):
                # Detect file type and adjust language for display
                if "Uploaded File:" in result:
                    filename = result.split("\n")[0].replace("Uploaded File: ", "").strip()
                    if filename.endswith(".json"):
                        st.code(result, language="json")
                    elif filename.endswith(".xml"):
                        st.code(result, language="xml")
                    else:
                        st.code(result, language="bash")
                else:
                    st.code(result, language="bash")

    # Display terminal outputs
    if app_version in st.session_state.terminal_dict:
        st.write("#### Terminal Outputs:")
        for i, output in enumerate(st.session_state.terminal_dict[app_version]):
            with st.expander(f"Terminal Output {i+1}"):
                # Detect file type and adjust language for display
                if "Uploaded File:" in output:
                    filename = output.split("\n")[0].replace("Uploaded File: ", "").strip()
                    if filename.endswith(".json"):
                        st.code(output, language="json")
                    elif filename.endswith(".xml"):
                        st.code(output, language="xml")
                    else:
                        st.code(output, language="bash")
                else:
                    st.code(output, language="bash")

    # Display code sections with file names
    if app_version in st.session_state.code_dict:
        st.write("#### Code Sections:")
        for i, (code, file_info) in enumerate(zip(st.session_state.code_dict[app_version], st.session_state.file_dict[app_version])):
            st.write(f"Code Section {i+1} - {file_info}:")
            st.code(code, language="cpp")

# Generate PDF
if st.button("Generate PDF"):
    pdf_buffer = BytesIO()
    doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, leftMargin=36, rightMargin=36)
    styles = getSampleStyleSheet()

    pdf_elements = []
    
    for app_version in st.session_state.task_list:
        pdf_elements.append(Paragraph(f"App Version: {app_version}", styles['Heading1']))
        
        # Add metadata
        if app_version in st.session_state.meta_dict:
            meta = st.session_state.meta_dict[app_version]
            pdf_elements.append(Paragraph(f"Compiler: {meta['compiler']}", styles['Normal']))
            pdf_elements.append(Paragraph(f"Framework: {meta['framework']}", styles['Normal']))
            pdf_elements.append(Paragraph(f"Build System: {meta['build_system']}", styles['Normal']))
            pdf_elements.append(Paragraph(f"C++ Standard: {meta['cpp_standard']}", styles['Normal']))
            pdf_elements.append(Paragraph(f"Compiler Flags: {meta['compiler_flags']}", styles['Normal']))
            pdf_elements.append(Paragraph(f"Compiler Libraries: {meta['compiler_libs']}", styles['Normal']))
            pdf_elements.append(Paragraph(f"Dependency Manager: {meta['dep_manager']}", styles['Normal']))
            pdf_elements.append(Paragraph(f"Build Commands: {meta['build_commands']}", styles['Normal']))
            pdf_elements.append(Paragraph(f"Testing Framework: {meta['testing_framework']}", styles['Normal']))
            pdf_elements.append(Spacer(1, 10))

        # Add text content
        if app_version in st.session_state.text_dict:
            pdf_elements.append(Paragraph("Notes:", styles['Heading2']))
            for text in st.session_state.text_dict[app_version]:
                pdf_elements.append(Paragraph(f"- {text}", styles['Normal']))
            pdf_elements.append(Spacer(1, 10))

        # Add test results
        if app_version in st.session_state.test_results_dict:
            pdf_elements.append(Paragraph("Test Results:", styles['Heading2']))
            for i, result in enumerate(st.session_state.test_results_dict[app_version]):
                pdf_elements.append(Paragraph(f"Test Result {i+1}:", styles['Heading3']))
                code_paragraph_style = ParagraphStyle(
                    name='TestStyle',
                    fontName='Courier',
                    fontSize=8,
                    leftIndent=10,
                    rightIndent=10,
                    leading=8,
                    wordWrap='CJK'
                )
                test_paragraph = Preformatted(result, code_paragraph_style, maxLineLength=65)
                pdf_elements.append(test_paragraph)
                pdf_elements.append(Spacer(1, 10))

        # Add terminal output content
        if app_version in st.session_state.terminal_dict:
            pdf_elements.append(Paragraph("Terminal Outputs:", styles['Heading2']))
            for i, output in enumerate(st.session_state.terminal_dict[app_version]):
                pdf_elements.append(Paragraph(f"Terminal Output {i+1}:", styles['Heading3']))
                code_paragraph_style = ParagraphStyle(
                    name='TerminalStyle',
                    fontName='Courier',
                    fontSize=8,
                    leftIndent=10,
                    rightIndent=10,
                    leading=8,
                    wordWrap='CJK'
                )
                terminal_paragraph = Preformatted(output, code_paragraph_style, maxLineLength=65)
                pdf_elements.append(terminal_paragraph)
                pdf_elements.append(Spacer(1, 10))

        # Add code content with file names
        if app_version in st.session_state.code_dict:
            pdf_elements.append(Paragraph("Code Sections:", styles['Heading2']))
            for i, (code, file_info) in enumerate(zip(st.session_state.code_dict[app_version], st.session_state.file_dict[app_version])):
                pdf_elements.append(Paragraph(f"Code Section {i+1} - {file_info}:", styles['Heading3']))
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
    st.markdown(create_download_link_pdf(pdf_data, "cpp_documentation.pdf"), unsafe_allow_html=True)
