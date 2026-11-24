import pandas as pd
import streamlit as st

from src.config import DATA_DIR, get_smtp_settings
from src.data_loader import load_contacts, load_reminders
from src.mailer import EmailSender, is_valid_email
from src.scheduler import process_due_reminders


@st.cache_data
def load_dashboard_data():
    contacts = load_contacts(DATA_DIR / "contacts.csv")
    reminders = load_reminders(DATA_DIR / "reminders.csv")
    return pd.DataFrame(contacts.values()), pd.DataFrame(reminders)


st.set_page_config(
    page_title="Mailflow | Operations",
    page_icon=":material/mark_email_unread:",
    layout="wide",
)

contacts_df, reminders_df = load_dashboard_data()
now = pd.Timestamp.now()

contacts_df["email_status"] = contacts_df["email"].apply(
    lambda email: "Valid" if is_valid_email(email) else "Invalid"
)
contact_lookup = contacts_df.set_index("contact_id").to_dict("index")
reminders_df["send_at"] = pd.to_datetime(reminders_df["send_at"], errors="coerce")


def reminder_readiness(reminder):
    if pd.isna(reminder["send_at"]):
        return "Invalid date"
    contact = contact_lookup.get(reminder["contact_id"])
    if not contact:
        return "Unknown contact"
    if not is_valid_email(contact["email"]):
        return "Invalid email"
    return "Ready" if reminder["send_at"] <= now else "Scheduled"


reminders_df["readiness"] = reminders_df.apply(reminder_readiness, axis=1)
reminders_df["recipient"] = reminders_df["contact_id"].map(
    contacts_df.set_index("contact_id")["name"]
).fillna("Unknown contact")

with st.sidebar:
    st.markdown("### :material/mark_email_unread: Mailflow")
    st.caption("EMAIL OPERATIONS")
    st.badge("Dry-run mode", icon=":material/shield:", color="green")
    st.space("medium")

    page = st.radio("Workspace", ["Overview", "Reminders", "Contacts"])

    st.space("large")
    st.caption("Data source")
    st.code("data/contacts.csv\ndata/reminders.csv", language=None)
    if st.button(":material/refresh: Refresh data", width="stretch"):
        load_dashboard_data.clear()
        st.rerun()

st.caption("OPERATIONS  /  EMAIL AUTOMATION")
st.title(
    {
        "Overview": "Reminder operations",
        "Reminders": "Reminder schedule",
        "Contacts": "Contact directory",
    }[page]
)
st.caption("A clear view of your outreach pipeline, delivery readiness, and data quality.")

metric_cols = st.columns(3, gap="small")
with metric_cols[0]:
    st.metric("Contacts", len(contacts_df), help="Contacts available in the CSV directory", border=True)
with metric_cols[1]:
    st.metric(
        "Ready now",
        int((reminders_df["readiness"] == "Ready").sum()),
        help="Due reminders with a valid contact and email address",
        border=True,
    )
with metric_cols[2]:
    st.metric(
        "Scheduled",
        int((reminders_df["readiness"] == "Scheduled").sum()),
        help="Reminders with a future send time",
        border=True,
    )

if page == "Overview":
    chart_col, quality_col = st.columns([1.3, 1])

    with chart_col:
        with st.container(border=True):
            st.subheader("Pipeline readiness")
            readiness_counts = (
                reminders_df["readiness"]
                .value_counts()
                .rename_axis("Readiness")
                .reset_index(name="Reminders")
            )
            st.bar_chart(readiness_counts, x="Readiness", y="Reminders")

    with quality_col:
        with st.container(border=True):
            st.subheader("Data quality")
            invalid_contacts = int((contacts_df["email_status"] == "Invalid").sum())
            unknown_contacts = int(
                (~reminders_df["contact_id"].isin(contacts_df["contact_id"])).sum()
            )
            needs_attention = int(
                reminders_df["readiness"].isin(
                    ["Invalid date", "Unknown contact", "Invalid email"]
                ).sum()
            )
            st.badge(
                f"{needs_attention} need review",
                icon=":material/warning:",
                color="orange",
            )
            st.metric("Invalid email addresses", invalid_contacts)
            st.metric("Unmatched contact IDs", unknown_contacts)
            st.caption("Resolve these before switching to live email delivery.")

    with st.container(border=True):
        st.subheader("Latest reminders")
        latest = reminders_df.sort_values("send_at", na_position="last").head(6)
        st.dataframe(
            latest[["reminder_id", "title", "recipient", "send_at", "readiness"]],
            hide_index=True,
            column_config={
                "reminder_id": st.column_config.TextColumn("ID", width="small"),
                "send_at": st.column_config.DatetimeColumn(
                    "Send at", format="MMM DD, YYYY · hh:mm a"
                ),
                "readiness": st.column_config.TextColumn("Readiness"),
            },
        )

    if st.button(
        ":material/play_arrow: Preview ready reminders",
        type="primary",
    ):
        contacts = load_contacts(DATA_DIR / "contacts.csv")
        reminders = load_reminders(DATA_DIR / "reminders.csv")
        sender = EmailSender(get_smtp_settings(), dry_run=True)
        st.session_state["preview_results"] = process_due_reminders(
            reminders,
            contacts,
            sender,
            pd.Timestamp.now(),
        )

    if "preview_results" in st.session_state:
        results = st.session_state["preview_results"]
        if results:
            st.success(f"Previewed {len(results)} due reminder(s). No emails were sent.")
            st.dataframe(pd.DataFrame(results), hide_index=True)
        else:
            st.info("There are no reminders ready to preview.")

elif page == "Reminders":
    filter_col, search_col = st.columns([1, 2])
    with filter_col:
        selected_readiness = st.selectbox(
            "Readiness",
            ["All"] + sorted(reminders_df["readiness"].unique().tolist()),
        )
    with search_col:
        search = st.text_input("Search reminders", placeholder="Search title, recipient, or ID")

    visible = reminders_df.copy()
    if selected_readiness != "All":
        visible = visible[visible["readiness"] == selected_readiness]
    if search:
        searchable = visible[["reminder_id", "title", "recipient"]].astype(str)
        matches = searchable.apply(
            lambda column: column.str.contains(search, case=False, na=False)
        ).any(axis=1)
        visible = visible[matches]

    st.caption(f"Showing {len(visible)} of {len(reminders_df)} reminders")
    st.dataframe(
        visible[
            ["reminder_id", "title", "recipient", "contact_id", "template", "send_at", "repeat", "readiness"]
        ],
        hide_index=True,
        column_config={
            "send_at": st.column_config.DatetimeColumn(
                "Send at", format="MMM DD, YYYY · hh:mm a"
            ),
            "readiness": st.column_config.TextColumn("Readiness"),
        },
    )

else:
    st.caption(f"{len(contacts_df)} contacts in your directory")
    st.dataframe(
        contacts_df[["contact_id", "name", "email", "department", "email_status"]],
        hide_index=True,
        column_config={
            "email_status": st.column_config.TextColumn("Email status"),
        },
    )
