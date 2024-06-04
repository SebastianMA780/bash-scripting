#!/bin/bash

# Usage: ./parseSystemFilesTocsvList.sh /folder/target -s
usage() {
	echo "Usage: $0 [absolute path to folder (/folder/target)] [option: -n (nested) or -s (simple) (default -n)]"
	exit 1
}

if [ "$#" -lt 1 ]; then
  usage;
  exit 1
fi

LIST_FORMAT="nested"

for i in "$@"
do
case $i in
    -s*)
			LIST_FORMAT="simple"
		;;
		-n*)
			LIST_FORMAT="nested"
		;;
		*)
      # unknown option
    ;;
esac
done

file_list_simple_formatting() {
	first_folder="$1"
	base_folder="${2:-$first_folder}"

	find "$first_folder" -mindepth 1 -maxdepth 1 -type f \( -name "*.xml" -o -name "*.html" -o -name "*.js" \) | sort | while read -r file; do
		list_csv_simple_formatting "$file" "$base_folder"
	done

	find "$first_folder" -mindepth 1 -maxdepth 1 -type d | sort | while read -r folder; do 
		file_list_simple_formatting "$folder" "$base_folder" "$base_order";
	done
}

#This function return a output like this: ~/path;file.(html/js/xml), you can import 
#this output in a csv file and it will be placed in two columns ";" does the trick. 
list_csv_simple_formatting() {
	file_path="$1"
	base_path="$2"

	parsed_file="${file_path//$base_path/~}"
	before_last_slash="${parsed_file%/*}"
	after_last_slash="${parsed_file##*/}"
	echo "$before_last_slash;$after_last_slash";
}

file_list_nested_format() {
	local first_folder="$1"
	local nested_param="${2:-;}"

	# Proccess folders in current level
	while IFS= read -r folder; do
			echo "$nested_param${folder##*/}"
			file_list_nested_format "$folder" "$nested_param;"
	done < <(find "$first_folder" -mindepth 1 -maxdepth 1 -type d | sort)

	# Proccess files in current level
	while IFS= read -r file; do
			list_csv_nested_formatting "$file" "$nested_param"
	done < <(find "$first_folder" -mindepth 1 -maxdepth 1 -type f \( -name "*.xml" -o -name "*.html" -o -name "*.js" \) | sort)
}

list_csv_nested_formatting() {
	file_path="$1"
	nested_info="$2"

	file_name="${file_path##*/}"
	echo "$nested_info$file_name"

	list_special_file_info_nested_formatting "$nested_info"
}

list_special_file_info_nested_formatting() {
	nested_info="$nested_info;"
	# extract the file path inside the "file" attribute of the "<m:skin>" tag
	file_info=$(grep -o '<m:skin file="[^"]*"' "$file_path" | grep -o '"[^"]*"' | tr -d '"')
  # print the file path in the specified structure
  if [ -n "$file_info" ]; then
    my_array=($(echo $file_info))

		# clean my_array from duplicates
		my_array=($(echo "${my_array[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' '))

    for i in "${my_array[@]}"
    do
			echo "$nested_info$i"
    done
  fi
}

initial_folder="$1"

# Check if the folder exists
if [ ! -d "$initial_folder" ]; then
	echo "Folder $initial_folder does not exist"
	exit 1
fi

if [ "$LIST_FORMAT" == "simple" ]; then
	file_list_simple_formatting "$initial_folder"
else
	file_list_nested_format "$initial_folder"
fi
