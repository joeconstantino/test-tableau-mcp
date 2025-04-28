in_context_samples = [
  {
    "fields": [
      { "fieldCaption": "Segment" },
      { "fieldCaption": "Sales", "function": "SUM" }
    ]
  },
  {
    "fields": [
      { "fieldCaption": "Category" },
      { "fieldCaption": "Profit", "function": "SUM", "sortDirection": "DESC" }
    ]
  },
  {
    "fields": [
      { "fieldCaption": "State/Province" },
      { "fieldCaption": "Sales", "function": "SUM", "sortDirection": "DESC" }
    ],
    "filters": [
      {
        "field": { "fieldCaption": "Segment" },
        "filterType": "SET",
        "values": ["Consumer"],
        "exclude": false
      },
      {
        "field": { "fieldCaption": "Order Date" },
        "filterType": "RANGE",
        "min": "2021-01-01",
        "max": "2021-12-31"
      }
    ],
    "limit": 5
  }
]