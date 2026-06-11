# AI Implementation Copilot — Classification Categories

This document explains the classification categories used by the **AI Implementation Copilot**.

The goal of the classifier is not only to detect keywords, but to identify the most appropriate **AI implementation pattern** for a messy operational business problem.

The classifier should answer:

> What kind of AI implementation pattern best solves this business problem?

These categories are not mutually exclusive. Most real client problems will have a **primary classification** and several **secondary classifications**. In many enterprise scenarios, the correct answer will be **Hybrid**.

---

## 1. RAG

### Meaning

**RAG** means **Retrieval-Augmented Generation**.

Use RAG when the AI needs to answer questions, reason, or generate responses based on a specific knowledge base, such as:

- PDFs
- Manuals
- Policies
- Contracts
- SOPs
- Internal documentation
- FAQs
- Product catalogs
- Technical procedures
- Customer-specific knowledge

The key idea:

> The answer should come from company-owned or domain-specific documents, not only from the model’s general knowledge.

### When to classify as RAG

Use this classification when the business problem includes language like:

- “We need to answer questions based on documents.”
- “Our employees search manuals manually.”
- “Support agents look through PDFs.”
- “We have internal policies nobody can find.”
- “We want a chatbot trained on our knowledge base.”
- “Technicians need fast answers from service manuals.”
- “Salespeople need product answers from catalogs.”

### Example problem

> Our support team receives technical questions from customers. They need to search through hundreds of PDF manuals to find the right answer. The process is slow and inconsistent.

### Example classification

```json
{
  "primary_solution_type": "RAG",
  "secondary_solution_types": [
    "Workflow Automation",
    "Human-in-the-loop Review"
  ],
  "rationale": "The core problem is retrieving reliable answers from internal technical documents."
}
```

### Suggested architecture

- Document ingestion
- Chunking
- Embedding generation
- Vector database
- Retrieval layer
- LLM response generation
- Source citation
- Feedback loop
- Human review for low-confidence answers

### Good use cases

- Internal knowledge assistants
- Technical support copilots
- Legal/policy Q&A
- Product recommendation based on catalogs
- Service manual search
- HR or compliance assistants

### Not ideal when

RAG is not ideal when the main need is:

- Predicting future values
- Extracting data from scanned images
- Executing multi-step actions
- Updating CRMs or ERPs
- Making operational decisions without document retrieval

In those cases, RAG may be secondary, not primary.

---

## 2. Agentic Workflow

### Meaning

An **Agentic Workflow** is needed when the AI must perform multiple steps, make decisions, use tools, call APIs, validate outputs, and possibly coordinate several specialized agents.

The key idea:

> The system does not just answer. It acts through a sequence of reasoning and tool-based steps.

### When to classify as Agentic Workflow

Use this classification when the problem includes:

- Several dependent steps
- Different decision points
- Multiple tools or systems
- Need for specialized roles
- Automated task execution
- Reasoning plus action
- Exception handling

Typical phrases:

- “The AI should analyze, decide, and then update the system.”
- “We need several agents handling different parts of the process.”
- “The workflow changes depending on the input.”
- “The system should check documents, classify the case, update CRM, and draft a response.”
- “We want an AI agent to coordinate the process.”

### Example problem

> When a customer submits a claim, someone needs to read the email, extract information from the attachment, check the policy, classify the claim, update the CRM, and draft a response. Today this is all manual.

### Example classification

```json
{
  "primary_solution_type": "Agentic Workflow",
  "secondary_solution_types": [
    "OCR / Document Extraction",
    "RAG",
    "API Integration",
    "Human-in-the-loop Review"
  ],
  "rationale": "The problem requires multiple AI-assisted steps, tool usage, system updates, and decision-making."
}
```

### Suggested architecture

- Intake Agent
- Document Understanding Agent
- Classification Agent
- Policy/RAG Agent
- CRM Update Agent
- QA Agent
- Human Approval Agent
- Response Drafting Agent

