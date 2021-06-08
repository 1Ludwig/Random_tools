import requests
from re import search
from bs4 import BeautifulSoup
import datetime


def main():
    URL = "https://www.1177.se/Stockholm/sjukdomar--besvar/lungor-och-luftvagar/inflammation-och-infektion-ilungor-och-luftror/om-covid-19--coronavirus/om-vaccin-mot-covid-19/boka-tid-for-vaccination-mot-covid-19-i-stockholms-lan/boka-tid-for-vaccination/"
    page = requests.get(URL)

    year_to_search_for = "199[0-9]"

    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find(id="content")
    slim_info = results.find_all("p", class_="preamble")

    for x in slim_info:
        if search(year_to_search_for, x.text):
            print("Time to Book Vaccine!!")
        else:
            print("Vaccination available?\nNot yet.")
            print(f"\nFrom: 1177.se\n{x.text}")
            with open("text_files/mail_message.txt", "w+") as f:
                f.write(f"Not quite there yet.\n{(datetime.datetime.now())}")
                print(datetime.datetime.now())
        # print(x.text, end='\n'*2)


if __name__ == "__main__":
    main()
