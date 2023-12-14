import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
from time import sleep

r = requests.get(
    "https://en.wiktionary.org/wiki/Wiktionary:Language_flags_list",
    allow_redirects=True,
)
soup = BeautifulSoup(r.content, "html.parser", from_encoding="utf-8")

language_flag_list = soup.find("ul").find_all("li")

# asserting formats of all elements we scrape
assert all([language.text[-2:] == ": " for language in language_flag_list])

all_image_types = [".svg", ".png", ".PNG", ".gif", ".jpg"]
assert all(
    [
        language.find("img")["alt"][-4:] in all_image_types
        for language in language_flag_list
    ]
)

all_info = []
problematic_languages_and_sources = []

print(f"num langs = {len(language_flag_list)}")
num_langs_done = 0

for language in language_flag_list:

    language_name = language.text[:-2]

    flag_image_element = language.find("img")

    flag_name = flag_image_element["alt"][:-4]  # unused!
    flag_image_src = "http:" + flag_image_element["src"]
    # print(flag_image_src + "\n")

    all_info.append((language_name, flag_name, flag_image_src))

    if os.path.isfile(f"./Flags/_language_flag_{language_name}.png"):
        print(f"Already have {language_name}.png")
        continue

    image_download_count = 0

    # downloading image
    while True:
        image_download_count += 1
        if image_download_count > 1:
            print(f"Skipped problem language = {language_name}")
            problematic_languages_and_sources.append((language_name, flag_image_src))
            break
        try:
            sleep(0.1)
            img = Image.open(requests.get(flag_image_src, stream=True).raw)
            img.save(f"./Flags/_language_flag_{language_name}.png")
            num_langs_done += 1
            print(f"Language {num_langs_done} ({language_name}) done")
            break
        except:
            print("Image download failed")
            sleep(2)
            pass

if problematic_languages_and_sources != []:
    print(f"\nFailed languages:")
    for lang, source in problematic_languages_and_sources:
        # print(f"{lang}: {source}")
        print(f"{lang}")

with open("all_flag_info.csv", "w", encoding="utf-8") as f:
    f.write("Language, Flag Name, Flag Image Src\n")
    for language_name, flag_name, flag_image_src in all_info:
        f.write(f"{language_name}, {flag_name}, {flag_image_src}\n")
