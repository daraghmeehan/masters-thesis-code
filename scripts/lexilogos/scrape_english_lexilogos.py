import requests
from bs4 import BeautifulSoup
from time import sleep

TIME_STAMP = "march_23"

english_homepage = "https://www.lexilogos.com/english/"

r = requests.get(
    f"{english_homepage}index.htm", allow_redirects=True
)  ##?? need redirects?
soup = BeautifulSoup(r.content, "html.parser", from_encoding="utf-8")

##!! need to add collecting "slang" links at top & "indo-european" links at bottom

# links with class "in i" are only compatible with French
all_english_compatible_languages = soup.find("div", class_="cok").select("a.in:not(.i)")

all_english_compatible_languages = {
    link.text: f"{english_homepage}{link['href']}"
    for link in all_english_compatible_languages
}

for language, page in all_english_compatible_languages.items():

    r = requests.get(page, allow_redirects=True)
    html_content = r.content

    with open(
        f"./language_pages/english_pages_{TIME_STAMP}/{language}.html", "wb+"
    ) as f:
        f.write(html_content)

    print(f"{language} done")

    sleep(3)
