from flask import Flask, render_template, request, redirect, url_for
import firebase_admin
from firebase_admin import credentials, firestore
from twilio.rest import Client
import re

app = Flask(__name__)

# Initialize Firebase Admin SDK with service account key
cred = credentials.Certificate(r"credentials.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Twilio credentials
account_sid = 'yourid'
auth_token = 'yourtoken'
twilio_client = Client(account_sid, auth_token)

# Function to calculate rank based on skills and education
def calculate_rank(applicant):
    # Define the skills required for data science (you can adjust this list as needed)
    required_skills = ["python", "machine learning", "cloud", "data analysis",'Data Science']
    # Extract skills and education from the applicant's data
    skills = applicant.get('skills', '').lower()
    education = applicant.get('education', '').lower()

    # Calculate rank based on skills and education matching
    rank = 0
    for skill in required_skills:
        if skill in skills:
            rank += 1
    if re.search(r"bachelor|master|phd", education):
        rank += 1

    return rank

# Fetch all applicants from Firestore and calculate rank for each
def get_applicants():
    applicants_ref = db.collection('categorized_text')
    applicants = []
    for doc in applicants_ref.stream():
        applicant_data = doc.to_dict()
        applicant_data['id'] = doc.id
        # Calculate rank for each applicant
        applicant_data['rank'] = calculate_rank(applicant_data)
        applicants.append(applicant_data)
    return applicants

@app.route('/')
def index():
    # Fetch all applicants from Firestore
    applicants = get_applicants()
    return render_template('employer.html', applicants=applicants)

@app.route('/select_applicant', methods=['POST'])
def select_applicant():
    # Get the selected applicant's name from the form
    selected_applicant_name = request.form['applicant_name']

    # Check if the applicant is already marked as selected
    selected_applicant = get_applicant(selected_applicant_name)
    if selected_applicant and not selected_applicant.get('selected'):
        # Mark the applicant as selected in Firestore
        mark_applicant_as_selected(selected_applicant_name)
        print(f"{selected_applicant_name} marked as selected")

        # Get the phone number of the selected applicant
        selected_applicant_phone = selected_applicant.get('phone')

        # Send message to the selected applicant
        send_message(selected_applicant_name, selected_applicant_phone)
        print(f"Message sent to {selected_applicant_phone} for {selected_applicant_name}")
    else:
        print(f"{selected_applicant_name} is already marked as selected or not found")

    # Redirect back to the index page
    return redirect(url_for('index'))

@app.route('/applicant/<name>')
def view_applicant_details(name):
    # Retrieve applicant details from Firestore
    applicant = get_applicant(name)
    if applicant:
        return render_template('applicant_details.html', applicant=applicant)
    else:
        return "Applicant not found."

def get_applicant(name):
    # Retrieve applicant from Firestore
    applicant_ref = db.collection('categorized_text').document(name)
    applicant_data = applicant_ref.get().to_dict()
    if applicant_data:
        return applicant_data
    else:
        return None

def mark_applicant_as_selected(name):
    # Mark applicant as selected in Firestore
    applicant_ref = db.collection('categorized_text').document(name)
    applicant_ref.update({'selected': True})

def send_message(applicant_name, applicant_phone):
    # Send message to the applicant
    message_body = f"Dear {applicant_name}, Congratulations! You have been selected for round 2.You will receive further details for the interview in your email."
    try:
        # Send the message
        message = twilio_client.messages.create(
            body=message_body,
            from_='+16507275165',  # Your Twilio phone number
            to=applicant_phone
        )
        print("Message sent successfully!")
    except Exception as e:
        print("Failed to send message:", e)

if __name__ == '__main__':
    app.run(debug=True)
