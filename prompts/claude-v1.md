# resurch

Create a CLI tool, written in Rust, called "resurch", whose primary purpose
is to search online repositories of academic papers, and fetch metadata about them,
storing information locally for later analysis.

There will be a variety of subcommands that implement specialized functionality
for the curation, analysis, and presentation of results.

The tool is intended to aggregate results across various online repositories
of research papers, so that scientists trying to understand a new topic can find
relevant research quickly, and identify further reading materials.

## workflow

The tool is responsible for a workflow consisting of the following steps:

  1. identify search terms relevant to the current research topic
  2. find academic papers including those search terms, e.g. "halophile AND halophyte"
  3. store the metadata for those papers within a local sqlite database.
  4. support exporting the results to various formats, like CSV, JSON, or even HTML.

Sometimes long-running operations will be interrupted, so they should be resumeable.

## supported repositories

The tool should understand how to query at least four different online repositories
of publications:

  * Google Scholar
  * CrossRef
  * OpenAlex
  * Semantic Scholar

Some repositories will have more papers than others; multiple should be searched,
to find the most complete picture possible of available research publications.

When querying the remote repositories make sure to support pagination in the responses:
typically the search APIs only return results in batches of 100 or so, meaning that follow-up
requests will be necessary to fetch.

## Data model

### ResurchPaper

The data model for each research paper should be approximately this:

```
// A research paper published in an academic journal or other repository.
struct Paper {
  // The full name of the paper as it was submitted to the journal.
  title: String,
  // The number of times this paper has been cited in other papers.
  citations: u64,
  // The "digital object identifier" for the paper; a uuid.
  //
  // Mostly applies to papers published after 2000 or so, so not all papers will have it.
  // This value can typically be parsed from the contents of the `publisher_url`.
  doi: Option<String>,
  // A URL like "https://doi.org/10.5555/20123118210"
  doi_url: Option<Url>,
  // The calendar year in which the paper was published, e.g. 2001.
  year: u8,
  // The journal or book in which the paper was printed
  publication: String,
  // The summary paragraph for the paper
  abstract: String,
  // An optional excerpt from the paper.
  snippet: Option<String>,
  // A URL to the paper, viewable in a browser.
  publisher_url: Url,
}
```

Make sure that the database is structured such that papers can be updated or enriched
with additional metadata. When in doubt, the DOI field should be used to assign additional metadata.
Remember, the "search" and "enrich" operations are resumable.

### Online repositories

Each online repository should have its own query URL syntax. Structure the code such that
additional online repositories can be added or removed at a later date.

## CLI interface

The "resurch" tool should support the following subcommands.

### search

The "search" subcommand finds papers online, by making network calls to online repositories such as Google Scholar.

* `resurch search <QUERY>` (with alias "surch" for fun) for finding papers online, across the various supported repositories.
* `resurch search --where / -w` for searching only a specific online repository for papers. By default, all available repositories should be searched.
* `resurch search --list / -l` to list previously interrupted searches
* `resurch search --resume / -r` to resume a previously interrupted search
* `resurch search --max-results / -m` to limit the number of results returned

Any articles that it finds should be coerced into a `ResurchPaper` type, and then written to a local sqlite database. The db logic is crucial, because it will allow analysis of metadata like abstract without continually polling online endpoints.

The subcommand should be respectful of remote APIs, and potential ratelimiting. If an HTTP 429 response is encountered, log a warning. Add a CLI flag like "--sleep-time" that accepts a time value such as "5s" to instruct the fetch logic to wait five seconds between network calls. Set it to "2s" by default.

Also, support parallel fetching, via a flag like "--num-parallel". Set it to 1 by default. Make sure that the ratelimit sleep logic interacts
well with the parallel logic: if "--num-parallel" is set to 5, then five requests should be made simultaneously, after which a sleep of 2s
should be made, then another batch of 5 fetched, etc.

The default path for the database should be `~/.local/share/resurch/resurch.sqlite`, which is
overrideable via a CLI flag such as "-d / --database".

### enrich

The "enrich" subcommand takes raw research results within the local db, and tries to canonicalize their representation.
For example, it'll try to add DOI numbers to papers where that information can be inferred.

* `resurch enrich` inspects the local database and tries to flesh out the metadata on each paper
* `resurch enrich --download` will also try to download a PDF version of the fullpaper, if available. off by default

The reason this subcommand is implemented separately from "search" is because it too involves a lot of network calls,
and generally the "enrich" process takes a lot longer than the "search" process, because each paper needs to be checked.
Therefore, the "enrich" subcommand should also accept ratelimiting-aware flags such as `--sleep-time`
and `--num-parallel`, mentioned above.

Similarly, it would be great if the enrichment process is resumable, and therefore completable in batches.

### query

The "query" subcommand searches the local sqlite3 database. It should have pretty-printing.
It can take a CLI flag like "--read-my-mind" to be forgiving about query about syntax,
to aid scientists in searching the db without a ton of SQL knowledge. By default, though, it should be 
strict about SQL formatting of queries.

* `research query [--database / -d] <QUERY>` search the local 

### export

The "export" subcommand reads the local sqlite3 database and saves reports in non-sqlite3 format, suitable
for sharing with colleagues.

* `resurch export [--database / -d] [--query <QUERY>] -o <csv|json|pdf>`
* `resurch export [--database / -d] [--doi <DOI>] -o <csv|json>`

If `resurch export` is run without "--query" or "--doi" flags, then it should export the entire database.

### website

The "website" subcommand reads the local sqlite3 database and creates a static website docroot that
can be served for sharing analysis with colleagues.

* `research website [--database / -d] [-o / --output <OUTPUT_DIR>]`

Create convenient aliases for this subcommand, such as "ssg", "generate", and "docroot".

The HTML on the static site should be organized into an interactive table, using JavaScript dependencies.
Generate the necessary assets, such as "index.html" plus "css" and "js" subdirectories.

### stats

The "status" subcommand displays a summary of the contents already within the local database.
It should include metrics like number of papers per online repository, as well as recent
queries that have been run. Give it a few helpful aliases, like "status" and "metrics".

## Usability

It's important that the user be able to interrupt and resume long search batches.
Try to be respectful of server administrators, and don't hammer on endpoints repeatedly:
rather, a long-running search should be interruptable, and then resumable later.
This is also true of the "enrich" process.

This probably means that searches and queries should have an intermediate representation in the database.
The user need not know that, but doing so would enable resumable operations, which is very helpful.

Accordingly, seek to utilize pre-existing free software dependencies to provide a pleasant UX,
including progress bars where appropriate. By default, assume that a progress bar should be displayed
on a long-running task, unless a different "--output" format is requested.

## Pre-existing work

There is a prior version of the searching and enriching logic in @user_provided/python/. Please review that logic for additional context,
but don't edit that code directly. Instead, create your own project within a new subdir, so that I can compare the functionality
of the two implementations manually.

There is also an example docroot of a previously generated static site in @docs/. Use that for inspiration when designing the "website"
subcommand.

Finally, there are some example cleaned up search results in JSON format at @results/search_results/standardized/gscholar.json. Review those
to understand how research papers were represented in the prior work.
