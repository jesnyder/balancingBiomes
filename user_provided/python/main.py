from search_gscholar import search_gscholar
from search_semanticscholar import search_semanticscholar
from search_openalex import search_openalex
from search_crossref import search_crossref
from compile_searches import compile_searches
from build_js_table import build_js_table
from count_species import count_species
from detail_species import detail_species

def main():
    print("main running")

    tasks = [1,8]

    # detail species
    if 1 in tasks: detail_species()

    # search gscholar and compile results https://scholar.google.com/
    if 2 in tasks: search_gscholar()
    # search semantic scholar https://www.semanticscholar.org/
    if 3 in tasks: search_semanticscholar()
    # search open alex https://openalex.org/
    if 4 in tasks: search_openalex()
    # search Crossref https://www.crossref.org/
    if 5 in tasks: search_crossref()

    # compile and summarize searches
    if 6 in tasks: compile_searches()

    # build javasript elements
    if 7 in tasks: build_js_table()

    # count species and build js table
    if 8 in tasks: count_species()



if __name__ == "__main__":
    main()
