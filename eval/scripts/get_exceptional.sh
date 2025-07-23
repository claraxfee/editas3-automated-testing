#!/bin/bash

CSV_FILE="exceptional.csv"  # <-- Replace with your actual CSV filename

# Loop through the CSV
tail -n +2 "$CSV_FILE" | while IFS=',' read -r project bug_number _ _ evotests_dir _; do
    # Remove whitespace if any
    project=$(echo "$project" | xargs)
    bug_number=$(echo "$bug_number" | xargs)
    evotests_dir=$(echo "$evotests_dir" | xargs)

    # Construct tarball name
    tarball="${project}${bug_number}.${evotests_dir}.tar.bz2"
    src_dir="${evotests_dir}"
    dest_dir="../${project}${bug_number}_exceptional"

    echo "Processing $project $bug_number in directory $src_dir (tarball: $tarball)"

    # Go into the source directory
    if [ -d "$src_dir" ]; then
        cd "$src_dir" || { echo "Failed to cd into $src_dir"; continue; }

        if [ -f "$tarball" ]; then
            # Make destination directory
            mkdir -p "$dest_dir"

            # Extract tarball into a temporary directory
            tmpdir=$(mktemp -d)
            tar -xjf "$tarball" -C "$tmpdir"

            # Move contents into destination
            mv "$tmpdir"/* "$dest_dir"

            # Clean up
            rm -r "$tmpdir"
            echo "Moved extracted files to $dest_dir"
        else
            echo "Tarball not found: $tarball"
        fi

        cd - > /dev/null
    else
        echo "Directory not found: $src_dir"
    fi

done