### Good use cases

- Claims processing
- Customer support automation
- Sales operations automation
- Back-office document workflows
- Procurement request handling
- Multi-step compliance checks
- AI assistants that use tools and APIs

### Important distinction

Not every AI workflow is agentic.

A simple chatbot over documents is usually **RAG**, not agentic.

A script that moves data from one spreadsheet to another is usually **Workflow Automation**, not agentic.

It becomes agentic when the system needs to reason across steps, use tools, make choices, and adapt its path.

---

## 3. Workflow Automation

### Meaning

**Workflow Automation** means the main problem is repetitive manual work that follows a relatively predictable process.

The key idea:

> Humans are doing repetitive operational steps that can be automated or partially automated.

This may or may not require AI. Sometimes the correct solution is a simple automation with business rules, APIs, and scheduled jobs.

### When to classify as Workflow Automation

Use this classification when the problem includes:

- Manual copy/paste
- Repeated emails
- Spreadsheet updates
- Routing tasks
- Approvals
- Status updates
- Repetitive back-office operations
- Moving information between systems

Typical phrases:

- “Our team manually updates spreadsheets.”
- “People copy data from emails into CRM.”
- “We send the same status reports every week.”
- “The process is repetitive and slow.”
- “We want to reduce manual work.”
- “There is too much rework.”

### Example problem

> Every morning, our operations analyst downloads a CSV from one system, cleans it manually in Excel, updates a tracker, and emails a summary to managers.

### Example classification

```json
{
  "primary_solution_type": "Workflow Automation",
  "secondary_solution_types": [
    "API Integration",
    "Reporting Automation"
  ],
  "rationale": "The main value comes from automating a repetitive operational process."
}
```

### Suggested architecture

- Scheduled job
- Data ingestion
- Validation rules
- Transformation logic
- Report generation
- Notification/email layer
- Audit log

### Good use cases

- Internal operations
- Repetitive reporting
- Email triage
- Spreadsheet replacement
- Task routing
- SLA follow-up
- Approval flows
- Back-office productivity

### Important distinction

Workflow Automation does not always require a complex LLM.

A senior implementation lead should be able to say:

> This does not need agents. This is mostly deterministic automation with maybe one AI classification step.

That shows maturity.

---

## 4. Forecasting / Predictive Analytics

### Meaning

**Forecasting / Predictive Analytics** means the business wants to predict something based on historical data.

The key idea:

> The system uses historical patterns to estimate future outcomes or risk.

### When to classify as Forecasting / Predictive Analytics

Use this classification when the problem involves:

- Future demand
- Sales forecast
- Inventory forecast
- Churn risk
- Failure prediction
- Revenue prediction
- Capacity planning
- Anomaly detection
- Lead scoring
- Probability of an event

Typical phrases:

- “We want to predict future sales.”
- “We need to know which customers will churn.”
- “We want to forecast demand.”
- “We need to predict maintenance failures.”
- “We want to identify risk before it happens.”
- “We need inventory recommendations.”

### Example problem

> We have three years of sales history by SKU and store. We want to know what each store is likely to sell next month and what products should be replenished.

### Example classification

```json
{
  "primary_solution_type": "Forecasting / Predictive Analytics",
  "secondary_solution_types": [
    "Workflow Automation",
    "Dashboarding"
  ],
  "rationale": "The core business need is predicting future sales and using those predictions to support inventory decisions."
}
```

### Suggested architecture

- Historical data ingestion
- Data cleaning
- Feature engineering
- Forecasting model
- Prediction output
- Business rules layer
- Dashboard
- Monitoring and retraining plan

### Good use cases

- Sales forecast
- Demand planning
- Inventory optimization
- Churn prediction
- Credit risk
- Maintenance prediction
- Delivery volume prediction
- Staffing/capacity prediction

### Important distinction

If the user asks:

