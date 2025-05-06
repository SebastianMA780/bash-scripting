#!/bin/bash

#Colors
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"

project_folder_path="$1"
project_deploy_url="${2:-http://localhost:8080/citizen}"

usage() {
	echo -e "Usage: $0 [absolute path to folder (/folder/target)]"
	exit 1
}

if [ "$#" -lt 1 ]; then
	usage;
	exit 1
fi

set_vue_material_new_version() {
	PACKAGE_JSON_PATH="$project_folder_path/front-end/package.json"
	OLD_DEPENDENCY='"vue-material": "\^1\.0\.0-beta-7"'
	NEW_DEPENDENCY='"vue-material": "^1.0.0-beta-11"'

	sed -i "s/$OLD_DEPENDENCY/$NEW_DEPENDENCY/g" "$PACKAGE_JSON_PATH"

	if [ $? -eq 0 ]; then
		echo -e "${GREEN} Updated vue-material version in $PACKAGE_JSON_PATH${NC}"
	else
		echo -e "${YELLOW}Failed to update vue-material version in $PACKAGE_JSON_PATH${NC}"
	fi
}

set_server_url() {
	echo -e "${YELLOW}Setting server URL...${NC}"
	
	CONFIG_FILE="$project_folder_path/front-end/src/main.js"
	sed -i "s|export const backEndUrl = .*|export const backEndUrl = '$project_deploy_url';|" "$CONFIG_FILE"
}

install_dependencies() {
	echo -e "${YELLOW}1. Installing compilation dependencies...${NC}"

	sudo apt update
	if sudo apt install -y make build-essential libssl-dev zlib1g-dev \
		libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
		libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev \
		liblzma-dev git; then
			echo "Dependencies installed successfully."
	else
			echo "Failed to install dependencies."
			exit 1
	fi
}

clone_pyenv() {
	echo -e "${YELLOW}2. Cloning pyenv...${NC}"

	if [ -d "$HOME/.pyenv" ]; then
    echo "Directory $HOME/.pyenv already exists. Skipping clone."
	else
			if git clone https://github.com/pyenv/pyenv.git ~/.pyenv; then
					echo "${GREEN}pyenv cloned successfully.${NC}"
			else
					echo "${YELLOW}Failed to clone pyenv.${NC}"
					exit 1
			fi
	fi
}

configure_shell() {
	echo -e "${YELLOW}3. Configuring shell...${NC}"

	if ! grep -q "PYENV_ROOT=\"\$HOME/.pyenv\"" ~/.bashrc; then
    echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc
		echo -e "${GREEN}PYENV_ROOT set in ~/.bashrc${NC}"
	fi

	if ! grep -q "PATH=\"\$PYENV_ROOT/bin:\$PATH\"" ~/.bashrc; then
    echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc
		echo -e "${GREEN}PATH set in ~/.bashrc${NC}"
	fi

	if ! grep -q "eval \"\$(pyenv init -)" ~/.bashrc; then
    echo -e 'if command -v pyenv >/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bashrc
		echo -e "${GREEN}pyenv init set in ~/.bashrc${NC}"
	fi

	export PYENV_ROOT="$HOME/.pyenv"c
	export PATH="$PYENV_ROOT/bin:$PATH"
	if command -v pyenv >/dev/null 2>&1; then
			eval "$(pyenv init -)"
	fi
	source ~/.bashrc
}

install_pyenv_python() {
	echo -e "${YELLOW}4. Installing Python 2.7.18...${NC}"

	if pyenv versions | grep "2.7.18"; then
		echo -e "${GREEN}Python 2.7.18 is already installed.${NC}"
	else
    if pyenv install 2.7.18; then
        echo -e "${GREEN}Python 2.7.18 installed successfully.${NC}"
    else
				echo -e "${YELLOW}Failed to install Python 2.7.18.${NC}"
        exit 1
    fi
	fi
}

