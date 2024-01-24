#!/bin/bash

#TODO: implement  list directories or files first (default: directories first)
file_list() {
	first_folder="$1"
	base_folder="${2:-$first_folder}"

	find "$first_folder" -mindepth 1 -maxdepth 1 -type f \( -name "*.xml" -o -name "*.html" -o -name "*.js" \) | sort | while read -r file; do
		list_excel_simple_formatting "$file" "$base_folder"
	done

	find "$first_folder" -mindepth 1 -maxdepth 1 -type d | sort | while read -r folder; do 
		file_list "$folder" "$base_folder" "$base_order";
	done
}

#This function return a output like this: ~/path;file.(html/js/xml), you can import 
#this output in a excel file and it will be placed in two columns ";" does the trick. 
list_excel_simple_formatting() {
	file_path="$1"
	base_path="$2"

	parsed_file="${file//$base_path/~}"
	before_last_slash="${parsed_file%/*}"
	after_last_slash="${parsed_file##*/}"
	echo "$before_last_slash;$after_last_slash";
}

file_list_nested_format() {
    local first_folder="$1"
    local nested_param="${2:-;}"

    # Proccess files in current level
    while IFS= read -r file; do
        list_execel_nested_formatting "$file" "$nested_param"
    done < <(find "$first_folder" -mindepth 1 -maxdepth 1 -type f \( -name "*.xml" -o -name "*.html" -o -name "*.js" \) | sort)

    # Proccess folders in current level
    while IFS= read -r folder; do
        echo "$nested_param${folder##*/}"
        file_list_nested_format "$folder" "$nested_param;"
    done < <(find "$first_folder" -mindepth 1 -maxdepth 1 -type d | sort)
}

list_execel_nested_formatting() {
	file_path="$1"
	nested_info="$2"

	file_name="${file_path##*/}"
	echo "$nested_info$file_name"
}

initial_folder="$1"

file_list_nested_format "$initial_folder"
