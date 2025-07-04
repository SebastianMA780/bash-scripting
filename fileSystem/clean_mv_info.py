#!/usr/bin/env python3

"""
1. gather all files .zip from a given directory in a temp folder
2. extract all files from the .zip files
3. clean the files text
4. move the files to the destination directory
5. remove the temp folder

Note: 
- this file needs execution permissions (chmod u+x clean_mv_info.py)
"""

import os
import re
import sys
import shutil
from datetime import datetime, timedelta
from pathlib import Path

CHAT_FILES_KEYWORDS = ["WhatsApp", "Chat"]
TEMP_FOLDER_NAME = "temp_folder"
ONE_MONTH_AGO = datetime.now() - timedelta(days=30)

def gather_zip_files_temp(zip_dir):
    """
    Moves all .zip files containing keywords from a source directory to a temporary folder inside the source directory.
    """
    temp_dir = os.path.join(zip_dir, TEMP_FOLDER_NAME)
    print(f"Creating temporary folder at: {temp_dir}")
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Scanning {zip_dir} for zip files with keywords: {CHAT_FILES_KEYWORDS}")
    
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
        print(f"Moving {filename} to {temp_dir}/")
        shutil.move(source_path, dest_path)

    print(f"Moved {len(files_to_move)} file(s).") 
    extract_zip_files(temp_dir)

def extract_zip_files(temp_dir):
    """
    Extracts all .zip files from a temporary folder. into the same folder
    """
    for filename in os.listdir(temp_dir):
        if filename.endswith(".zip"):
            source_path = os.path.join(temp_dir, filename)
            extract_dir = os.path.join(temp_dir, filename[:-4])
            print(f"Extracting {filename} to {extract_dir}")
            shutil.unpack_archive(source_path, extract_dir)

    print(f"Extracted {len(os.listdir(temp_dir))} file(s).")	
    rm_zip_files(temp_dir)

def rm_zip_files(temp_dir):
	"""
	Removes all .zip files from a temporary folder.
	"""
	for filename in os.listdir(temp_dir):
		if filename.endswith(".zip"):
			source_path = os.path.join(temp_dir, filename)
			print(f"Removing {filename}")
			os.remove(source_path)

	print(f"Removed {len(os.listdir(temp_dir))} file(s).")	
	clean_txt_files(temp_dir)

def clean_txt_files(temp_dir):
	"""
	deletes lines in .txt files in each folder older than 2 months of the current month, date format [7/3/25, 5:46:42 PM]
	"""
	for txt_path in Path(temp_dir).rglob('*.txt'):
		temp_file = txt_path.with_suffix('.tmp')
		removed_count = 0
		
		try:
			with txt_path.open('r', encoding='utf-8') as infile, temp_file.open('w', encoding='utf-8') as outfile:
				for line in infile:
					if is_date_more_than_time_ago(get_date_from_msg(line)):
						removed_count += 1
					else:
						outfile.write(line)
			
			os.replace(str(temp_file), str(txt_path))
			print(f"Cleaned {txt_path.name}: removed {removed_count} lines")
		except Exception as e:
			print(f"Error cleaning {txt_path.name}: {e}")
			if temp_file.exists():
				temp_file.unlink()


def is_date_more_than_time_ago(date_str):
	if not date_str:
		return False
	return datetime.strptime(date_str, "%m/%d/%y") < ONE_MONTH_AGO

def get_date_from_msg(msg):
	match = re.search(r'\[(\d{1,2}/\d{1,2}/\d{2,4})', msg)
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
	#clean_files("/Users/sebastian/Downloads/temp_folder/")
