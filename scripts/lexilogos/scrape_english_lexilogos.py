import requests
from bs4 import BeautifulSoup
from time import sleep

# Timestamp to differentiate data collections by date
TIME_STAMP = "feb_24"

# Base URL for the Lexilogos English homepage
english_homepage = "https://www.lexilogos.com/english/"

# Fetch the homepage content
r = requests.get(f"{english_homepage}index.htm", allow_redirects=True)
soup = BeautifulSoup(r.content, "html.parser", from_encoding="utf-8")

# TODO: Collect all other links for each language!

# Extract only English link - links with class "in i" are only compatible with French
all_english_compatible_languages = soup.find("div", class_="cok").select("a.in:not(.i)")

# Create a dictionary of language names and their corresponding URLs
all_english_compatible_languages = {
    link.text: f"{english_homepage}{link['href']}"
    for link in all_english_compatible_languages
}

# Loop through each language and download the corresponding page
for language, page in all_english_compatible_languages.items():

    # Fetch the content of the language-specific page
    r = requests.get(page)
    html_content = r.content

    # Save the HTML content to a file
    with open(
        f"./data/lexilogos/language_pages_{TIME_STAMP}/english_pages/{language}.html",
        "wb+",
    ) as f:
        f.write(html_content)

    print(f"{language} done")

    # Wait before making the next request to avoid overloading the server
    sleep(3)
