# agents/eligibility_agent.py
from typing import Tuple, List

def evaluate_service_eligibility(
    service_key: str,
    form_data: dict,
    policy_context: str = ""
) -> Tuple[bool, List[str], List[str]]:
    """
    Determines eligibility for each service based on form data and policy context.
    """

    eligible = False
    reasons = []
    required_docs = []

    # ✅ Zakat
    if service_key == "zakat":
        income = int(form_data.get("monthly_income", 0))
        is_muslim = form_data.get("is_muslim", "Yes") == "Yes"
        is_needy = form_data.get("is_needy", "Yes") == "Yes"

        if is_muslim and is_needy and income < 60000:
            eligible = True
            reasons.append("Meets Zakat criteria (Muslim, needy, income below PKR 60,000).")
            required_docs += ["CNIC copy", "Income certificate"]
        else:
            reasons.append("Does not meet Zakat eligibility conditions.")

    # ✅ PTC Transport Card
    elif service_key == "ptc_transport":
        age = int(form_data.get("age", 0))
        is_senior = form_data.get("is_senior_citizen", "No") == "Yes"
        has_cnic = form_data.get("has_cnic", "No") == "Yes"

        if (age >= 60 or is_senior) and has_cnic:
            eligible = True
            reasons.append("Eligible for free transport card (Senior citizen with valid CNIC).")
            required_docs += ["CNIC copy", "Proof of age"]
        else:
            reasons.append("Does not meet transport card eligibility.")

    # ✅ Health Immunization
    elif service_key == "health_immunization":
        age_months = int(form_data.get("age_months", 0))
        is_registered = form_data.get("is_registered", "No") == "Yes"

        if age_months <= 60 and is_registered:
            eligible = True
            reasons.append("Eligible for immunization (Child under 5 and registered).")
            required_docs += ["Birth certificate", "Guardian CNIC"]
        else:
            reasons.append("Does not meet immunization criteria.")

    # ✅ Housing Support (LDA)
    elif service_key == "housing_support":
        income = int(form_data.get("monthly_income", 0))
        family_size = int(form_data.get("family_size", 0))
        first_time = form_data.get("first_time_applicant", "No") == "Yes"
        has_property = form_data.get("has_property", "No") == "No"

        if income <= 80000 and family_size >= 3 and first_time and has_property:
            eligible = True
            reasons.append("Eligible for housing support (Low income, large family, first-time applicant, no property).")
            required_docs += ["CNIC", "Income certificate", "No property certificate"]
        else:
            reasons.append("Does not meet housing support eligibility criteria.")

    else:
        reasons.append("⚠️ This service is not yet supported. We are working on adding it soon.")
        return False, reasons, []

    # ✅ Policy context for transparency
    if policy_context:
        reasons.append("📜 Policy Reference:\n" + (policy_context[:700] + "..." if len(policy_context) > 700 else policy_context))

    return eligible, reasons, required_docs
