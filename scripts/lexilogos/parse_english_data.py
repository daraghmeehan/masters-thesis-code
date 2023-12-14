import json
from bs4 import BeautifulSoup

TIME_STAMP = "march_23"

first_languages_to_scrape = [
    "Dutch",
    "French",
    "German",
    "Italian",
    "Portuguese",
    "Spanish",
]


def extract_dictionary_links(links_paragraph):

    dictionary_links = {}

    for link in links_paragraph.find_all("a"):
        dictionary_name = link.text
        onclick_address = link["onclick"]

        if "http" not in onclick_address:
            print(f"Didn't scrape {dictionary_name}")
            continue

        assert "f.q.value" or "f.p.value" in onclick_address

        onclick_address = onclick_address.replace("href=", "")
        onclick_address = onclick_address.replace("trans();", "")

        address_components = onclick_address.split(" + ")
        assert len(address_components) in [2, 3]

        address_prefix = address_components[0].replace('"', "")
        if len(address_components) == 3:
            address_postfix = address_components[2].replace('"', "")
        else:
            address_postfix = ""

        dictionary_links[dictionary_name] = (address_prefix, address_postfix)

    return dictionary_links


for language in first_languages_to_scrape:

    with open(f"language_pages_{TIME_STAMP}/english_pages/{language}.html", "r") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")  # , from_encoding="utf-8")

    language_specific_characters = [a.text for a in soup.find_all("a", class_="lien")]

    dictionary_div = soup.find("div", class_="did")
    assert "dictionary" in dictionary_div.text

    eng_to_language_paragraph, language_to_eng_paragraph = dictionary_div.find_all("p")

    try:
        eng_to_language_links = extract_dictionary_links(language_to_eng_paragraph)
        # print(f"{language}:\n{eng_to_language_links}\n\n-----\n")
    except:
        print(f"Problem with {language}")
        exit()

    data = {
        "language_specific_characters": language_specific_characters,
        "language_to_eng": eng_to_language_links,
    }
    with open(f"json_ready_{TIME_STAMP}/english_data/{language}.json", "w") as f:
        json.dump(data, f)
