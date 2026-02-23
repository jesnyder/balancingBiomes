// Auto-generated tableAffsCountryCode.js
// Date: 2026-02-23
// Table of unique affiliation country codes with counts
// Table is searchable, sortable, highest count at the top

const AffsCountryCodeData = [
  {
    "country_code": "CN",
    "country_name": "Zhong Guo",
    "count": 19
  },
  {
    "country_code": "US",
    "country_name": "United States",
    "count": 9
  },
  {
    "country_code": "ES",
    "country_name": "Espana",
    "count": 7
  },
  {
    "country_code": "IN",
    "country_name": "India",
    "count": 6
  },
  {
    "country_code": "PT",
    "country_name": "Portugal",
    "count": 4
  },
  {
    "country_code": "DE",
    "country_name": "Deutschland",
    "count": 3
  },
  {
    "country_code": "DK",
    "country_name": "Danmark",
    "count": 3
  },
  {
    "country_code": "KR",
    "country_name": "daehanmingug",
    "count": 3
  },
  {
    "country_code": "GB",
    "country_name": "United Kingdom",
    "count": 2
  },
  {
    "country_code": "TN",
    "country_name": "twns",
    "count": 2
  },
  {
    "country_code": "GR",
    "country_name": "Ellas",
    "count": 1
  },
  {
    "country_code": "TW",
    "country_name": "Tai Wan",
    "count": 1
  },
  {
    "country_code": "DZ",
    "country_name": "Algerie  ljzy'r",
    "count": 1
  }
];

document.addEventListener('DOMContentLoaded', function() {
  // Create container div
  const AffsCountryCodeDiv = document.createElement('div');
  AffsCountryCodeDiv.id = 'AffsCountryCodeDiv';
  AffsCountryCodeDiv.style.marginBottom = '50px';
  document.body.appendChild(AffsCountryCodeDiv);

  // Create title
  const titleAffsCountryCode = document.createElement('h2');
  titleAffsCountryCode.textContent = 'Affiliation Country Codes Table';
  AffsCountryCodeDiv.appendChild(titleAffsCountryCode);

  // Create download button
  const downloadBtnAffsCountryCode = document.createElement('button');
  downloadBtnAffsCountryCode.textContent = 'Download Table Data';
  downloadBtnAffsCountryCode.style.marginBottom = '10px';
  downloadBtnAffsCountryCode.onclick = function() {
    AffsCountryCodeTable.download('csv', 'affiliation_country_codes.csv');
  };
  AffsCountryCodeDiv.appendChild(downloadBtnAffsCountryCode);

  // Create table div
  const tableDivAffsCountryCode = document.createElement('div');
  tableDivAffsCountryCode.id = 'AffsCountryCodeTableDiv';
  AffsCountryCodeDiv.appendChild(tableDivAffsCountryCode);

  // Initialize Tabulator table
  const AffsCountryCodeTable = new Tabulator('#AffsCountryCodeTableDiv', {
    data: AffsCountryCodeData,
    layout: 'fitColumns',
    pagination: 'local',
    paginationSize: 20,
    initialSort: [{column:'count', dir:'desc'}], // sort by count descending
    columns: [
      { title: 'Country Code', field: 'country_code', sorter: 'string', headerFilter: 'input' },
      { title: 'Country Name', field: 'country_name', sorter: 'string', headerFilter: 'input' },
      { title: 'Count', field: 'count', sorter: 'number', headerFilter: 'input' }
    ]
  });
}); // end DOMContentLoaded
