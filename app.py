
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "crm.db"

st.set_page_config(
    page_title="Sales CRM",
    page_icon="🎯",
    layout="wide",
)

STATUSES = [
    "New Lead",
    "Contacted",
    "Qualified",
    "Proposal",
    "Won",
    "Lost",
]

PRIORITIES = ["High", "Medium", "Low"]
SOURCES = ["Website", "LinkedIn", "Referral", "Cold Call", "Other"]


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                company TEXT,
                source TEXT NOT NULL DEFAULT 'Other',
                status TEXT NOT NULL DEFAULT 'New Lead',
                budget REAL NOT NULL DEFAULT 0,
                interest INTEGER NOT NULL DEFAULT 3,
                engagement INTEGER NOT NULL DEFAULT 3,
                assigned_to TEXT DEFAULT '',
                next_follow_up TEXT DEFAULT '',
                notes TEXT DEFAULT '',
                created_at TEXT NOT NULL
            )
        """)


def calculate_score(budget, interest, engagement):
    # Transparent rule-based score, not a trained ML model.
    budget_score = min(max(float(budget), 0), 100000) / 100000 * 30
    interest_score = min(max(int(interest), 1), 5) / 5 * 35
    engagement_score = min(max(int(engagement), 1), 5) / 5 * 35

    return round(budget_score + interest_score + engagement_score)


def score_label(score):
    if score >= 75:
        return "High"
    if score >= 50:
        return "Medium"
    return "Low"


def fetch_leads():
    with get_connection() as connection:
        rows = connection.execute(
            "SELECT * FROM leads ORDER BY id DESC"
        ).fetchall()

    df = pd.DataFrame([dict(row) for row in rows])

    if not df.empty:
        df["Lead Score"] = df.apply(
            lambda row: calculate_score(
                row["budget"], row["interest"], row["engagement"]
            ),
            axis=1,
        )
        df["Priority"] = df["Lead Score"].apply(score_label)

    return df


def add_lead(data):
    with get_connection() as connection:
        connection.execute("""
            INSERT INTO leads (
                name, email, company, source, status, budget,
                interest, engagement, assigned_to,
                next_follow_up, notes, created_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data["name"].strip(),
            data["email"].strip(),
            data["company"].strip(),
            data["source"],
            data["status"],
            data["budget"],
            data["interest"],
            data["engagement"],
            data["assigned_to"].strip(),
            str(data["next_follow_up"]) if data["next_follow_up"] else "",
            data["notes"].strip(),
            date.today().isoformat(),
        ))


def update_lead(lead_id, data):
    with get_connection() as connection:
        connection.execute("""
            UPDATE leads
            SET name=?, email=?, company=?, source=?, status=?,
                budget=?, interest=?, engagement=?, assigned_to=?,
                next_follow_up=?, notes=?
            WHERE id=?
        """, (
            data["name"].strip(),
            data["email"].strip(),
            data["company"].strip(),
            data["source"],
            data["status"],
            data["budget"],
            data["interest"],
            data["engagement"],
            data["assigned_to"].strip(),
            str(data["next_follow_up"]) if data["next_follow_up"] else "",
            data["notes"].strip(),
            int(lead_id),
        ))


