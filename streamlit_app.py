import streamlit as st
from datetime import date
from tools import check_missing_info, get_policy, select_policy


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
        st.success("Employee registered for onboarding!")

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

        st.subheader("Employee Information")
        st.json(employee)

        selected_rules = select_policy(employee)

        st.subheader("Applicable Onboarding Rules")

        for rule in selected_rules:
            st.write(rule["id"], "-", rule["task"])



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


