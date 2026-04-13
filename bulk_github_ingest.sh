#!/bin/bash

# ==============================================================================
# CTI Bulk GitHub Harvester
# Clones the CyberMonitor database, extracts 54 PDFs, and cleans up.
# ==============================================================================

TARGET_DIR="./data"
TEMP_REPO_DIR="./temp_cybermonitor"
PDF_TARGET_COUNT=54

# Ensure the data directory exists
mkdir -p "$TARGET_DIR"

echo "🚀 Step 1: Cloning the CyberMonitor APT Database (this may take a minute)..."
# We use --depth 1 to only pull the latest files and ignore the entire git history (saves time/bandwidth)
git clone --depth 1 https://github.com/CyberMonitor/APT_CyberCriminal_Campagin_Collections.git "$TEMP_REPO_DIR"

echo "📂 Step 2: Harvesting $PDF_TARGET_COUNT PDFs..."
# Find all PDFs in the repo, grab the first 54, and copy them to our data folder
find "$TEMP_REPO_DIR" -type f -name "*.pdf" | head -n "$PDF_TARGET_COUNT" | while read -r pdf_file; do
    filename=$(basename "$pdf_file")
    
    # Only copy if the file doesn't already exist in our data folder
    if [ ! -f "$TARGET_DIR/$filename" ]; then
        cp "$pdf_file" "$TARGET_DIR/"
        echo "   -> Copied: $filename"
    fi
done

echo "🧹 Step 3: Cleaning up temporary repository..."
rm -rf "$TEMP_REPO_DIR"

# Count total PDFs now in the data folder
TOTAL_PDFS=$(ls -1q "$TARGET_DIR"/*.pdf | wc -l)

echo "Success! Your data folder now contains $TOTAL_PDFS total Threat Reports."
