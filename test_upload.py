import requests
import os

# Create dummy image
with open('test_upload.jpg', 'wb') as f:
    f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01')

# Login to get token
login_data = {"username": "deepmediaUser@example.com", "password": "password123"}
# We are currently using form data for login because of OAuth2PasswordRequestForm
res = requests.post('http://localhost:8000/api/v1/auth/login', data=login_data)
if res.status_code != 200:
    print("Login failed, attempting register...")
    res = requests.post('http://localhost:8000/api/v1/auth/register', json={"email": "deepmediaUser@example.com", "password": "password123", "full_name": "Test"})
    res = requests.post('http://localhost:8000/api/v1/auth/login', data=login_data)

token = res.json().get('access_token')
print("Token:", token)

# Upload the file
headers = {'Authorization': f'Bearer {token}'}
files = {'file': open('test_upload.jpg', 'rb')}
print("Uploading file to fusion endpoint...")
upload_res = requests.post('http://localhost:8000/api/v1/analyze/fusion?explain=true', headers=headers, files=files)

print("Status:", upload_res.status_code)
print("Response:", upload_res.text)

# Cleanup
os.remove('test_upload.jpg')
