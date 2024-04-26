import firebase_admin
from firebase_admin import credentials, storage

# Initialize Firebase Admin SDK
cred = credentials.Certificate("yourcredential.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'your-storage-bucket-url'
})

# Initialize Firebase Storage
bucket = storage.bucket()

# Upload a text file
def upload_file(file_path, destination_blob_name):
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(file_path)
    print("File uploaded to Firebase Storage.")

# Example usage
if __name__ == "__main__":
    file_path = "path/to/your/text_file.txt"
    destination_blob_name = "uploaded_file.txt"
    upload_file(file_path, destination_blob_name)
