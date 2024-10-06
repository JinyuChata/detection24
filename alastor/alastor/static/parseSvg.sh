#!/bin/bash

dot_directory="./dot"
svg_directory="./dot-svg"

mkdir -p "$svg_directory"

for dot_file_path in "$dot_directory"/*.dot; do
    if [ -f "$dot_file_path" ]; then
        filename=$(basename -- "$dot_file_path")
        filename_no_ext="${filename%.dot}"
        svg_file_path="$svg_directory/$filename_no_ext.svg"
        command="dot -Tsvg -o $svg_file_path $dot_file_path"
        if $command; then
            echo "成功生成 $svg_file_path"
        else
            echo "生成 $svg_file_path 失败。"
        fi
    fi
done
