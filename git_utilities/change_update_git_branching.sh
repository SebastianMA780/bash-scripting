#!/bin/bash

# This script is used to change the branch and update it of the git repository

#Usage: 
usage() {
	echo "Usage: $0 [Absolute path of the directory] [option: -l(list) -u(update branch]. default is list"
	exit 1	
}

if [ "$#" -lt 1 ]; then
	usage;
	exit 1
fi

DIRECTORY="$1"
OPTION="list"

shift
echo "$@"

for i in "$@"
do
case $i in
		-l*)
			OPTION="list"
		;;
		-u*)
			OPTION="update"
		;;
		*)
			usage;
		;;
esac
done


list_folder_branch_info() {
	for folder in "$DIRECTORY"/*; do
			if [ -d "$folder" ]; then
				echo "processing folder: $folder -------------"
				(cd "$folder" && git status)
				echo "-------------------"
			fi
	done
}

update_folder_branch() {
	for folder in "$DIRECTORY"/*; do
		if [ -d "$folder" ]; then
			echo "processing folder: $folder"
			(cd "$folder" && git checkout master && git pull origin master)
			echo "Process finished"
		fi
	done
}

#feature/spring-upgrade
#feature/spring-upgrade

#check if the folder exists
if [ ! -d "$DIRECTORY" ]; then
	echo "Directory does not exist"
	exit 1
fi

if [ "$OPTION" == "list" ]; then
	list_folder_branch_info
elif [ "$OPTION" == "update" ]; then
	update_folder_branch
fi


# PENDING TO RESOLVE SHIFT ISSUE for ARGUMENTS AND OPTIONS
# PENDING ADD COLORS
# PENDING MAKE FETCH OPTIONAL
# ADDS ssh agent for key password
# eval $(ssh-agent -s)
# ssh-add /path/to/your/private/key