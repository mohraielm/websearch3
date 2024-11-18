import re
from bs4 import BeautifulSoup
from pymongo import MongoClient


def connect_database():
    client = MongoClient(host="localhost", port=27017)
    db = client["WebSearch3"]
    return db


def main():
    db = connect_database()
    PCol = db["professors"]
    pagesC = db["pages"]

    # target page from crawler
    TargetP = pagesC.find_one({"target": True})
    html = TargetP["html"]
    sp = BeautifulSoup(html, "html.parser")

    # finding divs w/ clearfix class
    faculty = sp.find_all("div", class_="clearfix")

    for div in faculty:
        Pinfo = {}

        # parsing through h2 tag
        nameT = div.find("h2")
        if nameT:
            Pinfo["name"] = nameT.get_text(strip=True)

        # Update 'text' to 'string' to avoid deprecation warning
        titleT = div.find("strong", string=re.compile("Title:"))
        if titleT:
            title = titleT.find_next("strong").get_text(strip=True)
            Pinfo["title"] = title

        officeT = div.find("strong", string=re.compile("Office:"))
        if officeT:
            office = officeT.find_next("strong").get_text(strip=True)
            Pinfo["office"] = office

        phoneT = div.find("strong", string=re.compile("Phone:"))
        if phoneT:
            phone = phoneT.find_next("strong").get_text(strip=True)
            Pinfo["phone"] = phone

        emailT = div.find("a", href=re.compile("mailto:"))
        if emailT:
            Pinfo["email"] = emailT.get("href").replace("mailto:", "")

        # extracting prof website if they have one
        webT = div.find("a", href=True)
        if webT and "http" in webT["href"]:
            Pinfo["website"] = webT["href"]
        else:
            Pinfo["website"] = "No website found for this prof"

        # store in mongodb
        if "name" in Pinfo:
            PCol.update_one(
                {"name": Pinfo["name"]},
                {"$set": Pinfo},
                upsert=True,
            )


if __name__ == "__main__":
    main()
