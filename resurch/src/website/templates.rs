//! HTML and JS templates for website

use super::WebsiteConfig;
use anyhow::{Context, Result};
use std::fs;
use std::path::Path;

/// Generate index.html
pub fn generate_index_html(config: &WebsiteConfig, output: &Path) -> Result<()> {
    let html = format!(
        r##"<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://unpkg.com/tabulator-tables@5.5.0/dist/css/tabulator.min.css" rel="stylesheet">
    <script src="https://cdn.plot.ly/plotly-2.29.1.min.js"></script>
    <style>
        body {{
            font-family: Arial, sans-serif;
            background-color: #f6f8fa;
            margin: 40px;
            color: #222;
        }}
        h1 {{
            color: #2c5aa0;
        }}
        p {{
            line-height: 1.6;
            max-width: 700px;
        }}
        .box {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #2c5aa0;
        }}
        .stat-label {{
            color: #666;
        }}
        #papers-table {{
            margin-top: 20px;
        }}
        .chart-container {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }}
        .chart {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        }}
        button {{
            background: #2c5aa0;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin-right: 10px;
        }}
        button:hover {{
            background: #1e4080;
        }}
    </style>
</head>
<body>
    <div class="box">
        <h1>{title}</h1>
        <p>Academic paper database with search results from multiple repositories.</p>
    </div>

    <div class="stats-grid" id="stats-grid">
        <!-- Stats loaded by JavaScript -->
    </div>

    <div class="box">
        <h2>Papers (2+ citations)</h2>
        <button id="download-csv">Download CSV</button>
        <button id="download-json">Download JSON</button>
        <div id="papers-table"></div>
    </div>

    <div class="chart-container">
        <div class="chart" id="year-chart"></div>
        <div class="chart" id="source-chart"></div>
    </div>

    <script src="https://unpkg.com/tabulator-tables@5.5.0/dist/js/tabulator.min.js"></script>
    <script src="js/table.js"></script>
    <script src="js/charts.js"></script>
</body>
</html>
"##,
        title = config.title
    );

    fs::write(output, html).context("Failed to write index.html")?;
    Ok(())
}

/// Generate table.js for Tabulator
pub fn generate_table_js(output: &Path) -> Result<()> {
    // Using include_str! would be cleaner, but for now we'll build it manually
    let js = r##"// Load and display papers table
fetch('data/papers.json')
    .then(response => response.json())
    .then(papers => {
        const table = new Tabulator("#papers-table", {
            data: papers,
            layout: "fitColumns",
            pagination: "local",
            paginationSize: 25,
            paginationSizeSelector: [10, 25, 50, 100],
            columns: [
                {
                    title: "Title",
                    field: "title",
                    headerFilter: "input",
                    formatter: function(cell) {
                        const paper = cell.getData();
                        const url = paper.doi_url || paper.publisher_url || '#';
                        return '<a href="' + url + '" target="_blank">' + cell.getValue() + '</a>';
                    },
                    widthGrow: 3
                },
                {
                    title: "Year",
                    field: "year",
                    headerFilter: "input",
                    width: 80
                },
                {
                    title: "Citations",
                    field: "citations",
                    headerFilter: "number",
                    headerFilterFunc: ">=",
                    sorter: "number",
                    width: 100
                },
                {
                    title: "DOI",
                    field: "doi",
                    headerFilter: "input",
                    formatter: function(cell) {
                        const doi = cell.getValue();
                        if (doi) {
                            return '<a href="https://doi.org/' + doi + '" target="_blank">' + doi + '</a>';
                        }
                        return "";
                    },
                    widthGrow: 1
                },
                {
                    title: "Source",
                    field: "source_repository",
                    headerFilter: "select",
                    headerFilterParams: {values: true},
                    width: 120
                }
            ],
            initialSort: [
                {column: "citations", dir: "desc"}
            ]
        });

        // Download handlers
        document.getElementById('download-csv').addEventListener('click', () => {
            table.download("csv", "papers.csv");
        });

        document.getElementById('download-json').addEventListener('click', () => {
            table.download("json", "papers.json");
        });
    });

// Load and display stats
fetch('data/stats.json')
    .then(response => response.json())
    .then(stats => {
        const statsGrid = document.getElementById('stats-grid');
        statsGrid.innerHTML =
            '<div class="stat-card">' +
                '<div class="stat-value">' + stats.total_papers + '</div>' +
                '<div class="stat-label">Total Papers</div>' +
            '</div>' +
            '<div class="stat-card">' +
                '<div class="stat-value">' + stats.papers_with_doi + '</div>' +
                '<div class="stat-label">With DOI</div>' +
            '</div>' +
            '<div class="stat-card">' +
                '<div class="stat-value">' + stats.papers_with_abstract + '</div>' +
                '<div class="stat-label">With Abstract</div>' +
            '</div>' +
            '<div class="stat-card">' +
                '<div class="stat-value">' + stats.papers_with_2_citations + '</div>' +
                '<div class="stat-label">2+ Citations</div>' +
            '</div>';
    });
"##;

    fs::write(output, js).context("Failed to write table.js")?;
    Ok(())
}

/// Generate charts.js for Plotly visualizations
pub fn generate_charts_js(output: &Path) -> Result<()> {
    let js = r##"// Load and display charts
fetch('data/stats.json')
    .then(response => response.json())
    .then(stats => {
        // Papers by Year chart
        const years = stats.by_year.map(function(item) { return item[0]; });
        const yearCounts = stats.by_year.map(function(item) { return item[1]; });

        Plotly.newPlot('year-chart', [{
            x: years,
            y: yearCounts,
            type: 'bar',
            marker: { color: '#2c5aa0' }
        }], {
            title: 'Papers by Year',
            xaxis: { title: 'Year' },
            yaxis: { title: 'Number of Papers' },
            margin: { t: 40, b: 40 }
        }, { responsive: true });

        // Papers by Source chart
        const sources = Object.keys(stats.by_source);
        const sourceCounts = Object.values(stats.by_source);

        Plotly.newPlot('source-chart', [{
            labels: sources,
            values: sourceCounts,
            type: 'pie',
            marker: {
                colors: ['#2c5aa0', '#4a7dc0', '#6b9cd0', '#8cbce0']
            }
        }], {
            title: 'Papers by Source',
            margin: { t: 40, b: 40 }
        }, { responsive: true });
    });
"##;

    fs::write(output, js).context("Failed to write charts.js")?;
    Ok(())
}
