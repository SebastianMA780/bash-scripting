#!/bin/bash

# This script is used to change the branch and update it of the git repository

#Colors
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
DARK_BLUE="\033[38;5;21m"
DARK_ORANGE="\033[38;5;208m"
RESET="\033[0m"

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
		-b*)
			OPTION="change"
		;;
		*)
			usage;
		;;
esac
done


list_folder_branch_info() {
	for folder in "$DIRECTORY"/*; do
			if [ -d "$folder" ]; then
				echo -e "processing folder: ${BLUE}$(basename "$folder")${RESET}"
				git_status=$(cd "$folder" && git status)
				branch_line=$(echo "$git_status" | grep "On branch")
				echo -e "${GREEN}${branch_line}${RESET}"
				echo -e "$git_status" | tail -n +2
				echo -e "${DARK_ORANGE}-------------------${RESET} \n\n"
			fi
	done
}

change_folder_branch() {
	for folder in "$DIRECTORY"/*; do
		if [ -d "$folder" ]; then
			echo -e "processing folder: ${GREEN}$(basename "$folder")${RESET}"
			(cd "$folder" && git checkout master)
			echo -e "-- Process finished -- \n\n"
		fi
	done
}

update_folder_branch() {
	add_ssh_key
	for folder in "$DIRECTORY"/*; do
		if [ -d "$folder" ]; then
			echo -e "processing folder: ${GREEN}$(basename "$folder")${RESET}"
			git_status=$(cd "$folder" && git status)
			branch_line=$(echo "$git_status" | grep "On branch")
			echo -e "${GREEN}${branch_line}${RESET}"
			(cd "$folder" && git pull)
			echo -e "-- Process finished -- \n\n"
		fi
	done
}

# ADDS ssh agent for key password
add_ssh_key() {
	if ! pgrep -u "$USER" ssh-agent > /dev/null; then
    echo "Starting SSH agent..."
    eval $(ssh-agent -s)
	else
    echo "SSH agent is already running."
	fi
	echo -e "ssh-add add path"
	ssh-add /Users/sebastian/.ssh/id_rsa
}

#check if the folder exists
if [ ! -d "$DIRECTORY" ]; then
	echo "Directory does not exist"
	exit 1
fi

if [ "$OPTION" == "list" ]; then
	list_folder_branch_info
elif [ "$OPTION" == "update" ]; then
	update_folder_branch
elif [ "$OPTION" == "change" ]; then
	change_folder_branch
else
	usage
fi


# PENDING TO RESOLVE SHIFT ISSUE for ARGUMENTS AND OPTIONS
# MAKE CHANGE BRANCH THE POSSIBILITY TO CHANGE TO A SPECIFIC BRANCH
#MAKE add_ssh_key the POSSIBILITY to add the key path as an argument
