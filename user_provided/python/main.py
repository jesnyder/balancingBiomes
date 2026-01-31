from search_gscholar import search_gscholar
from standardize_gscholar import standardize_gscholar


def main():
    print("main running")

    tasks = [1,2]


    if 1 in tasks: search_gscholar()
    if 2 in tasks: standardize_gscholar()




if __name__ == "__main__":
    main()
