import requests, json

# Get credentials
with open("credentials.json", "r", encoding="utf-8") as credentialsFile:
    credentials = json.load(credentialsFile)

def getAirlineStats():
    r = requests.get(f"https://www.fsairlines.net/va_interface2.php?function=getAirlineStats&va_id=42982&format=json&apikey={credentials['fsaKey']}")
    json_data = r.json()
    if json_data["status"] == "SUCCESS":
        data = json_data["data"][0]
        return data
    else:
        return False