> What happened last month?

That is analytics/reporting.

If the user asks:

> What is likely to happen next month?

That is forecasting or predictive analytics.

---

## 5. OCR / Document Extraction

### Meaning

**OCR / Document Extraction** means the system needs to read documents, scanned images, PDFs, invoices, forms, receipts, or attachments and extract structured data.

The key idea:

> The input is trapped inside documents, images, or semi-structured files, and the business needs structured fields.

OCR is only one part. Sometimes the system also needs layout understanding, table extraction, entity extraction, and validation.

### When to classify as OCR / Document Extraction

Use this classification when the problem mentions:

- PDFs
- Scanned documents
- Invoices
- Purchase orders
- Receipts
- Forms
- Contracts
- Attachments
- Photos
- Handwritten or scanned content
- Extracting fields from documents

Typical phrases:

- “We receive PDFs by email.”
- “Someone manually reads invoices.”
- “We need to extract data from forms.”
- “The information is inside scanned documents.”
- “We process attached files manually.”
- “We need to read purchase orders and update the system.”

### Example problem

> Our finance team receives hundreds of supplier invoices in PDF format. They manually read each invoice and type vendor, amount, due date, and tax information into the ERP.

### Example classification

```json
{
  "primary_solution_type": "OCR / Document Extraction",
  "secondary_solution_types": [
    "Workflow Automation",
    "API Integration",
    "Human-in-the-loop Review"
  ],
  "rationale": "The main bottleneck is manually extracting structured data from PDF invoices."
}
```

### Suggested architecture

- Document upload or email ingestion
- OCR/document parser
- Field extraction
- Confidence scoring
- Validation rules
- Human review for low-confidence fields
- ERP/API integration
- Audit trail

### Good use cases

- Invoice processing
- Purchase order automation
- Insurance claims
- Medical forms
- Logistics documents
- Bills of lading
- HR documents
- Contracts and onboarding forms

### Important distinction

If the document is used mainly for answering questions, classify as **RAG**.

If the document is used mainly to extract structured fields, classify as **OCR / Document Extraction**.

If both are needed, classify as **Hybrid**.

---

## 6. API Integration

### Meaning

**API Integration** means the AI system needs to connect with existing business systems to read or write data.

The key idea:

> The AI solution must interact with operational systems, not live in isolation.

This is especially important for real business value. Many AI demos fail because they generate answers but do not integrate with the actual workflow.

### When to classify as API Integration

Use this classification when the problem mentions:

- CRM
- ERP
- Ticketing system
- Database
- Internal system
- SaaS platform
- Logistics platform
- Payment system
- Updating records
- Retrieving status
- Creating tasks
- Calling endpoints

Typical phrases:

- “The system should update the CRM.”
- “We need to check order status in the ERP.”
- “The AI should create a ticket.”
- “We need to integrate with Salesforce, HubSpot, SAP, or ServiceNow.”
- “The answer depends on live data from our system.”
- “The workflow should call an API.”

### Example problem

> Customer service agents receive delivery status questions. They manually check the logistics platform and then reply to customers on WhatsApp.

### Example classification

```json
{
  "primary_solution_type": "API Integration",
  "secondary_solution_types": [
    "Workflow Automation",
    "Agentic Workflow"
  ],
  "rationale": "The solution needs to retrieve live delivery status from an operational system and return it to the user."
}
```

### Suggested architecture

- User/channel intake
- Intent classification
- API authentication
- API call to source system
- Response formatting
- Error handling
- Logging
- Fallback to human support

### Good use cases

- CRM updates
- ERP lookups
- Ticket creation
- Order tracking
- Logistics status
- Payment status
- Customer profile retrieval
- Automated system actions

### Important distinction

A chatbot that only answers from static documents may not need API integration.

But if the user asks:

> Where is my order right now?

That needs live system data, so API integration becomes central.

---

## 7. Human-in-the-loop Review

### Meaning

