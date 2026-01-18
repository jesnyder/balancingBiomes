import csv
import json
import time
import requests
from pathlib import Path

# -----------------------------
# CONFIGURATION
# -----------------------------
SPECIES_FILE = Path("user_provided/species_list.csv")
OUTPUT_DIR = Path("results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

JSON_PATH = OUTPUT_DIR / "species_detailed.json"
CSV_PATH = OUTPUT_DIR / "species_detailed.csv"

GBIF_API = "https://api.gbif.org/v1/species/match"
NCBI_API = "https://api.ncbi.nlm.nih.gov/taxonomy/v0/taxon/name/{}"

HEADERS = {"User-Agent": "species-detailer/1.0"}

# -----------------------------
# UTILITIES
# -----------------------------

def load_species():
    with open(SPECIES_FILE, newline="", encoding="utf-8") as f:
        species = [row[0].strip() for row in csv.reader(f) if row]
    return sorted(set(species))


def query_gbif(name):
    try:
        r = requests.get(
            GBIF_API,
            params={"name": name},
            headers=HEADERS,
            timeout=20
        )
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def query_ncbi(name):
    try:
        url = NCBI_API.format(name.replace(" ", "%20"))
        r = requests.get(url, headers=HEADERS, timeout=20)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


def classify_organism(gbif_data):
    if not gbif_data:
        return "unknown"

    kingdom = str(gbif_data.get("kingdom", "")).lower()

    if "plantae" in kingdom:
        return "plant"
    if "bacteria" in kingdom:
        return "bacteria"
    if "archaea" in kingdom:
        return "archaea"
    if "animalia" in kingdom:
        return "animal"

    return "unknown"


def infer_halotolerance(gbif_data, ncbi_data):
    keywords = ["halo", "salt", "saline", "halophile"]

    for source in (gbif_data, ncbi_data):
        if not source:
            continue
        text = json.dumps(source).lower()
        if any(k in text for k in keywords):
            return "yes"

    return "no"


def save_outputs(records):
    # JSON (full structure)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    # CSV (summary)
    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "species",
            "classification",
            "halotolerant",
            "url"
        ])

        for r in records:
            writer.writerow([
                r["species"],
                r["classification"],
                r["halotolerant"],
                r.get("url", "")
            ])


# -----------------------------
# MAIN FUNCTION
# -----------------------------

def detail_species():
    species_list = load_species()
    print(f"Loaded {len(species_list)} unique species")

    results = []

    for i, species in enumerate(species_list, 1):
        print(f"[{i}/{len(species_list)}] Processing: {species}")

        gbif = query_gbif(species)
        ncbi = query_ncbi(species)

        classification = classify_organism(gbif)
        halotolerant = infer_halotolerance(gbif, ncbi)

        url = None
        if gbif and gbif.get("usageKey"):
            url = f"https://www.gbif.org/species/{gbif['usageKey']}"

        record = {
            "species": species,
            "classification": classification,
            "halotolerant": halotolerant,
            "url": url,
            "gbif": gbif,
            "ncbi": ncbi
        }

        results.append(record)

        # Save after each species
        save_outputs(results)

        time.sleep(0.3)  # API-friendly pacing

    print("✅ Species detailing complete.")


if __name__ == "__main__":
    detail_species()
