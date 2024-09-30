#!/bin/bash

ROOT=$(dirname "$(dirname "$(realpath "$BASH_SOURCE")")")

echo "===================================="
echo "     FINDY - Lambda Generator"
echo "===================================="
echo "Version : 2024 Sep 30"
echo "Project Directory: $ROOT"
echo ""

read -p "Enter the function name: " function_name
echo ""

echo "===================================="
echo "Please select the function type:"
echo "===================================="
echo "1) Normal Lambda Function"
echo "2) API Lambda Function"
read -p "Your choice (1 or 2): " option
echo ""

TEMPLATE_DIR="$ROOT/template/lambda/python3.10"

if [[ $option -eq 1 ]]; then
    echo "Creating a Normal Lambda function..."
    TARGET_DIR="$ROOT/function/$function_name"
    mkdir -p "$TARGET_DIR"
    cp -r "$TEMPLATE_DIR/"* "$TARGET_DIR/"
    echo "✔️  $function_name function has been successfully created in the 'function' directory."
    echo "Directory: $TARGET_DIR"
elif [[ $option -eq 2 ]]; then
    echo "You selected API Lambda function."
    API_DIR="$ROOT/api"
    echo "------------------------------------"
    echo "Select an API domain option:"
    echo "------------------------------------"
    
    subdirs=($(ls -d "$API_DIR"/*/ 2>/dev/null) "Create new directory")
    select api_subdir in "${subdirs[@]}"; do
        if [[ $api_subdir == "Create new directory" ]]; then
            echo ""
            read -p "Enter the new subdirectory name: " new_dir
            selected_dir="$new_dir"
            mkdir -p "$API_DIR/$selected_dir"
            echo "✔️  New subdirectory '$new_dir' has been created."
            break
        elif [[ -n "$api_subdir" ]]; then
            selected_dir=$(basename "$api_subdir")
            echo "✔️  You selected '$selected_dir' directory."
            break
        else
            echo "⚠️  Invalid option. Please select a valid option."
        fi
    done
    
    echo "Creating the API Lambda function in the selected directory..."
    TARGET_DIR="$API_DIR/$selected_dir/$function_name"
    mkdir -p "$TARGET_DIR"
    cp -r "$TEMPLATE_DIR/"* "$TARGET_DIR/"
    echo "✔️  $function_name function has been successfully created in the '$selected_dir' directory."
    echo "Directory: $TARGET_DIR"
else
    echo "⚠️  Invalid selection. Please run the script again and select a valid option."
    exit 1
fi

echo ""
echo "===================================="
echo "   Lambda function generation complete!"
echo "===================================="
   