**Human-in-the-loop Review** means the AI should not act fully autonomously. A human must review, approve, correct, or override the output before final execution.

The key idea:

> AI assists the process, but humans remain responsible for sensitive, risky, ambiguous, or high-impact decisions.

### When to classify as Human-in-the-loop Review

Use this classification when the workflow involves:

- High-risk decisions
- Compliance
- Legal content
- Financial approvals
- Medical or health-related interpretation
- Customer-facing messages
- Low-confidence outputs
- Exceptions
- Sensitive data
- Potential business damage if wrong

Typical phrases:

- “A manager must approve before sending.”
- “We cannot fully automate this.”
- “The AI should draft, but a person should review.”
- “Some cases are sensitive.”
- “We need auditability.”
- “We need confidence thresholds.”

### Example problem

> We want AI to draft responses to customer complaints, but managers need to approve the message before it is sent, especially for refund or legal cases.

### Example classification

```json
{
  "primary_solution_type": "Human-in-the-loop Review",
  "secondary_solution_types": [
    "RAG",
    "Workflow Automation"
  ],
  "rationale": "The AI can assist with drafting and retrieval, but human approval is needed due to customer impact and possible exceptions."
}
```

### Suggested architecture

- AI draft generation
- Confidence score
- Risk classification
- Human approval queue
- Edit/approve/reject interface
- Audit log
- Feedback capture
- Escalation rules

### Good use cases

- Legal workflows
- Finance approvals
- Medical or health-related workflows
- Customer complaints
- Insurance claims
- Refund approval
- HR decisions
- Compliance-heavy processes

### Important distinction

Human-in-the-loop is often a **secondary classification**.

Examples:

- Invoice processing: OCR primary, human review secondary.
- Support assistant: RAG primary, human review secondary.
- Claims processing: Agentic workflow primary, human review secondary.

It becomes primary when risk, approval, or governance is the main concern.

---

## 8. Hybrid

### Meaning

**Hybrid** means the problem requires multiple implementation patterns together.

Most real business problems are hybrid.

The key idea:

> The solution cannot be solved cleanly with only one pattern.

For example, a real customer support automation could require:

- OCR to read attachments
- RAG to check internal procedures
- API integration to update CRM
- Agents to orchestrate steps
- Human approval for risky cases
- Workflow automation to move tasks

### When to classify as Hybrid

Use Hybrid when three or more categories are clearly involved, or when no single category dominates enough.

Typical signals:

- Documents + system updates + human approval
- Prediction + workflow automation
- RAG + API calls + multi-step agents
- OCR + RAG + CRM integration
- Operational process with multiple systems and exceptions

### Example problem

> Our customer support team receives hundreds of emails with attached PDFs. They manually classify requests, check internal procedures, update the CRM, and send a response to the client. The process is slow and inconsistent.

### Example classification

```json
{
  "primary_solution_type": "Hybrid",
  "secondary_solution_types": [
    "OCR / Document Extraction",
    "RAG",
    "Agentic Workflow",
    "API Integration",
    "Workflow Automation",
    "Human-in-the-loop Review"
  ],
  "rationale": "The problem includes document understanding, internal knowledge lookup, CRM integration, multi-step orchestration, and human approval for sensitive cases."
}
```

### Suggested architecture

- Email intake
- Attachment parser
- OCR/document extraction
- Request classification
- RAG over internal procedures
- CRM integration
- Agentic orchestration
- Human approval queue
- Client response generation
- Audit and monitoring layer

### Good use cases

- Real enterprise AI implementation
- Back-office automation
- Customer operations
- Claims
- Sales operations
- Finance operations
- Logistics operations
- Compliance workflows

### Important distinction

Hybrid should not mean:

> I do not know.

Hybrid should mean:

> I clearly identified multiple required implementation patterns, and I can explain how they work together.

---

# Practical Classification Examples

## Example 1 — Internal Policy Chatbot

