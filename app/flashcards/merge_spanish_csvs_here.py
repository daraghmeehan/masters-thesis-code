import glob
import re
import pandas as pd

all_easy_csvs = [easy_csv for easy_csv in glob.glob("(Spanish Easy)*.csv")]

if all_easy_csvs != []:

    # taking all card counts (e.g. integer 5 from "...5 cards.csv") and summing
    num_easy_cards = sum(
        [
            int(re.match("\(Spanish Easy\).* (\d+) card(s)?\.csv", easy_csv).groups()[0])
            for easy_csv in all_easy_csvs
        ]
    )

    # combine all files in the list
    combined_easy_csv = pd.concat(
        [pd.read_csv(easy_csv, header=None) for easy_csv in all_easy_csvs],
        ignore_index=True,
    )

    assert len(combined_easy_csv.index) == num_easy_cards

    # export to csv
    combined_easy_csv.to_csv(
        f"Combined easy csv - {num_easy_cards} cards.csv",
        header=False,
        index=False,
    )


# repeating process for normal csvs
all_normal_csvs = [normal_csv for normal_csv in glob.glob("(Spanish)*.csv")]

if all_normal_csvs != []:

    num_normal_cards = sum(
        [
            int(re.match("\(Spanish\).* (\d+) card(s)?\.csv", normal_csv).groups()[0])
            for normal_csv in all_normal_csvs
        ]
    )

    combined_normal_csv = pd.concat(
        [pd.read_csv(normal_csv, header=None) for normal_csv in all_normal_csvs],
        ignore_index=True,
    )

    assert len(combined_normal_csv.index) == num_normal_cards

    combined_normal_csv.to_csv(
        f"Combined normal csv - {num_normal_cards} cards.csv",
        header=False,
        index=False,
    )
