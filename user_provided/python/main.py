
from search_crossref import search_crossref
from search_gscholar import search_gscholar

from enrich_gscholar import enrich_gscholar

def main():
    print("main running")

    tasks = [3]

    if 1 in tasks: search_crossref()
    if 2 in tasks: search_gscholar()
    if 3 in tasks: enrich_gscholar()



if __name__ == "__main__":
    main()
