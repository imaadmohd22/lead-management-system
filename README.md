# Sales CRM & Pipeline Automation System

A lightweight Customer Relationship Management (CRM) application built with Python and Streamlit. It helps businesses organize leads, track sales opportunities, prioritize potential customers, and manage follow-ups from one interface.

## Features

- **Lead Management:** Add, search, edit, and delete customer leads.
- **Sales Pipeline:** Track leads across New Lead, Contacted, Qualified, Proposal, Won, and Lost stages.
- **Rule-Based Lead Scoring:** Calculate a score from estimated budget, interest, and engagement.
- **Follow-Up Tracking:** Identify overdue, due-today, and upcoming follow-ups.
- **Sales Analytics:** View lead counts, deal wins, conversion rate, and open pipeline value.
- **Data Export:** Download lead records as CSV or Excel files.
- **SQLite Storage:** Save lead records locally in a database.

## Tech Stack

- Python
- Streamlit
- Pandas
- SQLite
- OpenPyXL

## Project Structure

```text
lead-management-system/
├── app.py
├── requirements.txt
├── .gitignore
└── README.md
```

The `crm.db` database is created automatically when the application runs. It is intentionally excluded from Git.

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/lead-management-system.git
cd lead-management-system
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create and activate a virtual environment

**Windows PowerShell:**

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Start the application

```powershell
python -m streamlit run app.py
```

Streamlit will display a local URL in the terminal. Open that URL in your browser.

## How Lead Scoring Works

The application calculates a score out of 100 using three inputs:

- Estimated budget: up to 30 points
- Interest level: up to 35 points
- Engagement level: up to 35 points

Scores are categorized as:

- **High:** 75–100
- **Medium:** 50–74
- **Low:** Below 50

This is a transparent, rule-based scoring system, not a trained machine-learning model.

## Data and Deployment Notes

The application uses a local SQLite database named `crm.db`. For local development, records persist across app reruns.

For hosted deployment, local filesystem persistence may not be guaranteed. A production deployment should use a persistent database service before storing real customer information.

This project is a portfolio prototype. It does not currently include user authentication, role-based permissions, automatic email or WhatsApp messages, or production-grade security controls.

## Future Improvements

- Persistent hosted database
- User authentication and team-based access
- Automated email reminders
- Advanced sales forecasting
- Configurable lead-scoring rules
- Audit logs and role-based permissions

## Author

Developed as a portfolio project to demonstrate Python application development, CRM workflows, data handling, and business process automation.
