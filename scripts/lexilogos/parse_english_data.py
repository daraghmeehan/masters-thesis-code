import json
from bs4 import BeautifulSoup

TIME_STAMP = "feb_24"

first_languages_to_scrape = [
    "Dutch",
    "French",
    "German",
    "Italian",
    "Portuguese",
    "Spanish",
]

second_languages_to_scrape = [
    "Arabic",
    "Bulgarian",
    "Chinese",
    "Czech",
    "Danish",
    "Estonian",
    "Finnish",
    "Greek",
    "Hungarian",
    "Indonesian",
    "Japanese",
    "Korean",
    "Latvian",
    "Lithuanian",
    "Norwegian",
    "Polish",
    "Romanian",
    "Russian",
    "Slovak",
    "Slovenian",
    "Swedish",
    "Turkish",
    "Ukrainian",
]


def extract_dictionary_links(links_paragraph, language):

    dictionary_links = {}

    for link in links_paragraph.find_all("a"):
        dictionary_name = link.text
        onclick_address = link["onclick"]

        if "http" not in onclick_address:
            print(f"Didn't scrape {dictionary_name} for {language}")
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

        dictionary_links[dictionary_name] = {
            "url": (address_prefix, address_postfix),
            "is_favourite": False,
        }

    return dictionary_links


language_names = {"Greek": "Greek (Modern)"}

for language in second_languages_to_scrape:
    language = language_names.get(language, language)

    with open(
        f"./data/lexilogos/language_pages_{TIME_STAMP}/english_pages/{language}.html",
        "r",
        encoding="utf-8",
    ) as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")  # , from_encoding="utf-8")

    language_specific_characters = [a.text for a in soup.find_all("a", class_="lien")]

    dictionary_div = soup.find("div", class_="did")
    assert "dictionary" in dictionary_div.text

    eng_to_target_paragraph, target_to_eng_paragraph = dictionary_div.find_all("p")

    try:
        eng_to_target_links = extract_dictionary_links(
            target_to_eng_paragraph, language
        )
        # print(f"{language}:\n{eng_to_target_links}\n\n-----\n")
    except:
        print(f"Problem with {language}")
        exit()

    data = {
        "language_specific_characters": language_specific_characters,
        "dictionaries": {
            "custom_target_to_english": {},
            "custom_english_to_target": {},
            "custom_target_monolingual": {},
            "target_to_english": eng_to_target_links,
            "english_to_target": {},
            "target_monolingual": {},
        },
    }
    with open(
        f"./data/lexilogos/language_pages_cleaned_{TIME_STAMP}/{language}.json", "w"
    ) as f:
        json.dump(data, f)
