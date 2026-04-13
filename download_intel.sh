#!/bin/bash

# ==============================================================================
# CTI Bulk Ingestion Downloader
# Automates the retrieval of high-density IOC threat reports for the RAG Pipeline
# ==============================================================================

# Define the target data directory
TARGET_DIR="./data"

# Ensure the directory exists
mkdir -p "$TARGET_DIR"

# Array of verified, high-density CTI PDFs (Ransomware, APTs, Zero-Days)
URLS=(
    "https://www.cisa.gov/sites/default/files/2025-12/aa24-109a-stopransomware-akira-ransomware.pdf"
    "https://www.cisa.gov/sites/default/files/2024-07/aa24-207a-dprk-cyber-group-conducts-global-espionage-campaign.pdf"
    "https://www.cisa.gov/sites/default/files/2024-08/aa24-241a-iran-based-cyber-actors-enabling-ransomware-attacks-on-us-organizations_0.pdf"
    "https://www.cisa.gov/sites/default/files/2023-09/aa23-250a-apt-actors-exploit-cve-2022-47966-and-cve-2022-42475_1.pdf"
    "https://www.cisa.gov/sites/default/files/2023-03/aa23-074a-threat-actors-exploit-telerik-vulnerability-in-us-government-iis-server_1.pdf"
    "https://www.cisa.gov/sites/default/files/2023-05/aa23-131a_joint_csa_malicious_actors_exploit_cve-2023-27350_in_papercut_mf_and_ng_3.pdf"
    "https://www.cisa.gov/sites/default/files/publications/AA22-055A_Iranian_Government-Sponsored_Actors_Conduct_Cyber_Operations.pdf"
    "https://www.cisa.gov/sites/default/files/publications/AA22-138A-Threat_Actors_Exploiting_F5_BIG-IP_CVE-2022-1388_F5.pdf"
    "https://www.cisa.gov/sites/default/files/publications/aa22-228a-threat-actors-exploiting-multiple-cves-against-zimbra.pdf"
    "https://www.cisa.gov/sites/default/files/2023-11/aa23-320a_scattered_spider_0.pdf"
    "https://www.cisa.gov/sites/default/files/2023-11/aa23-325a_lockbit_3.0_ransomware_affiliates_exploit_cve-2023-4966_citrix_bleed_vulnerability_0.pdf"
    "https://www.cisa.gov/sites/default/files/2023-06/aa23-165a_understanding_TA_LockBit.pdf"
    "https://www.cisa.gov/sites/default/files/2023-08/aa23-242a-identification-and-disruption-of-qakbot-infrastructure.pdf"
    "https://www.cisa.gov/sites/default/files/2024-02/aa24-038a-jcsa-prc-state-sponsored-actors-compromise-us-critical-infrastructure_1.pdf"
    "https://www.cisa.gov/sites/default/files/2025-03/Joint-Guidance-Identifying-and-Mitigating-LOTL508.pdf"
)

count=1
total=${#URLS[@]}

echo "🛡️ Starting automated ingestion of $total CTI reports..."

# Loop through the array and download each file using curl
for url in "${URLS[@]}"; do
    # Extract the original filename from the URL
    filename=$(basename "$url")
    
    echo "[$count/$total] Fetching: $filename"
    
    # Download the file silently (-sS) into the data directory
    curl -sS -o "$TARGET_DIR/$filename" "$url"
    
    # Pause for 1 second to prevent the host server from blocking the connection
    sleep 1
    
    ((count++))
done

echo "Success! All PDFs have been staged in $TARGET_DIR."
