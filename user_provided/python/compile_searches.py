import json
import csv
from pathlib import Path
from collections import defaultdict

def compile_searches():
    """
    Compile search results from multiple database JSON files,
    deduplicate entries, add citation counts, save compiled results,
    and produce a search summary.
    """

    # -------------------------------
    # Paths
    # -------------------------------
    search_results_dir = Path("results/search_results")
    search_results_dir.mkdir(parents=True, exist_ok=True)

    # Assume all JSON files in the folder are individual database results
    database_files = list(search_results_dir.glob("*.json"))

    if not database_files:
        print("No JSON database files found in results/search_results")
        return

    compiled_dict = {}  # key: unique identifier (doi or url or title lower)
    database_summary = {}

    # -------------------------------
    # Helper function to get unique key
    # -------------------------------
    def get_unique_key(article):
        if "doi" in article and article["doi"]:
            return article["doi"].lower()
        if "url" in article and article["url"]:
            return article["url"].lower()
        if "title" in article and article["title"]:
            return article["title"].strip().lower()
        return None

    # -------------------------------
    # Read each database JSON
    # -------------------------------
    for db_file in database_files:
        db_name = db_file.stem  # use file name as database name
        with open(db_file, "r", encoding="utf-8") as f:
            try:
                articles = json.load(f)
            except Exception as e:
                print(f"Error reading {db_file}: {e}")
                continue

        if not isinstance(articles, list):
            print(f"{db_file} is not a list, skipping")
            continue

        database_summary[db_name] = {
            "count": len(articles),
            "fields": list(articles[0].keys()) if articles else [],
            "articles": articles
        }

        for article in articles:
            # Add cited_by if is_referenced_by_count exists
            if "is_referenced_by_count" in article:
                article["cited_by"] = article["is_referenced_by_count"]

            # Record which databases this article came from
            article_key = get_unique_key(article)
            if not article_key:
                continue

            if article_key in compiled_dict:
                # Merge metadata
                existing = compiled_dict[article_key]

                # Combine databases
                existing["databases"] = list(set(existing.get("databases", []) + [db_name]))

                # Merge fields - keep existing values, add new if not present
                for k, v in article.items():
                    if k not in existing or not existing[k]:
                        existing[k] = v
            else:
                # First occurrence
                article["databases"] = [db_name]
                compiled_dict[article_key] = article

    compiled_list = list(compiled_dict.values())

    # -------------------------------
    # Sort compiled list by citations descending
    # -------------------------------
    def citation_sort_key(article):
        return int(article.get("cited_by", 0) or 0)

    compiled_list.sort(key=citation_sort_key, reverse=True)

    # -------------------------------
    # Save list_compiled.json
    # -------------------------------
    json_path = search_results_dir / "list_compiled.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(compiled_list, f, indent=4, ensure_ascii=False)
    print(f"Saved compiled JSON: {json_path}")

    # -------------------------------
    # Save list_compiled.csv
    # -------------------------------
    # Determine all possible fields dynamically
    all_fields = set()
    for art in compiled_list:
        all_fields.update(art.keys())
    all_fields = sorted(all_fields)

    csv_path = search_results_dir / "list_compiled.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=all_fields)
        writer.writeheader()
        for art in compiled_list:
            writer.writerow({k: art.get(k, "") for k in all_fields})
    print(f"Saved compiled CSV: {csv_path}")

    # -------------------------------
    # Build search_summary.csv
    # -------------------------------
    summary_path = search_results_dir / "search_summary.csv"
    with open(summary_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Header
        header = ["Database", "Total Articles", "Fields Captured"]
        db_names = list(database_summary.keys())
        for db in db_names:
            header.append(f"Articles Also in {db}")
        writer.writerow(header)

        # Rows
        for db_name, info in database_summary.items():
            row = [
                db_name,
                len(info["articles"]),
                "; ".join(info["fields"]) if info["fields"] else "0"
            ]
            for compare_db in db_names:
                if compare_db == db_name:
                    # All articles are also in the same db
                    count = len(info["articles"])
                else:
                    # Count articles also found in compare_db
                    compare_keys = set()
                    for a in database_summary[compare_db]["articles"]:
                        key = get_unique_key(a)
                        if key:
                            compare_keys.add(key)

                    count = 0
                    for a in info["articles"]:
                        key = get_unique_key(a)
                        if key and key in compare_keys:
                            count += 1
                row.append(count)
            writer.writerow(row)
    print(f"Saved search summary CSV: {summary_path}")


if __name__ == "__main__":
    compile_searches()
