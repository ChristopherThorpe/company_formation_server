import pytest
from app import (
    CompanyFormation, BylawsRequest, generate_delaware_articles,
    generate_california_articles, generate_california_llc_certificate,
    generate_bylaws
)
from pydantic import ValidationError
from PyPDF2 import PdfReader
import io

# Test data
VALID_STATES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    'DC', 'PR', 'GU', 'VI', 'AS', 'MP'
]

def test_state_validation():
    # Test all valid states
    for state in VALID_STATES:
        data = {
            "company_name": "Test Company",
            "state_of_formation": state,
            "company_type": "corporation",
            "incorporator_name": "Test User"
        }
        company = CompanyFormation(**data)
        assert company.state_of_formation == state.upper()

    # Test invalid state
    with pytest.raises(ValidationError):
        data = {
            "company_name": "Test Company",
            "state_of_formation": "XX",
            "company_type": "corporation",
            "incorporator_name": "Test User"
        }
        CompanyFormation(**data)

def test_pdf_generation():
    # Test data
    test_data = {
        "company_name": "Basic Test Company",
        "state_of_formation": "DE",
        "company_type": "corporation",
        "incorporator_name": "Testy McTestface"
    }
    
    # Generate PDF
    pdf_buffer = generate_delaware_articles(CompanyFormation(**test_data))
    pdf_buffer.seek(0)
    
    # Read PDF content
    reader = PdfReader(pdf_buffer)
    text = "\n".join(page.extract_text() for page in reader.pages)
    
    # Verify key content
    assert "Basic Test Company" in text
    assert "Testy McTestface" in text
    assert "CERTIFICATE OF INCORPORATION" in text
    assert "FIRST: The name of this corporation is:" in text
    assert "SECOND: Its registered office in the State of Delaware" in text
    assert "THIRD: The purpose of the corporation is to engage" in text
    assert "FOURTH: The total number of shares of stock" in text
    assert "IN WITNESS WHEREOF, the undersigned" in text

def test_california_corporation_pdf():
    test_data = {
        "company_name": "California Test Corp",
        "state_of_formation": "CA",
        "company_type": "corporation",
        "incorporator_name": "Testy McTestface"
    }
    
    pdf_buffer = generate_california_articles(CompanyFormation(**test_data))
    pdf_buffer.seek(0)
    
    reader = PdfReader(pdf_buffer)
    text = "\n".join(page.extract_text() for page in reader.pages)
    
    assert "California Test Corp" in text
    assert "ARTICLES OF INCORPORATION" in text
    assert "ARTICLE I: The name of this corporation is:" in text
    assert "ARTICLE II: The purpose of the corporation" in text
    assert "ARTICLE III: The name and address in California" in text

def test_california_llc_pdf():
    test_data = {
        "company_name": "California Test LLC",
        "state_of_formation": "CA",
        "company_type": "LLC",
        "incorporator_name": "Testy McTestface"
    }
    
    pdf_buffer = generate_california_llc_certificate(CompanyFormation(**test_data))
    pdf_buffer.seek(0)
    
    reader = PdfReader(pdf_buffer)
    text = "\n".join(page.extract_text() for page in reader.pages)
    
    assert "California Test LLC" in text
    assert "ARTICLES OF ORGANIZATION" in text

# Test data for bylaws tests
VALID_BYLAWS_DATA = {
    "company_name": "Test Corporation",
    "principal_office": "123 Main St, Suite 100, San Francisco, CA 94105",
    "fiscal_year_end": "12-31",
    "board_size": 5,
    "officer_titles": ["Chief Executive Officer", "Secretary", "Treasurer"],
    "annual_meeting_month": "June",
    "quorum_percentage": 51
}

