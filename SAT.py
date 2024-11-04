import requests
import json
from datetime import datetime, timezone
from time import sleep



with open("node_js_fetch.txt", "r") as fetchnode:
    headers = fetchnode.read()

headers = headers[headers.find("\"headers\": ") + 11:headers.rfind("},") + 1] #isolates json headers

headers = json.loads(headers) #loads json headers to dict

firsthalf = headers["authorization"][:headers["authorization"].find("/") + 1] #gets firsts half of auth token
secondhalf = headers["authorization"][headers["authorization"][headers["authorization"].find("/") + 1:].find("/"):] #gets second half of auth token
headers["authorization"] = firsthalf + datetime.now(timezone.utc).strftime('%Y%m%d') + secondhalf #assembles auth token with correct timestamp

headers["x-amz-date"] = datetime.now(timezone.utc).strftime('%H%M%S') #sets amz date to correct timestamp


done = False
while not done:
    response = requests.get("https://reporting-api.collegeboard.org/msreportingscores-prod/student/asmtsummaries", headers=headers)

    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")
    
    done = True
    dict = json.loads(response.text)["allSummaryReports"]
    for score in dict:
        print(score["actualTestDate"] + " | " + score["educationLevel"]["description"])
        print(score["displayTitle"])
        
        for section in score["studentScore"]["sectionScores"]:
            print(str(section["scoreTierBasicInfo"]["score"]) + " | " + str(section["scoreTierBasicInfo"]["tierName"]))
        print(score["studentScore"]["totalScore"]["scoreTierBasicInfo"]["score"])
        print("")
    

