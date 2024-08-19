import os
from typing import Dict, Any
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


def extract_dictionary_links(
    links_paragraph: BeautifulSoup, language: str
) -> Dict[str, Dict[str, Any]]:
    """
    Extracts dictionary links from a given paragraph in the HTML content for a specific language.

    Parameters:
    links_paragraph (BeautifulSoup): The HTML paragraph containing the links.
    language (str): The language for which links are being extracted.

    Returns:
    Dict[str, Dict[str, Any]]: A dictionary mapping dictionary names to their URLs and additional metadata.
    """
    dictionary_links = {}

    for link in links_paragraph.find_all("a"):
        dictionary_name = link.text
        onclick_address = link["onclick"]

        if "http" not in onclick_address:
            print(f"Didn't scrape {dictionary_name} for {language}")
            continue

        if "f.q.value" not in onclick_address and "f.p.value" not in onclick_address:
            print(f"Unexpected onclick format for {dictionary_name} in {language}")
            continue

        onclick_address = onclick_address.replace("href=", "").replace("trans();", "")

        address_components = onclick_address.split(" + ")
        if len(address_components) not in [2, 3]:
            print(
                f"Unexpected address component length for {dictionary_name} in {language}"
            )
            continue

        # E.g. prefix/postfix is before/after "hola" in "https://dictionary.reverso.net/spanish-english/hola/forced"
        address_prefix = address_components[0].replace('"', "")
        address_postfix = (
            address_components[2].replace('"', "")
            if len(address_components) == 3
            else ""
        )

        dictionary_links[dictionary_name] = {
            "url": (address_prefix, address_postfix),
            "is_favourite": False,
        }

    return dictionary_links


# Special handling for certain languages
language_names = {"Greek": "Greek (Modern)"}

# Create output directory if it doesn't exist
output_dir = f"./data/lexilogos/language_pages_cleaned_{TIME_STAMP}/"
os.makedirs(output_dir, exist_ok=True)

# Loop through languages to scrape data
for language in second_languages_to_scrape:
    language = language_names.get(language, language)

    # Open and parse the HTML file for the language
    try:
        with open(
            f"./data/lexilogos/language_pages_{TIME_STAMP}/english_pages/{language}.html",
            "r",
            encoding="utf-8",
        ) as f:
            html_content = f.read()
            soup = BeautifulSoup(
                html_content, "html.parser"
            )  # , from_encoding="utf-8")
    except FileNotFoundError:
        print(f"File for {language} not found. Skipping...")
        continue

    # Extract language-specific characters
    language_specific_characters = [a.text for a in soup.find_all("a", class_="lien")]

    # Locate the dictionary section and extract links
    try:
        dictionary_div = soup.find("div", class_="did")
        assert "dictionary" in dictionary_div.text.lower()

        eng_to_target_paragraph, target_to_eng_paragraph = dictionary_div.find_all("p")
        eng_to_target_links = extract_dictionary_links(
            target_to_eng_paragraph, language
        )
    except (AttributeError, AssertionError) as e:
        print(f"Problem with {language}: {e}")
        continue

    # Prepare data to be saved as JSON
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

    # Save the data to a JSON file
    with open(f"{output_dir}/{language}.json", "w", encoding="utf-8") as f:
        json.dump(data, f)

    print(f"Data for {language} saved successfully.")
