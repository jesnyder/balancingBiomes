
/*
TABLE: Article Types
*/

const types = [
  {
    "type": "journal-article",
    "count": 1969
  },
  {
    "type": "book-chapter",
    "count": 127
  },
  {
    "type": "posted-content",
    "count": 61
  },
  {
    "type": "component",
    "count": 25
  },
  {
    "type": "proceedings-article",
    "count": 14
  },
  {
    "type": "grant",
    "count": 13
  },
  {
    "type": "peer-review",
    "count": 13
  },
  {
    "type": "dataset",
    "count": 6
  },
  {
    "type": "dissertation",
    "count": 5
  },
  {
    "type": "other",
    "count": 3
  },
  {
    "type": "book",
    "count": 2
  },
  {
    "type": "reference-entry",
    "count": 2
  },
  {
    "type": "report",
    "count": 1
  }
];

const tableTypes = new Tabulator("#tableOfTypes", {
  data: types,
  layout: "fitColumns",
  pagination: true,
  paginationSize: 20,
  initialSort: [{column: "count", dir: "desc"}],
  columns: [
    {title: "Type", field: "type", headerFilter: "input"},
    {title: "Count", field: "count", sorter: "number"}
  ]
});
