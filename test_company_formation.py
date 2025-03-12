import pytest
from app import CompanyFormation, generate_delaware_articles, generate_california_articles, generate_california_llc_certificate
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
    assert "ARTICLE I: The name of the limited liability company is:" in text
    assert "ARTICLE II: The purpose of the limited liability company" in text
    assert "ARTICLE III: The name and address in California" in text
