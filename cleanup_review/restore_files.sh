#!/bin/bash

# Script to restore files from cleanup folders if needed

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to restore files from a confidence folder
restore_folder() {
    local confidence_level=$1
    local folder="$confidence_level"
    
    if [ ! -d "$folder" ]; then
        echo -e "${RED}Folder $folder not found${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Restoring files from $folder...${NC}"
    
    # Move all files except REMOVAL_REASONS.md back to parent
    for file in "$folder"/*; do
        if [ -f "$file" ] && [ "$(basename "$file")" != "REMOVAL_REASONS.md" ]; then
            mv "$file" ../../
            echo -e "${GREEN}Restored: $(basename "$file")${NC}"
        fi
    done
}

# Main menu
echo -e "${GREEN}=== File Restoration Tool ===${NC}"
echo "Which files would you like to restore?"
echo "1) All files"
echo "2) High confidence files only"
echo "3) Medium confidence files only"
echo "4) Low confidence files only"
echo "5) Specific file (enter name)"
echo "6) Cancel"

read -p "Enter choice (1-6): " choice

case $choice in
    1)
        restore_folder "high_confidence"
        restore_folder "medium_confidence"
        restore_folder "low_confidence"
        ;;
    2)
        restore_folder "high_confidence"
        ;;
    3)
        restore_folder "medium_confidence"
        ;;
    4)
        restore_folder "low_confidence"
        ;;
    5)
        read -p "Enter filename: " filename
        found=false
        for folder in high_confidence medium_confidence low_confidence; do
            if [ -f "$folder/$filename" ]; then
                mv "$folder/$filename" ../../
                echo -e "${GREEN}Restored: $filename from $folder${NC}"
                found=true
                break
            fi
        done
        if [ "$found" = false ]; then
            echo -e "${RED}File $filename not found in any cleanup folder${NC}"
        fi
        ;;
    6)
        echo "Cancelled"
        exit 0
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

echo -e "${GREEN}Restoration complete!${NC}"