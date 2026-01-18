import os
import json
import csv
from collections import defaultdict

RESULTS_DIR = "results/search_results"

LIST_FILES = {
    "Google Scholar": os.path.join(RESULTS_DIR, "list_gscholar.json"),
    "Semantic Scholar": os.path.join(RESULTS_DIR, "list_semanticscholar.json"),
    "OpenAlex": os.path.join(RESULTS_DIR, "list_openalex.json"),
    "CrossRef": os.path.join(RESULTS_DIR, "list_crossref.json")
}

COMPILED_JSON = os.path.join(RESULTS_DIR, "list_compiled.json")
COMPILED_CSV = os.path.join(RESULTS_DIR, "list_compiled.csv")
SUMMARY_CSV = os.path.join(RESULTS_DIR, "search_summary.csv")


def compile_searches():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    # Step 1: load all individual database results
    db_entries = {}  # database -> list of entries
    for db_name, path in LIST_FILES.items():
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            db_entries[db_name] = []
            print(f"{db_name}: No results found.")
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                db_entries[db_name] = json.load(f)
            print(f"{db_name}: Loaded {len(db_entries[db_name])} entries.")
        except json.JSONDecodeError:
            db_entries[db_name] = []
            print(f"{db_name}: Invalid JSON, skipping.")

    # Step 2: build master list, combine duplicates, track databases
    master_dict = {}  # key -> entry, key is doi/url/title
    for db_name, entries in db_entries.items():
        for entry in entries:
            key = entry.get("doi") or entry.get("url") or entry.get("title")
            if key in master_dict:
                # merge metadata: update missing fields
                for k, v in entry.items():
                    if k not in master_dict[key] or not master_dict[key][k]:
                        master_dict[key][k] = v
                # update databases found in
                master_dict[key]["databases_found_in"].add(db_name)
            else:
                entry["databases_found_in"] = {db_name}
                master_dict[key] = entry

    # Convert set to sorted list for CSV/JSON
    master_list = []
    for entry in master_dict.values():
        entry_copy = entry.copy()
        entry_copy["databases_found_in"] = sorted(list(entry_copy["databases_found_in"]))
        master_list.append(entry_copy)

    # Step 3: Save compiled list JSON
    with open(COMPILED_JSON, "w", encoding="utf-8") as f:
        json.dump(master_list, f, indent=2, ensure_ascii=False)

    # Step 4: Save compiled list CSV
    if master_list:
        fieldnames = sorted({k for entry in master_list for k in entry.keys()})
        with open(COMPILED_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(master_list)

    # Step 5: Prepare search summary
    summary_rows = []
    for db_name in LIST_FILES.keys():
        entries = db_entries.get(db_name, [])
        if not entries:
            summary_rows.append([db_name, 0, "N/A"] + [0]*len(LIST_FILES))
            continue

        fields = set()
        for e in entries:
            fields.update(e.keys())

        # Compute overlaps with all databases
        overlaps = []
        for other_db, other_entries in db_entries.items():
            if not other_entries:
                overlaps.append(0)
                continue
            count = 0
            other_keys = set(
                e.get("doi") or e.get("url") or e.get("title") for e in other_entries
            )
            for e in entries:
                key = e.get("doi") or e.get("url") or e.get("title")
                if key in other_keys:
                    count += 1
            overlaps.append(count)

        summary_rows.append([db_name, len(entries), ", ".join(sorted(fields))] + overlaps)

    # Save summary CSV
    header = ["Database", "Number of Results", "Fields Captured"] + list(LIST_FILES.keys())
    with open(SUMMARY_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(summary_rows)

    print(f"\nCompiled list saved: {COMPILED_JSON}, {COMPILED_CSV}")
    print(f"Search summary saved: {SUMMARY_CSV}")


if __name__ == "__main__":
    compile_searches()
