#! python3

# imports
import re
import os
import shutil

import ftfy

from hortus.date_helpers import utc_now, days_from_now, yesterday, day_is

# Variables
DATA_DIR    = r'<replace_path_...>\TouchPointScripts\MSPInvSubGroupUpload\csv_cleanah\data'
INBOX       = f'{DATA_DIR}\inbox'
OUTBOX      = f'{DATA_DIR}\outbox'
ARCHIVE     = f'{DATA_DIR}\\archive'


# Functions
def f_remove_accents(old):
    """
    https://stackoverflow.com/a/69099798
    https://stackoverflow.com/questions/517923/what-is-the-best-way-to-remove-accents-normalize-in-a-python-unicode-string
    Removes common accent characters
    Uses: regex.
    """
    new = re.sub(r'[àáâãäå]', 'a', old)
    new = re.sub(r'[ÀÁÂÃ]', 'A', new)
    new = re.sub(r'[èéêë]', 'e', new)
    new = re.sub(r'[ËÉÈÊ]', 'E', new)
    new = re.sub(r'[ìíîï]', 'i', new)
    new = re.sub(r'[ÏÍÌÎ]', 'I', new)
    new = re.sub(r'[òóôõö]', 'o', new)
    new = re.sub(r'[ÖÔÓÒ]', 'O', new)
    new = re.sub(r'[ùúûü]', 'u', new)
    new = re.sub(r'[ÛÚÙÜ]', 'U', new)
    new = re.sub(r'[ñńņň]', 'n', new)
    new = re.sub(r'[ÑŃŅŇ]', 'N', new)
    return new


def process_csv_file(inbox_csv_file: str):
    output_path = os.path.join(OUTBOX, os.path.basename(inbox_csv_file))

    with open(inbox_csv_file, "r", encoding="latin-1") as infile, \
         open(output_path, "w", encoding="utf-8") as outfile:

        for line in infile.readlines():
            outfile.write(f_remove_accents(ftfy.fix_text(line)))


def archive_file(file_to_archive: str, filename: str):
    time_prefix = utc_now().strftime("%H%M%S")
    shutil.move(file_to_archive, os.path.join(ARCHIVE, f"{time_prefix}{filename}"))


def process_csv_inbox():
    for filename in os.listdir(INBOX):
        f = os.path.join(INBOX, filename)

        if not (os.path.isfile(f) and filename.endswith('.csv')):
            continue

        process_csv_file(f)

        archive_file(f, filename)


if __name__ == "__main__":
    process_csv_inbox()