select_local_python_version() {
	echo -e "${YELLOW}5. Setting Python 2.7.18 as local version...${NC}"

	cd "$project_folder_path"

	if pyenv local 2.7.18; then
		echo echo -e "${GREEN}Python 2.7.18 set as local version.${NC}"
	else
		echo echo -e "${YELLOW}Failed to set Python 2.7.18 as local version.${NC}"
		exit 1
	fi
}

install_nvm() {
	echo -e "${YELLOW}Installing NVM...${NC}"

	if [ -d "$HOME/.nvm" ]; then
		echo -e "${GREEN}NVM is already installed.${NC}"
	else
    if curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash; then
				echo -e "${GREEN}NVM installed successfully.${NC}"
    else
				echo -e "${YELLOW}Failed to install NVM.${NC}"
				exit 1
    fi
	fi
}

load_nvm() {
	echo -e "${YELLOW}Loading NVM...${NC}"

	source ~/.nvm/nvm.sh
}

install_node_14() {
	echo -e "${YELLOW}Installing Node.js 14...${NC}"

	if nvm ls 14 | grep -q "v14."; then
	 		echo -e "${GREEN}Node.js 14 is already installed.${NC}"
	else
			if nvm install 14; then
					echo -e "${GREEN}Node.js 14 installed successfully.${NC}"
			else
					echo -e "${YELLOW}Failed to install Node.js 14.${NC}"
					exit 1
			fi
	fi
}

use_node_14() {
	nvm use 14
	echo -e "${GREEN} using $(node -v)${NC}"
}

install_node_version() {
	# Node 14 is required for the project

	install_nvm
	load_nvm
	install_node_14
	use_node_14
}

install_python_version() {
	# Python 2.7.18 is required for the project

	install_dependencies
	clone_pyenv
	configure_shell
	install_pyenv_python
	select_local_python_version
}

npm_install() {
	echo -e "${YELLOW}6. Installing npm dependencies...${NC}"

	cd "$project_folder_path/front-end"
	if npm install; then
		echo -e "${GREEN}npm dependencies installed successfully.${NC}"
	else
		echo -e "${YELLOW}Failed to install npm dependencies.${NC}"
		exit 1
	fi
}

npm_run_build() {
	echo -e "${YELLOW}7. Building the project...${NC}"

	cd "$project_folder_path/front-end"
	if npm run build; then
		echo -e "${GREEN}Project built successfully.${NC}"
	else
		echo -e "${YELLOW}Failed to build the project.${NC}"
		exit 1
	fi
}

set_routes_to_index_html() {
	echo -e "${YELLOW}Setting routes to index.html...${NC}"

	cd "$project_folder_path/front-end/dist"
	HTML_FILE="index.html"

	sed -i 's/<script type=text\/javascript src=/<script type=text\/javascript src=./g' "$HTML_FILE";
	sed -i 's/<link href=/<link href=./g' "$HTML_FILE";

	if [ $? -eq 0 ]; then
		echo -e "${GREEN}Routes set to index.html successfully.${NC}"
	else
		echo -e "${YELLOW}Failed to set routes to index.html.${NC}"
		exit 1
	fi
}

move_frontend_to_backend() {
	echo -e "${YELLOW}Moving frontend to backend...${NC}"

	rm -rf "$project_folder_path/src/main/webapp/static"
	rm "$project_folder_path/src/main/webapp/index.html"

	mv "$project_folder_path/front-end/dist/index.html" "$project_folder_path/src/main/webapp"
	mv "$project_folder_path/front-end/dist/static" "$project_folder_path/src/main/webapp"
}

# Check if the folder exists
if [ ! -d "$project_folder_path" ]; then
	echo "Folder $project_folder_path does not exist"
	exit 1
fi

set_vue_material_new_version
set_server_url
install_node_version
install_python_version
npm_install
npm_run_build
set_routes_to_index_html
move_frontend_to_backend
