"""Canonical test problems used across the test suite and demo script."""

LOGISTICS_INVOICE = {
    "business_problem": (
        "Our logistics company processes 3000 invoices per month manually. Each invoice "
        "requires a clerk to open a PDF, read line items, match them against purchase orders "
        "in our ERP, and flag discrepancies. This takes 2 full-time employees and has a 4% "
        "error rate causing payment delays and vendor complaints."
    ),
    "company_context": "ERP: SAP S/4HANA. Invoice formats: PDF, mixed structured and scanned.",
    "industry": "Logistics",
}

HR_KNOWLEDGE_BASE = {
    "business_problem": (
        "Our HR department receives 200+ employee questions per week via email about policies, "
        "benefits, and leave procedures. HR business partners spend 60% of their time answering "
        "repetitive questions already documented in our 500-page employee handbook. New hires "
        "especially struggle to find information quickly."
    ),
    "company_context": "Handbook lives in SharePoint, updated quarterly. Team size: 4 HR BPs.",
    "industry": "Human Resources",
}

FINANCE_FORECASTING = {
    "business_problem": (
        "Our FP&A team produces monthly cash flow forecasts manually in Excel. The process "
        "takes 3 analysts 5 days each month, pulls data from 6 source systems, and produces "
        "forecasts that are consistently 15-20% off actuals. The CFO wants weekly forecasts "
        "but the team cannot increase cadence with the current process."
    ),
    "company_context": "3 years of historical transaction data. External signals: customer payment terms.",
    "industry": "Finance",
}
