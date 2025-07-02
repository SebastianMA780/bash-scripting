#!/bin/bash

DOWNLOADS_DIR="$HOME/Downloads"
DEST_DIR="/Users/sebastian/dev/learning/dc-account/client-management/july"

if [ ! -d "$DOWNLOADS_DIR" ]; then
    echo "Error: Downloads directory not found: $DOWNLOADS_DIR"
    exit 1
fi

if [ ! -d "$DEST_DIR" ]; then
    echo "Creating destination directory: $DEST_DIR"
    mkdir -p "$DEST_DIR"
fi

echo "Moving .zip files from $DOWNLOADS_DIR to $DEST_DIR"

zip_count=0
for zip_file in "$DOWNLOADS_DIR"/*.zip; do
    if [ -f "$zip_file" ]; then
        filename=$(basename "$zip_file")
        echo "Moving: $filename"
        mv "$zip_file" "$DEST_DIR/"
        
        if [ $? -eq 0 ]; then
            echo "Successfully moved: $filename"
            ((zip_count++))
            
            echo "Extracting: $filename"
            base_name=$(basename "$filename" .zip)
            extract_dir="$DEST_DIR/$base_name"
            
            if [ -d "$extract_dir" ]; then
                echo "Directory $base_name already exists, removing old version..."
                rm -rf "$extract_dir"
            fi
            
            mkdir -p "$extract_dir"
            unzip -q "$DEST_DIR/$filename" -d "$extract_dir/"
            
            if [ $? -eq 0 ]; then
                echo "Successfully extracted: $filename to $extract_dir"
                echo "Deleting zip file: $filename"
                rm "$DEST_DIR/$filename"
                echo "Deleted: $filename"
            else
                echo "Failed to extract: $filename"
            fi
            echo "---"
        else
            echo "Failed to move: $filename"
        fi
    fi
done

if [ $zip_count -eq 0 ]; then
    echo "No .zip files found in $DOWNLOADS_DIR"
else
    echo "Moved $zip_count .zip file(s) to $DEST_DIR"
fi