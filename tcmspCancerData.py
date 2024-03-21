import json
import random
import re
import time

import requests
import pandas as pd


def callTCMPSGetResponse(index):
    url = 'https://tcmsp-e.com/molecule.php?qn=' + str(index)
    print(url)
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': '_ga=GA1.1.1764850825.1706031870; PHPSESSID=c0k3djb1bl7kd552abfvt63ed5; Hm_lvt_045f99afbec668d057769af796f1ed4f=1706031872,1708215866; PHPTCM=c0k3djb1bl7kd552abfvt63ed5; _ga_Y7GC5FHYTY=GS1.1.1708273290.3.1.1708274280.60.0.0; Hm_lpvt_045f99afbec668d057769af796f1ed4f=1708274282',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }
    return requests.get(url, headers=headers)


def checkAndGetCancerDiseases(response):
    pattern = re.compile(r'var dis = \[.*?\];', re.DOTALL)
    match = pattern.search(response.text)
    if match:
        js_variable_content = match.group(0)

        # Extract the JavaScript variable content
        js_variable_content = re.search(r'var dis = (\[.*?\]);', js_variable_content).group(1)

        # Load the JSON data
        disease_data = json.loads(js_variable_content)

        # Extract and print disease names containing "cancer"
        cancer_diseases = [entry['disease_name'] for entry in disease_data if 'cancer' in entry['disease_name'].lower()]

        return cancer_diseases


def hasMoleculeHaveCancerDiseaso(cancer_disease):
    return len(cancer_diseases) > 0


def getMoleculeId(html_content):
    # Define patterns to extract data
    molecule_id_pattern = r'<th class="left_header">Molecule ID</th>\s*<td style="background-color:#f6fcff">(.*?)</td>'

    # Extract Molecule ID
    molecule_id_match = re.search(molecule_id_pattern, html_content)
    molecule_id = molecule_id_match.group(1) if molecule_id_match else None

    # Print the results
    print("Molecule ID:", molecule_id)
    return molecule_id


def getMoleculeName(html_content):
    molecule_name_pattern = r'<th class="left_header">Molecule name</th>\s*<td>(.*?)</td>'

    # Extract Molecule name
    molecule_name_match = re.search(molecule_name_pattern, html_content)
    molecule_name = molecule_name_match.group(1) if molecule_name_match else None

    print("Molecule Name:", molecule_name)
    return molecule_name


def getPubchemCid(html_content):
    pubchem_cid_pattern = r'<th class="left_header">Pubchem Cid</th>\s*<td><a href="http://pubchem.ncbi.nlm.nih.gov/summary/summary.cgi\?cid=(\d+)">'

    # Extract Pubchem Cid
    pubchem_cid_match = re.search(pubchem_cid_pattern, html_content)
    pubchem_cid = pubchem_cid_match.group(1) if pubchem_cid_match else None

    print("Pubchem Cid:", pubchem_cid)
    return pubchem_cid


def getTarget(html_content):
    pattern = re.compile(r'var tar = \[.*?\];', re.DOTALL)
    match = pattern.search(html_content)
    if match:
        js_variable_content = match.group(0)
        # Extract the JavaScript variable content
        js_variable_content = re.search(r'var tar = (\[.*?\]);', js_variable_content).group(1)

        # Load the JSON data
        target_data = json.loads(js_variable_content)

        # Extract target names
        target_names = [entry['target_name'] for entry in target_data]
        return target_names


def getEntry(molecule_id, molecule_name, cid, target, diseases):
    return {
        "molecule_id": molecule_id,
        "molecule_name": molecule_name,
        "cid": cid,
        "related_target": '\r\n'.join(target),
        "cancers": '\r\n'.join(diseases)
    }


excel_file_path = 'output1.xlsx'

for i in range(7180,13720):
    response = callTCMPSGetResponse(i)
    cancer_diseases = checkAndGetCancerDiseases(response)
    print(cancer_diseases)
    if cancer_diseases:
        molecule_id = getMoleculeId(response.text)
        print(molecule_id)
        molecule_name = getMoleculeName(response.text)
        cid = getPubchemCid(response.text)
        target = getTarget(response.text)
        df = pd.DataFrame([getEntry(molecule_id, molecule_name, cid, target, cancer_diseases)])

        # Check if the Excel file already exists
        try:
            existing_df = pd.read_excel(excel_file_path)
            print("Type of existing_df:", type(existing_df))

            # Concatenate the existing DataFrame with the new DataFrame
            existing_df = pd.concat([existing_df, df], ignore_index=True)

            # Print the types after concatenation
            print("Type of existing_df after concatenation:", type(existing_df))
            print("Type of df:", type(df))
        except FileNotFoundError:
            # If the file doesn't exist, create a new DataFrame
            existing_df = df

        # Write the DataFrame to an Excel file
        existing_df.to_excel(excel_file_path, index=False)
        print(f'Data written to {excel_file_path}')
        # Random sleep between 0 and 60 seconds
        sleep_duration = random.randint(0, 10)
        print(f"Sleeping for {sleep_duration} seconds...")
        time.sleep(sleep_duration)