### Problem

> Employees ask HR many questions about vacation, benefits, and internal policies. The HR team spends too much time searching documents and answering repetitive questions.

### Classification

```json
{
  "primary_solution_type": "RAG",
  "secondary_solution_types": [
    "Workflow Automation",
    "Human-in-the-loop Review"
  ]
}
```

### Why

The main task is answering from internal HR policies.

---

## Example 2 — Invoice Processing

### Problem

> Our accounting team receives supplier invoices as PDFs and manually enters vendor, amount, due date, and tax data into the ERP.

### Classification

```json
{
  "primary_solution_type": "OCR / Document Extraction",
  "secondary_solution_types": [
    "Workflow Automation",
    "API Integration",
    "Human-in-the-loop Review"
  ]
}
```

### Why

The bottleneck is extracting structured information from documents and entering it into a system.

---

## Example 3 — Churn Prediction

### Problem

> We want to know which customers are likely to cancel their subscription in the next 60 days and why.

### Classification

```json
{
  "primary_solution_type": "Forecasting / Predictive Analytics",
  "secondary_solution_types": [
    "Dashboarding",
    "Workflow Automation"
  ]
}
```

### Why

The core need is predicting a future event.

---

## Example 4 — Delivery Status Assistant

### Problem

> Drivers and customers contact support asking about delivery sequence and estimated arrival. Agents manually check the logistics platform and respond through WhatsApp.

### Classification

```json
{
  "primary_solution_type": "API Integration",
  "secondary_solution_types": [
    "Workflow Automation",
    "Agentic Workflow"
  ]
}
```

### Why

The answer depends on live operational data from another system.

---

## Example 5 — Complex Support Automation

### Problem

> Support receives emails with attachments. They need to classify the request, extract document data, check internal procedures, update CRM, and draft a response.

### Classification

```json
{
  "primary_solution_type": "Hybrid",
  "secondary_solution_types": [
    "OCR / Document Extraction",
    "RAG",
    "Agentic Workflow",
    "API Integration",
    "Human-in-the-loop Review",
    "Workflow Automation"
  ]
}
```

### Why

This requires several patterns working together.

---

# Suggested Classifier Logic

The classifier should follow this reasoning:

```text
If the problem mainly requires answers from internal documents:
    classify as RAG

If the problem requires multi-step reasoning, agents, tools, or dynamic decisions:
    classify as Agentic Workflow

If the problem is mostly repetitive manual task execution:
    classify as Workflow Automation

If the problem involves predicting future values, risks, demand, churn, failures, or probabilities:
    classify as Forecasting / Predictive Analytics

If the problem involves extracting information from PDFs, scans, invoices, forms, images, or attachments:
    classify as OCR / Document Extraction

If the problem requires reading from or writing to CRM, ERP, ticketing systems, databases, or external platforms:
    classify as API Integration

If the problem is sensitive, risky, low-confidence, compliance-heavy, or customer-facing:
    add Human-in-the-loop Review

If three or more patterns are clearly needed:
    classify primary as Hybrid
```

---

# Recommended Classifier Output Structure

The classifier should return a structured object like this:

```json
{
  "primary_solution_type": "Hybrid",
  "secondary_solution_types": [
    "OCR / Document Extraction",
    "RAG",
    "Agentic Workflow",
    "API Integration",
    "Human-in-the-loop Review"
  ],
  "confidence_score": 0.88,
  "rationale": "The workflow involves extracting information from attached PDFs, checking internal procedures, updating CRM records, and drafting customer responses. Because multiple implementation patterns are required, this is best classified as a hybrid AI workflow."
}
```

---

# Final Principle

Do not make the classifier behave like a toy keyword detector.

Make it behave like a junior version of an AI implementation architect.

It should answer:

> What is the real implementation pattern behind this business problem, and what should we build first?

That is the kind of thinking the AI Implementation Copilot should demonstrate.
