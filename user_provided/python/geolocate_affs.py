# geolocate_affs.py
# Date: 2026-02-19
# Objective: Geolocate all affiliations from compiled article list using Nominatim
# Dependencies: requests, json, csv, time, re, unidecode

import json
import csv
import time
import re
import requests
from unidecode import unidecode

def clean_affiliation(aff):
    """
    Remove leading numbers, Unicode control characters, and extra whitespace.
    Lowercase for consistent matching.
    """
    aff = re.sub(r'^[\d\W]+', '', aff)  # remove leading numbers/special chars
    aff = aff.strip()
    return aff

def load_aff_lookup(file_path):
    """
    Load CSV replacement rules.
    Each line: matched_aff;;replacement_aff
    Returns list of tuples: (matched_lower, replacement)
    """
    lookup = []
    try:
        with open(file_path, encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split(';;')
                if len(parts) == 2:
                    matched, replacement = parts
                    lookup.append((matched.lower().strip(), replacement.strip()))
    except FileNotFoundError:
        print(f"Warning: Lookup file {file_path} not found.")
    return lookup

def apply_lookup(aff_cleaned, lookup):
    """
    Apply replacement rules: if any matched_aff substring exists in aff_cleaned,
    return replacement; otherwise return aff_cleaned.
    """
    aff_lower = aff_cleaned.lower()
    for matched, replacement in lookup:
        if matched in aff_lower:
            return replacement
    return aff_cleaned

def query_nominatim(query_str, max_retries=3):
    """
    Query Nominatim with automatic retries.
    Returns dict with lat, lon, country, country_code, display_name if found, else None.
    """
    url = "https://nominatim.openstreetmap.org/search"
    headers = {'User-Agent': 'AffiliationGeolocator/1.0'}
    params = {
        'q': query_str,
        'format': 'json',
        'limit': 1,
        'addressdetails': 1
    }
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                if data:
                    result = data[0]
                    country = result.get('address', {}).get('country', '')
                    country_code = result.get('address', {}).get('country_code', '').upper()
                    return {
                        'lat': result.get('lat'),
                        'lon': result.get('lon'),
                        'country': country,
                        'country_code': country_code,
                        'display_name': result.get('display_name')
                    }
                else:
                    return None
            else:
                print(f"Warning: Nominatim returned status {resp.status_code}")
        except requests.RequestException as e:
            print(f"Warning: Query failed ({e}), retrying...")
        time.sleep(5)
    return None

def geolocate_affs():
    print("Loading compiled affiliations...")
    with open('results/query/compiled_affs.json', encoding='utf-8') as f:
        compiled = json.load(f)

    affs_list = compiled.get('affs', [])
    total_affs = len(affs_list)
    print(f"Total unique affiliations to geolocate: {total_affs}")

    lookup_rules = load_aff_lookup('user_provided/admin/affs_lookup.csv')
    print(f"Loaded {len(lookup_rules)} CSV replacement rules")

    geolocated_affs = []
    countries_count = {}
    not_found = []

    for i, aff in enumerate(affs_list, start=1):
        name_original = aff
        name_cleaned = clean_affiliation(name_original)
        name_queried = apply_lookup(name_cleaned, lookup_rules)

        print(f"[{i}/{total_affs}] Querying Nominatim for: {name_queried}")

        result = query_nominatim(name_queried)
        if result:
            country_ascii = unidecode(result['country'])
            geolocated_affs.append({
                'name_original': name_original,
                'name_cleaned': name_cleaned,
                'name_queried': name_queried,
                'lat': result['lat'],
                'lon': result['lon'],
                'country': result['country'],
                'country_code': result['country_code'],
                'country_English': country_ascii
            })
            countries_count[country_ascii] = countries_count.get(country_ascii, 0) + 1
        else:
            print("→ Not found")
            not_found.append(name_original)

        # Save progress every request to avoid data loss
        with open('results/affs/geolocated_affs.json', 'w', encoding='utf-8') as f:
            json.dump({
                'affs_unique': total_affs,
                'affs_total': total_affs,
                'affs_geolocated': len(geolocated_affs),
                'most_common_missing_affs': not_found[:10],
                'affs': sorted(affs_list),
                'countries': [{'name': k, 'count': v} for k, v in sorted(countries_count.items(), key=lambda x: x[1], reverse=True)],
                'affs_geolocated': geolocated_affs,
                'not_found': not_found
            }, f, ensure_ascii=False, indent=2)

        time.sleep(5)  # Respect Nominatim usage policy

    print("Geolocation complete!")

if __name__ == "__main__":
    geolocate_affs()
