from flask import Flask, request, render_template
from PyPDF2 import PdfReader
import re

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'resume' not in request.files:
        return 'No file part'
    
    resume_file = request.files['resume']
    
    if resume_file.filename == '':
        return 'No selected file'
    
    if resume_file:
        # Check if the file is a PDF document
        if resume_file.filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(resume_file)
            categorized_text = categorize_text(text)
            return render_template('result.html', categorized_text=categorized_text)
        else:
            return 'Unsupported file format. Please upload a PDF document.'

def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text.strip()

def categorize_text(text):
    # Convert the text to lowercase for case-insensitive matching
    text = text.lower()
    
    # Initialize dictionaries to store extracted information
    education = []
    skills = []
    experience = []

    # Define keywords for each category
    education_keywords = ['education', 'qualification', 'degree']
    skills_keywords = ['skills', 'abilities', 'technologies', 'tools', 'languages']
    experience_keywords = ['experience', 'work experience', 'employment', 'professional experience']

    # Split the text into lines for easier processing
    lines = text.split('\n')

    # Iterate through each line and categorize based on keywords
    current_category = None
    for line in lines:
        if any(keyword in line for keyword in education_keywords):
            current_category = 'education'
        elif any(keyword in line for keyword in skills_keywords):
            current_category = 'skills'
        elif any(keyword in line for keyword in experience_keywords):
            current_category = 'experience'
        else:
            if current_category == 'education':
                education.append(line)
            elif current_category == 'skills':
                skills.append(line)
            elif current_category == 'experience':
                experience.append(line)

    # Return the categorized information
    return {
        'education': '\n'.join(education),
        'skills': '\n'.join(skills),
        'experience': '\n'.join(experience)
    }

if __name__ == '__main__':
    app.run(debug=True)

