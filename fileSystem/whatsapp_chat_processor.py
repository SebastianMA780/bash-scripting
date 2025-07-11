#!/usr/bin/env python3

"""
Note: 
- this file needs execution permissions (chmod u+x whatsapp_chat_processor.py)

Description:
1. gather all files .zip from a given directory in a temp folder.
2. extract all files from the .zip files.
3. clean the files text removing lines older than DAYS_AGO and adding processed metadata.
4. remove files older than DAYS_AGO, and files with extensions other than .txt and .opus.
	 If the file exists in the CSV data, it will be renamed with a "PROCESSED_" prefix.
5. move the folders with the clean files to the destination directory.
6. remove the temp folder.

Usage:
python whatsapp_chat_processor.py
"""

import os
import re
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path
sys.path.append('/Users/sebastian/dev/learning/bash-scripting')
from fetch_data.get_csv_data import load_csv_data

CHAT_FILES_KEYWORDS = ["WhatsApp", "Chat"]
TEMP_FOLDER_NAME = "temp_folder"
DAYS_AGO = 20
TIME_AGO = datetime.now() - timedelta(days=DAYS_AGO)
RE_DATE_MSG = r'\[(\d{1,2}/\d{1,2}/\d{2,4})'
RE_DATE_FILE_NAME = r'(\d{4}-\d{2}-\d{2})'
DEFAULT_ZIP_DIR = "/Users/sebastian/Downloads"
DEFAULT_DEST_DIR = "/Users/sebastian/dev/learning/dc-account/client-management"
CURRENT_MONTH_NAME = datetime.now().strftime("%B")
CSV_DATA_PATH = "/Users/sebastian/dev/learning/dc-account/info/Balance - Log Chats.csv"
# Global variable to cache CSV data
_csv_data = None

def gather_zip_files_temp(zip_dir, temp_dir):
    """
    Moves all .zip files containing keywords from a source directory to a temporary folder inside the source directory.
    """
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

def rm_zip_files(temp_dir):
	"""
	Removes all .zip files from a temporary folder.
	"""
	for filename in os.listdir(temp_dir):
		if filename.endswith(".zip"):
			source_path = os.path.join(temp_dir, filename)
			os.remove(source_path)

	print(f"Removed zip files.")	

def clean_txt_files(temp_dir):
	"""
	deletes lines in .txt files in each folder older than DAYS_AGO, date format [7/3/25, 5:46:42 PM]
	"""
	for txt_path in Path(temp_dir).rglob('*.txt'):
		temp_file = txt_path.with_suffix('.tmp')
		chat_folder_name = extract_contact_name(txt_path.parent.name)
		exists, next_value = check_chat_exists_in_csv(chat_folder_name)
				
		try:
			with txt_path.open('r', encoding='utf-8') as infile, temp_file.open('w', encoding='utf-8') as outfile:
				if exists and next_value:
					outfile.write(meta_format_data_txt_files(next_value))
				else:
					outfile.write(meta_format_data_txt_files(None))

				for line in infile:
					if not is_date_more_than_time_ago(get_date_from_string(line, RE_DATE_MSG)):
						outfile.write(line)
			os.replace(str(temp_file), str(txt_path))
		except Exception as e:
			print(f"Error cleaning {txt_path.name}: {e}")
			if temp_file.exists():
				temp_file.unlink()
	print(f"Cleaned txt files.")

def meta_format_data_txt_files(date_value):
	if date_value is None:
		return "NOT_PROCESSED. \n\n"
	return f"PROCESS_UNTIL {date_value}.\n\n"
	
def extract_contact_name(folder_name):
    """
    Extract contact name from WhatsApp chat folder name.
    """
    if " - " in folder_name:
        contact_part = folder_name.split(" - ", 1)[1]
        if contact_part.startswith("+"):
            return contact_part[1:]
        return contact_part
    return folder_name

