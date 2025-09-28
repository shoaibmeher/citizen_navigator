# agents/question_agent.py

def get_questions_for_service(service_key: str):
    """
    Returns a list of questions required for eligibility checking
    based on the detected service.
    """

    if service_key == "zakat":
        return [
            {"key": "monthly_income", "label": "Monthly household income (PKR):", "type": "number"},
            {"key": "is_muslim", "label": "Are you a Muslim?", "type": "select", "options": ["Yes", "No"]},
            {"key": "is_needy", "label": "Are you financially needy?", "type": "select", "options": ["Yes", "No"]},
        ]

    elif service_key == "ptc_transport":
        return [
            {"key": "age", "label": "Your age:", "type": "number"},
            {"key": "is_senior_citizen", "label": "Are you a senior citizen?", "type": "select", "options": ["Yes", "No"]},
            {"key": "has_cnic", "label": "Do you have a valid CNIC?", "type": "select", "options": ["Yes", "No"]},
        ]

    elif service_key == "health_immunization":
        return [
            {"key": "age_months", "label": "Child's age (in months):", "type": "number"},
            {"key": "is_registered", "label": "Is the child registered with the EPI program?", "type": "select", "options": ["Yes", "No"]},
        ]

    elif service_key == "housing_support":
        return [
            {"key": "monthly_income", "label": "Monthly household income (PKR):", "type": "number"},
            {"key": "family_size", "label": "How many people are in your household?", "type": "number"},
            {"key": "first_time_applicant", "label": "Is this your first time applying for housing support?", "type": "select", "options": ["Yes", "No"]},
            {"key": "has_property", "label": "Do you currently own any property?", "type": "select", "options": ["Yes", "No"]},
        ]

    else:
        return []
