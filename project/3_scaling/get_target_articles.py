# this file creates a csv file that contains the articles listed under the Wikipedia categories for AI and ML

import requests
import csv

# takes a Wikipedia category name as an input, and outputs a list of the articles (no subcategories) listed under that category
def make_list(category_name):
    url = "https://en.wikipedia.org/w/api.php"
    members = set()
    cmcontinue = None

    # required idenfication header to make Wikipedia API calls
    headers = {
      "User-Agent": (
          "cs131project python-requests"
      )
    }

    # keep requesting data until all links are read
    while True:
        params = {
            "action": "query",
            "list": "categorymembers",
            "cmtitle": f"Category:{category_name}",
            "cmlimit": "max",
            "format": "json"
        }

        if cmcontinue:
            params["cmcontinue"] = cmcontinue
            
        response = requests.get(url, params=params, headers=headers).json()
        
        for member in response.get("query", {}).get("categorymembers", []):
            # namespace 0 = articles only
            if member["ns"] == 0:
                # replace spaces in the article name with underscores to match pageviews dataset
                members.add(member["title"].replace(" ", "_"))

        # check for more data --> if yes, keep reading
        continuation = response.get("continue")
        if not continuation:
            break
        cmcontinue = continuation.get("cmcontinue")
        
    return members

# get page lists for the AI and ML categories
ai_pages = make_list("Artificial intelligence")
ml_pages = make_list("Machine learning")
target_pages = list(ai_pages.union(ml_pages))

print(f"Total unique pages to filter: {len(target_pages)}")

# save to a csv file
with open("target_pages.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    
    for page in target_pages:
        writer.writerow([page])

print("Saved successfully to target_pages.csv")