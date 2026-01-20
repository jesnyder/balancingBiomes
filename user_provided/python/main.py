from search_gscholar import search_gscholar
from search_semanticscholar import search_semanticscholar
from search_openalex import search_openalex
from search_crossref import search_crossref
from compile_searches import compile_searches
#from build_js_table import build_js_table
from count_species import count_species
from detail_species import detail_species
from build_table_summary import build_table_summary
from add_crossref_to_gscholar import add_crossref_to_gscholar
from plot_gscholar import plot_gscholar

def main():
    print("main running")

    tasks = [2]

    # detail species
    if 1 in tasks: detail_species()

    # search gscholar https://scholar.google.com/
    # compile results
    # enrich the results with crossref
    if 2 in tasks:
        #search_gscholar()
        #add_crossref_to_gscholar()
        plot_gscholar()

    # search semantic scholar https://www.semanticscholar.org/
    if 3 in tasks: search_semanticscholar()
    # search open alex https://openalex.org/
    if 4 in tasks: search_openalex()
    # search Crossref https://www.crossref.org/
    if 5 in tasks: search_crossref()

    # compile and summarize searches
    if 6 in tasks: compile_searches()
    if 7 in tasks: build_table_summary()

    # build javasript elements
    if 8 in tasks: build_js_table()

    # count species and build js table
    if 9 in tasks: count_species()



if __name__ == "__main__":
    main()
