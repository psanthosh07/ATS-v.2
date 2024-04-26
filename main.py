from flask import Flask, request, render_template, session
from PyPDF2 import PdfReader
import firebase_admin
from firebase_admin import credentials, firestore
from twilio.rest import Client
account_sid = 'enter your auth id'
auth_token = 'enter your auth token'
client = Client(account_sid, auth_token)
app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Initialize Firebase Admin SDK with service account key and storage bucket
cred = credentials.Certificate(r"yourcreditional.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'ats100-e78c6.appspot.com'
})

# Initialize Firestore client
db = firestore.client()

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
            name = request.form.get('name', 'Unknown')
            email = request.form.get('email', 'Unknown')
            phone = request.form.get('phone', 'Unknown')  # Extract phone number
            
            # Upload categorized text and personal information to Firestore
            upload_to_firestore(name, email, phone, categorized_text)
            
            session['name'] = name
            session['email'] = email
            session['phone'] = phone 
            send_message(name,phone) # Store personal information in session
            return render_template('result.html', categorized_text=categorized_text, name=name, email=email, phone=phone)
        else:
            return 'Unsupported file format. Please upload a PDF document.'

@app.route('/submission_confirmation')
def submission_confirmation():
    return render_template('submission_confirmation.html')

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

def upload_to_firestore(name, email, phone, categorized_text):
    # Reference to a Firestore collection
    categorized_text_ref = db.collection('categorized_text')
    
    # Create a document named after the person's name
    person_ref = categorized_text_ref.document(name)
    
    # Upload categorized text and personal information
    person_ref.set({
        'name': name,
        'email': email,
        'phone': phone,
        'education': categorized_text['education'],
        'skills': categorized_text['skills'],
        'experience': categorized_text['experience']
    })
def send_message(name, recipient_phone_number):
    # Send a message to the applicant
    message_body = f"Dear {name}, We have received your application. Thank you for applying! Best regards, Team ATS"

    try:
        # Send the message
        message = client.messages.create(
            body=message_body,
            from_='+16507275165',  # Your Twilio phone number
            to=recipient_phone_number
        )
        print("Message sent successfully!")
    except Exception as e:
        print("Failed to send message:", e)

if __name__ == '__main__':
    app.run(debug=True)
