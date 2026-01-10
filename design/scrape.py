import requests
import csv
import time

contacts = []

queries = [
    "location:cambridge language:javascript",
    "location:cambridge language:typescript",
    "location:cambridge language:react",
    "location:boston language:javascript",
    "mit.edu in:email",
    "harvard.edu in:email",
]

for query in queries:
    try:
        response = requests.get(
            "https://api.github.com/search/users",
            params={"q": query, "per_page": 100}
        )
        print(f"\nQuery: {query}")
        print(f"Status: {response.status_code}")
        
        data = response.json()
        if 'items' in data:
            print(f"Found {len(data['items'])} users")
            for user in data['items']:
                # Fetch user details to get email
                user_response = requests.get(user['url'])
                user_data = user_response.json()
                
                contacts.append({
                    'username': user_data.get('login'),
                    'name': user_data.get('name'),
                    'email': user_data.get('email'),
                    'location': user_data.get('location'),
                    'github': user_data.get('html_url'),
                    'bio': user_data.get('bio'),
                })
                
            time.sleep(2)  # Rate limiting
        else:
            print(f"Error: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    time.sleep(2)  # Avoid rate limits

# Remove duplicates
seen = set()
unique_contacts = []
for c in contacts:
    if c['username'] not in seen:
        seen.add(c['username'])
        unique_contacts.append(c)

# Write to CSV
with open('contacts.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['username', 'name', 'email', 'location', 'github', 'bio'])
    writer.writeheader()
    writer.writerows(unique_contacts)

print(f"\nTotal unique contacts: {len(unique_contacts)}")
