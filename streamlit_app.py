import streamlit as st
from datetime import date

from tools import (
    check_missing_info,
    get_policy,
    select_policy,
    prepare_tasks,
    draft_welcome_email
)

from agent import run_onboarding_agent

st.set_page_config(
    page_title="AutoFirstHi",
    page_icon="👋",
    layout="centered"
)

st.title("👋 AutoFirstHi")
st.subheader("AI-Powered Employee Onboarding")
st.write("Let's make every first day easier.")

st.divider()


st.header("New Employee Registration")

with st.form("employee_form"):

    col1, col2 = st.columns(2)

    with col1:
        first_name = st.text_input("First Name *")
        role = st.text_input("Role *")
        manager = st.text_input("Manager Name")

        start_date = st.date_input(
            "Starting Date *",
            value=date.today()
        )

    with col2:
        last_name = st.text_input("Surname *")

        department = st.selectbox(
            "Department *",
            ["Engineering", "Operations", "Research", "HR"]
        )

        employee_email = st.text_input("Employee Email")
        manager_email = st.text_input("Manager Email")

    work_arrangement = st.radio(
        "Work Arrangement *",
        ["Onsite", "Remote", "Hybrid"],
        horizontal=True
    )

    office = None

    if work_arrangement != "Remote":
        office = st.selectbox(
            "Office Location",
            ["Stockholm", "Other"]
        )

    submitted = st.form_submit_button(
        "Start Onboarding",
        type="primary"
    )

if submitted:

    if not first_name or not last_name or not role:
        st.error("Please complete the required fields.")

    else:
        employee = {
            "first_name": first_name,
            "last_name": last_name,
            "role": role,
            "department": department,
            "employee_email": employee_email,
            "manager": manager,
            "manager_email": manager_email,
            "start_date": str(start_date),
            "work_arrangement": work_arrangement,
            "office": office
        }

        # Save employee for future Streamlit reruns
        st.session_state["employee"] = employee

        # Remove previous AI analysis
        st.session_state.pop("ai_analysis", None)

        # Write welcome draft
        st.session_state.pop("welcome_draft", None)

        st.success("Onboarding information submitted!")

if "employee" in st.session_state:

    employee = st.session_state["employee"]

    st.divider()
    st.subheader("Employee Information")
    st.json(employee)

    # Select applicable policies
    selected_rules = select_policy(employee)

    st.subheader("Applicable Onboarding Rules")

    for rule in selected_rules:
        st.write(rule["id"], "-", rule["task"])

    # Generate onboarding tasks
    tasks = prepare_tasks(employee, selected_rules)

    st.subheader("Onboarding Tasks")

    st.dataframe(
        tasks,
        use_container_width=True,
        hide_index=True
    )

    # Welcome email draft and HR approval
    st.subheader("Welcome Email Draft")

    if st.button("Prepare Welcome Email"):
        st.session_state["welcome_draft"] = draft_welcome_email(employee)

    if "welcome_draft" in st.session_state:
        draft = st.session_state["welcome_draft"]

        if "error" in draft:
            st.warning(draft["error"])

        else:
            st.write("To:", draft["to"])
            st.write("CC:", draft["cc"] or "Not specified")
            st.write("Subject:", draft["subject"])

            st.text_area(
                "Email message",
                value=draft["body"],
                height=200,
                disabled=True
            )

            col_approve, col_reject = st.columns(2)

            with col_approve:
                if st.button("Approve Draft"):
                    draft["approval_status"] = "Approved (not sent)"

            with col_reject:
                if st.button("Reject Draft"):
                    draft["approval_status"] = "Rejected"

            st.write("Status:", draft["approval_status"])

    # Check missing employee information
    missing = check_missing_info(employee)

    if missing:
        st.warning(
            "Additional information required: "
            + ", ".join(missing)
        )

    else:
        st.success("All contact details are available!")

st.divider()
st.subheader("DemoTech Policy")

policy = get_policy()

st.write("Policy ID:", policy["policy_id"])
st.write("Number of rules:", len(policy["rules"]))

if "employee" in st.session_state:

    st.divider()
    st.subheader("AI Onboarding Analysis")

    st.write(
        "Use Gemini AI to analyze the onboarding tasks "
        "and explain any missing requirements."
    )

    if st.button(
        "Generate AI Analysis",
        type="primary"
    ):

        with st.spinner(
            "Gemini is analyzing onboarding requirements..."
        ):

            try:
                analysis = run_onboarding_agent(
                    st.session_state["employee"]
                )

                st.session_state["ai_analysis"] = analysis

            except Exception as error:
                st.error(f"AI analysis failed: {error}")

    # Display the saved AI analysis
    if "ai_analysis" in st.session_state:

        st.markdown(
            st.session_state["ai_analysis"]
        )

        st.info(
            "AI-generated recommendations require HR review. "
            "No emails or calendar invitations have been sent."
        )
