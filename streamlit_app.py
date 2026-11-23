import streamlit as st
from datetime import date, datetime, timezone, time
from zoneinfo import ZoneInfo

from tools import (
    check_missing_info,
    get_policy,
    select_policy,
    prepare_tasks,
    draft_welcome_email,
    draft_manager_meeting,
    get_allowed_meeting_dates
)

from agent import run_onboarding_agent

st.set_page_config(
    page_title="AutoFirstHi",
    page_icon="👋",
    layout="centered"
)

if "approval_history" not in st.session_state:
    st.session_state["approval_history"] = []


st.title("AutoFirstHi 👋 ")
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

        # Write meeting draft
        st.session_state.pop("meeting_draft", None)

        st.success("Onboarding information submitted!")

if "employee" in st.session_state:

    employee = st.session_state["employee"]


    st.subheader("Equipment Preferences")

    with st.form("equipment_form"):
        laptop = st.selectbox(
            "Preferred laptop",
            ["MacBook", "Dell", "Lenovo"]
        )

        phone = st.selectbox(
            "Preferred work phone",
            ["iPhone", "Samsung"]
        )

        equipment_submitted = st.form_submit_button(
            "Save Equipment Preferences"
        )

    if equipment_submitted:
        employee["equipment_preferences"] = {
            "laptop": laptop,
            "phone": phone
        }

        st.session_state["employee"] = employee
        st.session_state.pop("ai_analysis", None)
        st.rerun()



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
        st.session_state["include_manager_cc"] = bool(employee.get("manager_email"))

    if "welcome_draft" in st.session_state:
        draft = st.session_state["welcome_draft"]

        if "error" in draft:
            st.warning(draft["error"])

        else:
            st.write("To:", draft["to"])

            include_cc = st.checkbox(
                "Include manager in CC",
                key="include_manager_cc",
                disabled=draft["approval_status"] == "Approved (not sent)"
            )

            new_cc = employee.get("manager_email", "") if include_cc else ""

            if new_cc != draft["cc"]:
                draft["cc"] = new_cc
                draft["approval_status"] = "Awaiting HR approval"

            st.write("CC:", draft["cc"] or "Not specified")

            st.write("Subject:", draft["subject"])

            edited_body = st.text_area(
                "Email message",
                value=draft["body"],
                height=200,
                disabled=(draft["approval_status"] == "Approved (not sent)")
            )

            if edited_body != draft["body"]:
                draft["body"] = edited_body
                draft["approval_status"] = "Awaiting HR approval"


            col_approve, col_reject = st.columns(2)



            with col_approve:
                if st.button("Approve Draft"):
                    draft["approval_status"] = "Approved (not sent)"

                    st.session_state["approval_history"].append({
                        "action": "Welcome email",
                        "decision": "Approved",
                        "employee_email": employee.get("employee_email", ""),
                        "employee": employee.get("first_name", ""),
                        "timestamp_utc": datetime.now(timezone.utc).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    })



            with col_reject:
                if st.button("Reject Draft"):
                    draft["approval_status"] = "Rejected"

                    st.session_state["approval_history"].append({
                        "action": "Welcome email",
                        "decision": "Rejected",
                        "employee_email": employee.get("employee_email", ""),
                        "employee": employee.get("first_name", ""),
                        "timestamp_utc": datetime.now(timezone.utc).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    })



            st.write("Status:", draft["approval_status"])



            if st.session_state["approval_history"]:
                st.dataframe(
                    st.session_state["approval_history"],
                    hide_index=True,
                    width="stretch"
                )
            else:
                st.info("No approval decisions recorded yet.")



    # Manager introduction meeting
    st.divider()
    st.subheader("Manager Introduction Draft")

    if st.button("Prepare Manager Meeting"):
        st.session_state["meeting_draft"] = draft_manager_meeting(employee)

    if "meeting_draft" in st.session_state:
        meeting = st.session_state["meeting_draft"]

        if "error" in meeting:
            st.warning(meeting["error"])

        else:
            st.write("Subject:", meeting["subject"])
            st.write("Attendees:", ", ".join(meeting["attendees"]))

            st.write("Agenda:", meeting["agenda"])

            meeting_date = st.date_input(
                "Proposed meeting date",
                value=date.fromisoformat(employee["start_date"])
            )

            meeting_time = st.time_input(
                "Proposed meeting time",
                value=time(10, 0)
            )

            allowed_dates = get_allowed_meeting_dates(
                employee["start_date"]
            )

            if meeting_date in allowed_dates:
                st.success("Meeting date follows company policy!")
            else:
                st.error(
                    "Meeting must be scheduled within "
                    "the first two working days."
                )

            # Save proposed meeting date and time
            proposed_date = meeting_date.isoformat()
            proposed_time = meeting_time.strftime("%H:%M")

            meeting_timezone = ZoneInfo("Europe/Stockholm")

            proposed_datetime = datetime.combine(
                meeting_date,
                meeting_time,
                tzinfo=meeting_timezone
            )

            is_future = proposed_datetime > datetime.now(
                meeting_timezone
            )

            if not is_future:
                st.error("Meeting must be scheduled in the future.")


            if (
                meeting.get("meeting_date") != proposed_date
                or meeting.get("meeting_time") != proposed_time
            ):
                meeting["meeting_date"] = proposed_date
                meeting["meeting_time"] = proposed_time
                meeting["approval_status"] = "Awaiting HR approval"

            # Create approval buttons
            col_approve, col_reject = st.columns(2)

            with col_approve:
                if st.button(
                    "Approve Meeting",
                    disabled=(
                        meeting_date not in allowed_dates
                        or not is_future
                        or meeting["approval_status"] == "Approved (not sent)"
                    )

                ):

                    meeting["approval_status"] = "Approved (not sent)"


                    st.session_state["approval_history"].append({
                        "action": "Manager meeting",
                        "employee": employee["first_name"],
                        "meeting_date": proposed_date,
                        "meeting_time": proposed_time,
                        "attendees": ", ".join(meeting["attendees"]),
                        "decision": "Approved",
                        "timestamp_utc": datetime.now(timezone.utc).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    })


            with col_reject:
                if st.button("Reject Meeting"):
                    meeting["approval_status"] = "Rejected"

                    st.session_state["approval_history"].append({
                        "employee": employee["first_name"],
                        "meeting_date": proposed_date,
                        "meeting_time": proposed_time,
                        "attendees": ", ".join(meeting["attendees"]),
                        "action": "Manager meeting",
                        "decision": "Rejected",
                        "timestamp_utc": datetime.now(
                            timezone.utc
                        ).strftime("%Y-%m-%d %H:%M:%S")
                    })

            st.write("Status:", meeting["approval_status"])


    # Check missing employee information
    missing = check_missing_info(employee)

    # Combined approval history
    st.divider()
    st.subheader("Approval History")

    if st.session_state["approval_history"]:
        st.dataframe(
            st.session_state["approval_history"],
            hide_index=True,
            width="stretch"
        )
    else:
        st.info("No approval decisions recorded yet.")


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
