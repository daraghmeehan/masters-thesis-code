from time import sleep
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from PIL import Image

# Fetch the HTML content of the language flags list from Wiktionary
r = requests.get(
    "https://en.wiktionary.org/wiki/Wiktionary:Language_flags_list",
)

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(r.content, "html.parser", from_encoding="utf-8")

# Extract the list of languages and their corresponding flags
language_flag_list = soup.find("ul").find_all("li")

# Verify that all language list items end with ": "
assert all([language.text[-2:] == ": " for language in language_flag_list])

# List of valid image file formats
all_image_types = [".svg", ".png", ".PNG", ".gif", ".jpg"]

# Verify that all images have an appropriate file extension
assert all(
    [
        language.find("img")["alt"][-4:] in all_image_types
        for language in language_flag_list
    ]
)

# Initialize lists to store language information and problematic downloads
all_info = []
problematic_languages_and_sources = []

# Print the total number of languages found
print(f"num langs = {len(language_flag_list)}")

num_langs_done = 0

# Loop through each language and process its flag image
for language in language_flag_list:

    # Extract the language name (without the ": ")
    language_name = language.text[:-2]

    # Extract the flag image element and its source URL
    flag_image_element = language.find("img")
    flag_name = flag_image_element["alt"][:-4]  # unused for now
    flag_image_src = "http:" + flag_image_element["src"]

    # Store the extracted information for later use
    all_info.append((language_name, flag_name, flag_image_src))

    # Define the path to the flag image
    flag_path = Path(f"./Flags/_language_flag_{language_name}.png")

    # Check if the flag image already exists locally to avoid re-downloading
    if flag_path.is_file():
        print(f"Already have {language_name}.png")
        continue

    # Number of times trying to download a specific flag image
    image_download_count = 0

    # Attempt to download and save the flag image
    while True:
        image_download_count += 1
        if image_download_count > 1:
            print(f"Skipped problem language = {language_name}")
            problematic_languages_and_sources.append((language_name, flag_image_src))
            break
        try:
            # Download the image and save it locally
            sleep(0.1)  # Small delay between requests
            img = Image.open(requests.get(flag_image_src, stream=True).raw)
            img.save(f"./Flags/_language_flag_{language_name}.png")
            num_langs_done += 1
            print(f"Language {num_langs_done} ({language_name}) done")
            break
        except:
            # Handle any errors during image download and retry
            print("Image download failed")
            sleep(2)
            pass

# Print any languages for which the image download failed
if problematic_languages_and_sources != []:
    print(f"\nFailed languages:")
    for lang, source in problematic_languages_and_sources:
        print(f"{lang}")

# Save all the language and flag information to a CSV file
with open("all_flag_info.csv", "w", encoding="utf-8") as f:
    f.write("Language, Flag Name, Flag Image Src\n")
    for language_name, flag_name, flag_image_src in all_info:
        f.write(f"{language_name}, {flag_name}, {flag_image_src}\n")
