import os
from pathlib import Path

import re
import json

from config import BASE_PATH, ARTIFACTS_PATH, forms_proto_dm_dir_path

def prompt_for_page_dm_chunking(proto_dm):

    system_prompt = f"""
    You will be provided with a broker supplemental application data model in proto format. 
    Your job is to semantically chunk the data model based on questions/sections and develop similar clusters.
    Return a python list of the chunks.

    Proto data model: {proto_dm}

    ONLY RETURN THE LIST WITHOUT ANY EXPLANATIONS
    """

    ex_1 = """
    syntax = "proto3";

    // Contractors Supplemental Application Form

    message ContractorsSupplementalApplication {
    // Section I - Applicant Information
    ApplicantInformation applicant_information = 1;
    
    // Section II - Business Information
    BusinessInformation business_information = 2;
    }

    message ApplicantInformation {
    // Name of Applicant
    string name_of_applicant = 1;
    
    // Address
    string address = 2;
    
    // City
    string city = 3;
    
    // State
    string state = 4;
    
    // Zip Code
    string zip_code = 5;
    
    // P.O. Box City
    string po_box_city = 6;
    
    // P.O. Box State
    string po_box_state = 7;
    
    // P.O. Box Zip Code
    string po_box_zip_code = 8;
    
    // Telephone
    string telephone = 9;
    
    // Website
    string website = 10;
    
    // State(s) / Area of Operation
    string states_area_of_operation = 11;
    
    // Licensed for Business in State(s)
    string licensed_for_business_in_states = 12;
    
    // Years in Business
    string years_in_business = 13;
    
    // Contractor License #
    string contractor_license_number = 14;
    
    // Industry Experience
    string industry_experience = 15;
    
    // Description of Operations
    string description_of_operations = 16;
    }

    message BusinessInformation {
    // Question 1: Is applicant or any proposed named insured one of the following? (Check all that apply.)
    ApplicantTypes applicant_types = 1;
    
    // Question 2: Please provide historical receipts, payroll and cost of subcontracted work.
    HistoricalFinancials historical_financials = 2;
    
    // Question 3: Payroll of owners, officers and partners active at jobsites or performing supervisory duties
    string payroll_of_owners_officers_partners = 3;
    
    // Question 3: Payroll of employees other than owners, officers, partners and clerical
    string payroll_of_employees = 4;
    
    // Question 3: Cost of leased, temporary, staffing service, casual labor (if not included above)
    string cost_of_leased_temporary_labor = 5;
    
    // Question 4: Does the applicant currently own or operate any other business?
    bool owns_other_business = 6;
    
    // Question 4: If YES, list name and describe operations and percentage of ownership
    string other_business_details = 7;
    
    // Question 5: List and describe operations of all other business names and licenses active or inactive that applicant has used in the last five (5) years
    bool has_other_business_names = 8;
    
    // Question 5: Details of other business names and licenses
    string other_business_names_details = 9;
    
    // Question 6: Have you ever declared bankruptcy under this name or any other similar entity in which you have had a controlling interest?
    bool declared_bankruptcy = 10;
    
    // Question 6: If YES, provide name of each entity and the date and jurisdiction of bankruptcy
    string bankruptcy_details = 11;
    }

    message ApplicantTypes {
    // Construction Consultant
    bool construction_consultant = 1;
    
    // Subcontractor
    bool subcontractor = 2;
    
    // Construction Manager
    bool construction_manager = 3;
    
    // Spec Builder
    bool spec_builder = 4;
    
    // Developer
    bool developer = 5;
    
    // Architect/Engineer
    bool architect_engineer = 6;
    
    // General Contractor
    bool general_contractor = 7;
    
    // Surveyor
    bool surveyor = 8;
    }

    message HistoricalFinancials {
    // 5th Prior Year
    YearlyFinancials fifth_prior_year = 1;
    
    // 4th Prior Year
    YearlyFinancials fourth_prior_year = 2;
    
    // 3rd Prior Year
    YearlyFinancials third_prior_year = 3;
    
    // 2nd Prior Year
    YearlyFinancials second_prior_year = 4;
    
    // Current Year
    YearlyFinancials current_year = 5;
    
    // Projected Next 12 months
    YearlyFinancials projected_next_12_months = 6;
    }

    message YearlyFinancials {
    // Payroll amount
    string payroll = 1;
    
    // Receipts amount
    string receipts = 2;
    
    // Subcontractor Costs amount
    string subcontractor_costs = 3;
    }
    """

    answer_1 = json.dumps()

    messages = [
        {"role":"user", "content":system_prompt}
    ]

    return messages