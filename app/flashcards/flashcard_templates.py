TEXT_TEMPLATE = {}

AVI_TEMPLATE = {
    "fields": [
        "Picture",
        "Audio",
        "Question Text",
        "Answer Text",
        "Hint",
        "Example Sentence(s)",
        "Other Forms",
        "Extra Info",
        "Pronunciation",
        "Question Language",
        "Answer Language",
        "Show Picture Before?",
        "Show Audio Before?",
        "Show Text Before?",
        "Source",
        "Tags",
    ],
    "types": [
        
    ]
}

field_types_actualdatatype = {
            "Question Text": "PlainT",  # "txt"
            "Answer Text": "PlainT",  # "txt"
            "Hint": "Line",  # "txt"
            "Picture": "Special Pic one",  # "jpg"
            "Is picture on front": "Checkbox",  # "1/0?? or text/nothing"
            "Audio": "Special audio one",  # "audio :)"
            "Is audio on front": "Checkbox",  # "1/0 from above"
            "Example Sentence(s)": "PlainT but smaller",  # "txt"
            "Other Forms": "same (or delete)",  # "txt"
            "Extra Info": "same",  # "txt"
            "Pronunciation": "Line edit",  # "txt"
            "Source": "PlainT but smaller",  # "txt"
            "Question Language": "LineEdit",  # "txt"
            "Answer Language": "LineEdit",  # "txt"
            "Tags": "Hidden",  # "??"
        }