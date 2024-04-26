from flask import Flask, request, render_template
from PyPDF2 import PdfReader
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# Initialize Firebase Admin SDK with service account key and storage bucket
cred = credentials.Certificate("your credentials.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'ats100-e78c6.appspot.com'
})

# Initialize Firestore client
db = firestore.client()

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ''
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text.strip()

# Function to categorize text
def categorize_text(text):
    # Convert the text to lowercase for case-insensitive matching
    text = text.lower()
    
    # Initialize dictionaries to store extracted information
    education = []
    skills = []
    experience = []

    # Define keywords for each category
    education_keywords = ['education', 'qualification', 'degree','Education','EDUCATION']
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

# Function to upload categorized text to Firestore
def upload_to_firestore(person_name, categorized_text):
    # Reference to a Firestore collection
    categorized_text_ref = db.collection('categorized_text')
    
    # Create a folder/document named after the person's name
    person_ref = categorized_text_ref.document(person_name)
    
    # Upload categorized text data within the person's folder/document
    person_ref.set({
        'education': categorized_text['education'],
        'skills': categorized_text['skills'],
        'experience': categorized_text['experience']
    })

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
            
            # Extract person's name from the resume filename
            person_name = resume_file.filename.split('.')[0]
            
            # Upload categorized text to Firestore with person's name
            upload_to_firestore(person_name, categorized_text)
            
            return render_template('result.html', categorized_text=categorized_text)
        else:
            return 'Unsupported file format. Please upload a PDF document.'

if __name__ == '__main__':
    app.run(debug=True)
