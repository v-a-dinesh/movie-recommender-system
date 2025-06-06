import requests

API_KEY = "a315cfed271160ed969ba23972ca1188"
URL = f"https://api.themoviedb.org/3/movie/550?api_key={API_KEY}"

response = requests.get(URL)
print(response.status_code)
print(response.json())  # Check if data is returned