def clean_chat_files(temp_dir):
	"""
	Cleans chat files in the temporary directory by removing files older than DAYS_AGO,
	ADDING a prefix "PROCESSED_" to the file name if it exists in the CSV data.
	Also removes files with extensions other than .txt and .opus.
	"""
	for file_path in Path(temp_dir).rglob('*'):
		chat_folder_name = extract_contact_name(file_path.parent.name)
		exists, next_value = check_chat_exists_in_csv(chat_folder_name)

		if file_path.is_file():
			date_str = get_date_from_string(file_path.name, RE_DATE_FILE_NAME)

			if is_date_more_than_time_ago(date_str) or file_path.suffix not in ['.txt', '.opus']:
				file_path.unlink()
			else:
				if exists and next_value:
					if date_str and is_date_lower_than_csv_value(date_str, next_value):
						new_name = f"PROCESSED_{file_path.name}"
						new_path = file_path.parent / new_name
						file_path.rename(new_path)
		
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

def is_date_lower_than_csv_value(date_str, csv_date_str):
	"""Compare if file date is lower than CSV date value."""
	try:
		file_date = datetime.strptime(date_str, "%Y-%m-%d")
		csv_date = datetime.strptime(str(csv_date_str), "%Y-%m-%d")
		
		return file_date < csv_date
	except Exception as e:
		print(f"Error comparing dates: {e}")
		return False

def get_date_from_string(str_info, regex):
	match = re.search(regex, str_info)
	if match:
		return match.group(1)
	return None

def load_csv_data_once(csv_path=CSV_DATA_PATH):
	"""Load CSV data only once and cache it."""
	global _csv_data
	if _csv_data is None:
		_csv_data = load_csv_data(csv_path)
	return _csv_data

def check_chat_exists_in_csv(chat_name, csv_path=CSV_DATA_PATH):
	"""
	Check if a chat name exists in the CSV data and return the next column value.
	
	Returns:
		tuple: (exists: bool, next_column_value: str or None)
	"""
	try:
		df = load_csv_data_once(csv_path)
		if df is not None:
			for i, column in enumerate(df.columns):
				mask = df[column].astype(str).str.contains(chat_name, case=False, na=False)
				if mask.any():
					row_idx = df[mask].index[0]
					next_value = None
					if i + 1 < len(df.columns):
						next_column = df.columns[i + 1]
						next_value = df.loc[row_idx, next_column]
					return True, next_value
			return False, None
		return False, None
	except Exception as e:
		print(f"Error checking chat in CSV: {e}")
		return False, None

def create_temp_dir(zip_dir):
	temp_dir = os.path.join(zip_dir, TEMP_FOLDER_NAME)
	print(f"Creating temporary folder at: {temp_dir}")
	os.makedirs(temp_dir, exist_ok=True)
	return temp_dir

def create_destination_dir(dest_dir):
	if not os.path.isdir(dest_dir):
		print(f"Creating destination folder at: {dest_dir}")
		os.makedirs(dest_dir, exist_ok=True)

def move_folders(temp_dir, dest_dir):
	for folder in os.listdir(temp_dir):
		source_path = os.path.join(temp_dir, folder)
		dest_path = os.path.join(dest_dir, folder)
		shutil.move(source_path, dest_path)
	print(f"Moved folders to {dest_dir}")

def execute_process(zip_dir, dest_dir):
	temp_dir = create_temp_dir(zip_dir)
	gather_zip_files_temp(zip_dir, temp_dir)
	extract_zip_files(temp_dir)	
	rm_zip_files(temp_dir)
	clean_txt_files(temp_dir)
	clean_chat_files(temp_dir)
	create_destination_dir(dest_dir)
	move_folders(temp_dir, dest_dir)
	os.rmdir(temp_dir)

# main
if __name__ == "__main__":
	if len(sys.argv) > 1:
			zip_dir = sys.argv[1]
			if len(sys.argv) > 2:
				dest_dir = sys.argv[2]
	else:
			zip_dir = DEFAULT_ZIP_DIR
			dest_dir = os.path.join(DEFAULT_DEST_DIR, CURRENT_MONTH_NAME)
	
	if not os.path.isdir(zip_dir):
			print(f"Error: Directory not found at {zip_dir}")
			sys.exit(1)

	execute_process(zip_dir, dest_dir)


"""
 PENDING IMPROVEMENTS
 - Add cases to delete messages, for example when messages are more than 2 rows the last one is not deleted
 because it does not have the date.
 - Implement parallel processing to speed up the process. is there optimization to be done?
"""