def test_bylaws_request_validation():
    # Test valid data
    bylaws = BylawsRequest(**VALID_BYLAWS_DATA)
    assert bylaws.company_name == "Test Corporation"
    assert bylaws.board_size == 5
    assert len(bylaws.officer_titles) == 3

    # Test invalid fiscal year end
    invalid_date_data = VALID_BYLAWS_DATA.copy()
    invalid_date_data["fiscal_year_end"] = "13-31"
    with pytest.raises(ValidationError):
        BylawsRequest(**invalid_date_data)

    # Test invalid month
    invalid_month_data = VALID_BYLAWS_DATA.copy()
    invalid_month_data["annual_meeting_month"] = "InvalidMonth"
    with pytest.raises(ValidationError):
        BylawsRequest(**invalid_month_data)

    # Test invalid board size
    invalid_board_data = VALID_BYLAWS_DATA.copy()
    invalid_board_data["board_size"] = 0
    with pytest.raises(ValidationError):
        BylawsRequest(**invalid_board_data)

    # Test invalid quorum percentage
    invalid_quorum_data = VALID_BYLAWS_DATA.copy()
    invalid_quorum_data["quorum_percentage"] = 101
    with pytest.raises(ValidationError):
        BylawsRequest(**invalid_quorum_data)

def test_bylaws_pdf_generation():
    bylaws_data = BylawsRequest(**VALID_BYLAWS_DATA)
    pdf_buffer = generate_bylaws(bylaws_data)
    pdf_buffer.seek(0)
    
    reader = PdfReader(pdf_buffer)
    text = "\n".join(page.extract_text() for page in reader.pages)
    
    # Test presence of company information
    assert "Test Corporation" in text
    assert "123 Main St, Suite 100, San Francisco, CA 94105" in text
    
    # Test presence of all articles
    assert "ARTICLE I - OFFICES" in text
    assert "ARTICLE II - SHAREHOLDERS MEETINGS" in text
    assert "ARTICLE III - BOARD OF DIRECTORS" in text
    assert "ARTICLE IV - OFFICERS" in text
    assert "ARTICLE V - FISCAL YEAR" in text
    
    # Test specific content
    assert "June of each year" in text
    assert "51% of the outstanding shares" in text
    assert "Board of Directors shall consist of 5" in text
    assert "Chief Executive Officer" in text
    assert "Secretary" in text
    assert "Treasurer" in text
    assert "12-31" in text

def test_bylaws_edge_cases():
    # Test minimum valid configuration
    min_data = {
        "company_name": "Minimal Corp",
        "principal_office": "1 Main St",
        "fiscal_year_end": "01-01",
        "board_size": 1,
        "officer_titles": ["President"],
        "annual_meeting_month": "January",
        "quorum_percentage": 0
    }
    bylaws = BylawsRequest(**min_data)
    pdf_buffer = generate_bylaws(bylaws)
    pdf_buffer.seek(0)
    
    reader = PdfReader(pdf_buffer)
    text = "\n".join(page.extract_text() for page in reader.pages)
    
    assert "Minimal Corp" in text
    assert "1 Main St" in text
    assert "Board of Directors shall consist of 1" in text
    
    # Test maximum configuration
    max_data = {
        "company_name": "Maximal Corp",
        "principal_office": "Very Long Address, Suite 1000000, Maximum City, Maximum State, 99999",
        "fiscal_year_end": "12-31",
        "board_size": 99,
        "officer_titles": [f"Officer {i}" for i in range(20)],
        "annual_meeting_month": "December",
        "quorum_percentage": 100
    }
    bylaws = BylawsRequest(**max_data)
    pdf_buffer = generate_bylaws(bylaws)
    pdf_buffer.seek(0)
    
    reader = PdfReader(pdf_buffer)
    text = "\n".join(page.extract_text() for page in reader.pages)
    
    assert "Maximal Corp" in text
    assert "Board of Directors shall consist of 99" in text
    assert "100% of the outstanding shares" in text
    assert "ARTICLE I: The name of the limited liability company is:" in text
    assert "ARTICLE II: The purpose of the limited liability company" in text
    assert "ARTICLE III: The name and address in California" in text
