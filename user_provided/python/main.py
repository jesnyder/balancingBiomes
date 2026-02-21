from query_gscholar import query_gscholar
from doi_gscholar import doi_gscholar
from crossref_gscholar import crossref_gscholar
from openalex_gscholar import openalex_gscholar

from doi_crossref import doi_crossref
from query_crossref import query_crossref
from compile_crossref import compile_crossref
from openalex_crossref import openalex_crossref

from combine_articles import combine_articles
from list_affs import list_affs
from geolocate_affs import geolocate_affs

def main():
    print("main running")

    tasks = [7, 9, 10, 11]


    if 1 in tasks: query_gscholar()
    if 2 in tasks: doi_gscholar()
    if 3 in tasks: crossref_gscholar()
    if 4 in tasks: openalex_gscholar()

    if 5 in tasks: doi_crossref()
    if 6 in tasks: query_crossref()
    if 7 in tasks: compile_crossref()
    if 8 in tasks: openalex_crossref()

    if 9 in tasks: combine_articles()
    if 10 in tasks: list_affs()
    if 11 in tasks: geolocate_affs()


    # list_affs
    # geolocate_affs
    # geolocate_articles
    # map_articles
    # table_articles
    # query_gbif
    # count_organisms
    # map_high_counts





if __name__ == "__main__":
    main()
