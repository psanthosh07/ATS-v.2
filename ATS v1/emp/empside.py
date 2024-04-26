from flask import Flask, render_template
import firebase_admin
from firebase_admin import credentials, firestore
import re

app = Flask(__name__)

# Initialize Firebase Admin SDK with service account key
cred = credentials.Certificate(r"C:\Users\Sanjana\Downloads\ats100-e78c6-firebase-adminsdk-klyof-f2f1e0b08a.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

GENERAL_DATA_SCIENCE_SKILLS = {
    'python', 'r', 'sql', 'machine learning', 'data analysis', 'data visualization',
    'statistics', 'linear regression', 'logistic regression', 'decision trees', 
    'random forests', 'gradient boosting', 'neural networks', 'deep learning', 
    'natural language processing', 'clustering', 'classification', 'regression'
}

def calculate_rating(user_data):
    # Tokenize the user data using regular expressions
    user_tokens = re.findall(r'\b\w+\b', user_data)
    
    # Match tokens with general data science skills
    matched_skills = set(user_tokens) & GENERAL_DATA_SCIENCE_SKILLS
    
    # Calculate rating based on matched skills
    rating = len(matched_skills) / len(GENERAL_DATA_SCIENCE_SKILLS) * 5
    return rating

@app.route('/')
def index():
    # Retrieve all users and their categorized text from Firestore
    categorized_texts = []
    users_ref = db.collection('categorized_text').stream()
    for user in users_ref:
        data = user.to_dict()
        user_data = data['education'] + " " + data['skills'] + " " + data['experience']
        rating = calculate_rating(user_data)
        categorized_texts.append({
            'name': user.id,
            'education': data['education'],
            'skills': data['skills'],
            'experience': data['experience'],
            'rating': round(rating, 2)  # Round rating to 2 decimal places
        })
    return render_template('index.html', categorized_texts=categorized_texts)

if __name__ == '__main__':
    app.run(debug=True)