def delete_lead(lead_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM leads WHERE id=?", (int(lead_id),))


def seed_sample_data():
    with get_connection() as connection:
        count = connection.execute(
            "SELECT COUNT(*) FROM leads"
        ).fetchone()[0]

    if count:
        return False

    samples = [
        {
            "name": "Aarav Sharma", "email": "aarav@example.com",
            "company": "BrightTech", "source": "Website",
            "status": "Qualified", "budget": 80000,
            "interest": 5, "engagement": 4, "assigned_to": "Sales Team",
            "next_follow_up": date.today().isoformat(),
            "notes": "Interested in a business software package",
        },
        {
            "name": "Priya Verma", "email": "priya@example.com",
            "company": "Northstar Retail", "source": "Referral",
            "status": "Proposal", "budget": 65000,
            "interest": 4, "engagement": 5, "assigned_to": "Sales Team",
            "next_follow_up": (date.today() + timedelta(days=1)).isoformat(),
            "notes": "Proposal discussion pending",
        },
        {
            "name": "Kabir Khan", "email": "kabir@example.com",
            "company": "UrbanWorks", "source": "LinkedIn",
            "status": "New Lead", "budget": 20000,
            "interest": 3, "engagement": 2, "assigned_to": "Imaad",
            "next_follow_up": date.today().isoformat(),
            "notes": "Contact and understand requirements",
        },
        {
            "name": "Sara Mehta", "email": "sara@example.com",
            "company": "Mehta Foods", "source": "Cold Call",
            "status": "Won", "budget": 90000,
            "interest": 5, "engagement": 5, "assigned_to": "Sales Team",
            "next_follow_up": "",
            "notes": "Deal closed successfully",
        },
    ]

    for sample in samples:
        add_lead(sample)

    return True


initialize_database()

st.title("🎯 Sales CRM & Pipeline")
st.caption("Manage leads, prioritize opportunities, and track follow-ups.")

with st.sidebar:
    st.header("CRM Controls")
    if st.button("Load Sample Leads", use_container_width=True):
        if seed_sample_data():
            st.success("Sample leads added.")
        else:
            st.info("Database already contains leads.")

    st.caption("Data is stored locally in crm.db.")
    st.divider()
    page = st.radio(
        "Navigate",
        ["Overview", "Add Lead", "Manage Leads", "Sales Pipeline",
         "Follow-ups", "Export"],
    )

df = fetch_leads()

if page == "Overview":
    st.subheader("Sales Overview")

    if df.empty:
        st.info("No leads yet. Use Add Lead or Load Sample Leads.")
    else:
        total = len(df)
        active = len(df[~df["status"].isin(["Won", "Lost"])])
        won = len(df[df["status"] == "Won"])
        lost = len(df[df["status"] == "Lost"])
        conversion = won / total * 100 if total else 0
        pipeline_value = df.loc[
            ~df["status"].isin(["Won", "Lost"]), "budget"
        ].sum()

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Leads", total)
        c2.metric("Active Leads", active)
        c3.metric("Deals Won", won)
        c4.metric("Conversion Rate", f"{conversion:.1f}%")
        c5.metric("Open Pipeline", f"₹{pipeline_value:,.0f}")

        st.divider()
        left, right = st.columns(2)

        with left:
            st.markdown("#### Leads by Status")
            status_counts = (
                df["status"].value_counts().reindex(STATUSES, fill_value=0)
            )
            st.bar_chart(status_counts)

        with right:
            st.markdown("#### Leads by Source")
            st.bar_chart(df["source"].value_counts())

        st.markdown("#### Highest-Priority Leads")
        top_leads = df.sort_values(
            "Lead Score", ascending=False
        ).head(5)
        st.dataframe(
            top_leads[
                ["name", "company", "status", "Lead Score", "Priority"]
            ],
            use_container_width=True,
            hide_index=True,
        )

elif page == "Add Lead":
    st.subheader("Add a New Lead")

    with st.form("add_lead_form", clear_on_submit=True):
        name = st.text_input("Full Name *")
        email = st.text_input("Email")
        company = st.text_input("Company")
        c1, c2 = st.columns(2)

        with c1:
            source = st.selectbox("Lead Source", SOURCES)
            status = st.selectbox("Sales Status", STATUSES)
            budget = st.number_input(
                "Estimated Deal Budget (₹)", min_value=0.0, step=1000.0
            )

        with c2:
            interest = st.slider("Interest Level", 1, 5, 3)
            engagement = st.slider("Engagement Level", 1, 5, 3)
            assigned_to = st.text_input("Assigned To")

        follow_up = st.date_input(
            "Next Follow-up Date",
            value=date.today() + timedelta(days=1),
        )
        notes = st.text_area("Notes")
        submitted = st.form_submit_button(
            "Save Lead", type="primary", use_container_width=True
        )

        if submitted:
            if not name.strip():
                st.error("Full Name is required.")
            else:
                add_lead({
                    "name": name, "email": email, "company": company,
                    "source": source, "status": status, "budget": budget,
                    "interest": interest, "engagement": engagement,
                    "assigned_to": assigned_to, "next_follow_up": follow_up,
                    "notes": notes,
                })
                st.success("Lead saved successfully.")
                st.rerun()

elif page == "Manage Leads":
    st.subheader("Manage Leads")

    if df.empty:
        st.info("No leads available. Add a lead first.")
    else:
        search = st.text_input("Search by name, company, or email")
        statuses = st.multiselect("Filter by status", STATUSES)
        view = df.copy()

        if search.strip():
            mask = (
                view["name"].fillna("").str.contains(search, case=False)
                | view["company"].fillna("").str.contains(search, case=False)
                | view["email"].fillna("").str.contains(search, case=False)
            )
            view = view[mask]

        if statuses:
            view = view[view["status"].isin(statuses)]

        st.dataframe(
            view[
                ["id", "name", "email", "company", "source", "status",
                 "budget", "assigned_to", "next_follow_up",
                 "Lead Score", "Priority"]
            ],
            use_container_width=True,
            hide_index=True,
        )

        st.divider()
        st.markdown("#### Edit a Lead")

        selected_id = st.selectbox(
            "Choose Lead ID",
            view["id"].tolist() if not view.empty else df["id"].tolist(),
        )
        selected = df[df["id"] == selected_id].iloc[0]

        with st.form("edit_lead_form"):
            edit_name = st.text_input("Full Name", value=selected["name"])
            edit_email = st.text_input("Email", value=selected["email"] or "")
            edit_company = st.text_input("Company", value=selected["company"] or "")
            edit_source = st.selectbox(
                "Source", SOURCES,
                index=SOURCES.index(selected["source"])
                if selected["source"] in SOURCES else len(SOURCES) - 1,
            )
            edit_status = st.selectbox(
                "Status", STATUSES,
                index=STATUSES.index(selected["status"])
                if selected["status"] in STATUSES else 0,
            )
            edit_budget = st.number_input(
                "Budget (₹)", min_value=0.0,
                value=float(selected["budget"]),
                step=1000.0,
            )
            edit_interest = st.slider(
                "Interest", 1, 5, int(selected["interest"])
            )
            edit_engagement = st.slider(
                "Engagement", 1, 5, int(selected["engagement"])
            )
            edit_assignee = st.text_input(
                "Assigned To", value=selected["assigned_to"] or ""
            )

            old_date = selected["next_follow_up"]
            try:
                default_followup = date.fromisoformat(old_date) if old_date else date.today()
            except ValueError:
                default_followup = date.today()

            edit_follow_up = st.date_input(
                "Next Follow-up", value=default_followup
            )
            edit_notes = st.text_area(
                "Notes", value=selected["notes"] or ""
            )

            save_edit = st.form_submit_button("Save Changes")
            if save_edit:
                if not edit_name.strip():
                    st.error("Full Name is required.")
                else:
                    update_lead(int(selected_id), {
                        "name": edit_name, "email": edit_email,
                        "company": edit_company, "source": edit_source,
                        "status": edit_status, "budget": edit_budget,
                        "interest": edit_interest,
                        "engagement": edit_engagement,
                        "assigned_to": edit_assignee,
                        "next_follow_up": edit_follow_up,
                        "notes": edit_notes,
                    })
                    st.success("Lead updated.")
                    st.rerun()

        with st.expander("Delete a Lead"):
            st.warning("Deleting a lead cannot be undone.")
            confirm = st.checkbox(
                f"Confirm deletion of lead #{selected_id}",
                key=f"confirm_delete_{selected_id}",
            )
            if st.button("Delete Selected Lead", type="primary"):
                if confirm:
                    delete_lead(int(selected_id))
                    st.success("Lead deleted.")
                    st.rerun()
                else:
                    st.error("Confirm deletion first.")

elif page == "Sales Pipeline":
    st.subheader("Sales Pipeline")

    if df.empty:
        st.info("Add leads to see the pipeline.")
    else:
        columns = st.columns(len(STATUSES))
        for col, status in zip(columns, STATUSES):
            stage = df[df["status"] == status]
            with col:
                st.markdown(f"**{status}**")
                st.metric("Leads", len(stage))
                st.caption(
                    f"Value: ₹{stage['budget'].sum():,.0f}"
                )
                for _, lead in stage.iterrows():
                    with st.container(border=True):
                        st.write(f"**{lead['name']}**")
                        st.caption(lead["company"] or "No company")
                        st.write(f"₹{lead['budget']:,.0f}")
                        st.caption(
                            f"Score: {lead['Lead Score']} · {lead['Priority']}"
                        )

elif page == "Follow-ups":
    st.subheader("Follow-up Center")

    if df.empty:
        st.info("No leads available.")
    else:
        open_leads = df[
            ~df["status"].isin(["Won", "Lost"])
        ].copy()

        def followup_group(value):
            if not value:
                return "Not scheduled"
            try:
                follow_date = date.fromisoformat(str(value))
            except ValueError:
                return "Not scheduled"
            if follow_date < date.today():
                return "Overdue"
            if follow_date == date.today():
                return "Due Today"
            return "Upcoming"

        open_leads["Follow-up State"] = open_leads[
            "next_follow_up"
        ].apply(followup_group)

        overdue = open_leads[open_leads["Follow-up State"] == "Overdue"]
        due_today = open_leads[
            open_leads["Follow-up State"] == "Due Today"
        ]
        upcoming = open_leads[
            open_leads["Follow-up State"] == "Upcoming"
        ]

        c1, c2, c3 = st.columns(3)
        c1.metric("Overdue", len(overdue))
        c2.metric("Due Today", len(due_today))
        c3.metric("Upcoming", len(upcoming))

        st.markdown("#### Leads Requiring Attention")
        attention = open_leads[
            open_leads["Follow-up State"].isin(["Overdue", "Due Today"])
        ].sort_values("Lead Score", ascending=False)

        if attention.empty:
            st.success("No overdue or today's follow-ups.")
        else:
            st.dataframe(
                attention[
                    ["name", "company", "email", "status",
                     "assigned_to", "next_follow_up",
                     "Follow-up State", "Lead Score"]
                ],
                use_container_width=True,
                hide_index=True,
            )

        st.markdown("#### All Open Follow-ups")
        st.dataframe(
            open_leads[
                ["name", "company", "status", "next_follow_up",
                 "Follow-up State", "assigned_to"]
            ].sort_values("next_follow_up"),
            use_container_width=True,
            hide_index=True,
        )

elif page == "Export":
    st.subheader("Export CRM Data")

    if df.empty:
        st.info("No leads to export.")
    else:
        export_df = df.drop(columns=[], errors="ignore")
        csv_bytes = export_df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "Download Leads as CSV",
            data=csv_bytes,
            file_name="crm_leads.csv",
            mime="text/csv",
            use_container_width=True,
        )

        excel_buffer = __import__("io").BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
            export_df.to_excel(writer, index=False, sheet_name="Leads")

        st.download_button(
            "Download Leads as Excel",
            data=excel_buffer.getvalue(),
            file_name="crm_leads.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        st.caption("Exports include lead details and calculated priority scores.")

st.divider()
st.caption("CRM prototype · Rule-based lead scoring · Local SQLite storage")
