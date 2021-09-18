import requests, json

with open("credentials.json", "r", encoding="utf-8") as credentialsFile:
    credentials = json.load(credentialsFile)

baseUrl = "https://flyviking.net/api/index.php?"
apiKey = credentials["websiteKey"]

doNotTrack = False # Only for testing purposes.

def fileQuery(q):
    r = requests.get(f"{baseUrl}/core/search&q={q}&type=downloads_file&search_and_or=and&doNotTrack={doNotTrack}&key={apiKey}")

    json_data = r.json()
    if json_data["totalResults"] == 1:
        result = getFileById(json_data["results"][0]["itemId"])
        return result
    else:
        return json_data["totalResults"]

def getFileById(i):
    r = requests.get(f"{baseUrl}/downloads/files/{i}&key={apiKey}")

    json_data = r.json()
    if "errorCode" in json_data:
        return False
    else:
        return json_data
