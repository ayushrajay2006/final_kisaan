# policy_advisor.py
# This agent provides information about government schemes and subsidies.

import logging

# This mock database simulates a real database of government schemes.
# The keys are keywords that we will search for in the user's query.
MOCK_SCHEME_DATABASE = {
    "drip irrigation": {
        "scheme_name": "Pradhan Mantri Krishi Sinchayee Yojana (PMKSY)",
        "summary": "This scheme aims to improve water use efficiency through micro-irrigation (drip and sprinkler). Farmers receive a subsidy on the cost of installing the system.",
        "eligibility": "All categories of farmers are eligible. Preference may be given to small and marginal farmers.",
        "documents_needed": "Aadhar card, land ownership documents (Pattadar Passbook/RoR), quote from an approved vendor, passport size photo.",
        "how_to_apply": "Contact your local district horticulture or agriculture office."
    },
    "pm kisan": {
        "scheme_name": "PM-Kisan Samman Nidhi",
        "summary": "An income support scheme where eligible farmer families receive ₹6,000 per year in three equal installments.",
        "eligibility": "All landholding farmer families are eligible, subject to certain exclusion criteria (e.g., high-income earners, institutional landholders).",
        "documents_needed": "Aadhar card, landholding papers, bank account details.",
        "how_to_apply": "Register through the official PM-KISAN portal or at your nearest Common Service Centre (CSC)."
    },
    "crop insurance": {
        "scheme_name": "Pradhan Mantri Fasal Bima Yojana (PMFBY)",
        "summary": "Provides comprehensive insurance coverage against crop failure, helping to stabilize the income of farmers.",
        "eligibility": "All farmers who have taken loans (loanee farmers) are automatically enrolled. Non-loanee farmers can enroll voluntarily.",
        "documents_needed": "Land records, bank passbook, Aadhar card, and crop sowing certificate.",
        "how_to_apply": "Through your bank, a registered insurance company, or the National Crop Insurance Portal."
    }
}

def get_scheme_information(text: str):
    """
    Analyzes text to find keywords related to government schemes and returns information.

    Args:
        text (str): The transcribed text from the user.

    Returns:
        dict: A dictionary containing the scheme details, or an error message.
    """
    text_lower = text.lower()

    # Simple entity extraction: find which scheme the user is asking about.
    for keyword, scheme_info in MOCK_SCHEME_DATABASE.items():
        if keyword in text_lower:
            logging.info(f"Policy Advisor found keyword: {keyword}")
            return {
                "status": "success",
                "data": scheme_info
            }
    
    logging.warning(f"Policy Advisor could not find a known scheme in text: '{text}'")
    return {
        "status": "error",
        "message": "Sorry, I could not find information on the scheme you mentioned. Please try asking in a different way."
    }


