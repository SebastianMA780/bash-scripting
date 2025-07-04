#!/usr/bin/env python3

"""
Note: 
- this file needs execution permissions (chmod u+x clean_mv_info.py)

Description:
1. gather all files .zip from a given directory in a temp folder.
2. extract all files from the .zip files.
3. clean the files text removing lines older than DAYS_AGO.
4. remove files older than DAYS_AGO.
5. move the folders with the clean files to the destination directory.
6. remove the temp folder.

Usage:
python clean_mv_info.py [/path/to/zip/files]
"""

import os
import re
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

CHAT_FILES_KEYWORDS = ["WhatsApp", "Chat"]
TEMP_FOLDER_NAME = "temp_folder"
DAYS_AGO = 45
TIME_AGO = datetime.now() - timedelta(days=DAYS_AGO)
RE_DATE_MSG = r'\[(\d{1,2}/\d{1,2}/\d{2,4})'
RE_DATE_FILE_NAME = r'(\d{4}-\d{2}-\d{2})'

def gather_zip_files_temp(zip_dir):
    """
    Moves all .zip files containing keywords from a source directory to a temporary folder inside the source directory.
    """
    temp_dir = os.path.join(zip_dir, TEMP_FOLDER_NAME)
    print(f"Creating temporary folder at: {temp_dir}")
    os.makedirs(temp_dir, exist_ok=True)
    
    files_to_move = [
			f for f in os.listdir(zip_dir) 
			if f.endswith(".zip") and any(keyword in f for keyword in CHAT_FILES_KEYWORDS)
    ]

    if not files_to_move:
        print("No matching zip files found to move.") 
        os.rmdir(temp_dir)
        return

    for filename in files_to_move:
        source_path = os.path.join(zip_dir, filename)
        dest_path = os.path.join(temp_dir, filename)
        shutil.move(source_path, dest_path)

    print(f"Moved {len(files_to_move)} zip file(s).") 
    extract_zip_files(temp_dir)

def extract_zip_files(temp_dir):
    """
    Extracts all .zip files from a temporary folder. into the same folder
    """
    for filename in os.listdir(temp_dir):
        if filename.endswith(".zip"):
            source_path = os.path.join(temp_dir, filename)
            extract_dir = os.path.join(temp_dir, filename[:-4])
            shutil.unpack_archive(source_path, extract_dir)

    print(f"Extracted zip files.")	
    rm_zip_files(temp_dir)

def rm_zip_files(temp_dir):
	"""
	Removes all .zip files from a temporary folder.
	"""
	for filename in os.listdir(temp_dir):
		if filename.endswith(".zip"):
			source_path = os.path.join(temp_dir, filename)
			os.remove(source_path)

	print(f"Removed zip files.")	
	clean_txt_files(temp_dir)
	delete_old_files(temp_dir)

def clean_txt_files(temp_dir):
	"""
	deletes lines in .txt files in each folder older than DAYS_AGO, date format [7/3/25, 5:46:42 PM]
	"""
	for txt_path in Path(temp_dir).rglob('*.txt'):
		temp_file = txt_path.with_suffix('.tmp')
		
		try:
			with txt_path.open('r', encoding='utf-8') as infile, temp_file.open('w', encoding='utf-8') as outfile:
				for line in infile:
					if not is_date_more_than_time_ago(get_date_from_string(line, RE_DATE_MSG)):
						outfile.write(line)
			os.replace(str(temp_file), str(txt_path))
		except Exception as e:
			print(f"Error cleaning {txt_path.name}: {e}")
			if temp_file.exists():
				temp_file.unlink()
	print(f"Cleaned txt files.")

def delete_old_files(temp_dir):
	"""
	deletes files older than DAYS_AGO in the temp directory
	"""
	for file_path in Path(temp_dir).rglob('*'):
		if file_path.is_file():
			date_str = get_date_from_string(file_path.name, RE_DATE_FILE_NAME)
			if is_date_more_than_time_ago(date_str):
				file_path.unlink()
	print(f"Deleted old files.")

def is_date_more_than_time_ago(date_str):
	if not date_str:
		return False
	# Handle different date formats
	if '/' in date_str:
		# Format: MM/DD/YY
		return datetime.strptime(date_str, "%m/%d/%y") < TIME_AGO
	elif '-' in date_str and len(date_str) == 10:
		# Format: YYYY-MM-DD
		return datetime.strptime(date_str, "%Y-%m-%d") < TIME_AGO
	return False

def get_date_from_string(str_info, regex):
	match = re.search(regex, str_info)
	if match:
		return match.group(1)
	return None

# main
if __name__ == "__main__":
	if len(sys.argv) > 1:
			zip_dir = sys.argv[1]
	else:
			zip_dir = "/Users/sebastian/Downloads"
	
	if not os.path.isdir(zip_dir):
			print(f"Error: Directory not found at {zip_dir}")
			sys.exit(1)

	gather_zip_files_temp(zip_dir)


"""
 PENDING IMPROVEMENTS
 - Add cases to delete messages, for example when messages are more than 2 rows the last one is not deleted
 because it does not have the date.
"""