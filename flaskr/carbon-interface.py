import requests

# Replace with your actual API key
API_KEY = "8rycEWz0j91TWBcaCK6w"

# API endpoint
url = "https://www.carboninterface.com/api/v1/auth"

# Headers with the API key
headers = {
    "Authorization": f"Bearer {API_KEY}"
}

# Make the request
response = requests.get(url, headers=headers)

# Check the response
if response.status_code == 200:
    print("Auth successful:", response.json())
else:
    print(f"Failed to authenticate. Status code: {response.status_code}")
    print("Response:", response.text)