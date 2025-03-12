from flask import Flask, request, jsonify, send_file
from pydantic import BaseModel, Field, validator
from typing import Literal, List
import re
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from datetime import datetime
import os

app = Flask(__name__)

class CompanyFormation(BaseModel):
    company_name: str = Field(..., description="Company name")
    state_of_formation: str = Field(..., description="US state or territory")
    company_type: Literal["corporation", "LLC"] = Field(..., description="Type of company")
    incorporator_name: str = Field(..., description="Name of incorporator")

class BylawsRequest(BaseModel):
    company_name: str = Field(..., description="Company name")
    principal_office: str = Field(..., description="Principal office address")
    fiscal_year_end: str = Field(..., description="End of fiscal year (MM-DD)")
    board_size: int = Field(..., description="Number of directors on the board", ge=1)
    officer_titles: List[str] = Field(..., description="List of officer positions")
    annual_meeting_month: str = Field(..., description="Month for annual shareholder meeting")
    quorum_percentage: int = Field(..., description="Percentage of shareholders needed for quorum", ge=0, le=100)

    @validator('fiscal_year_end')
    def validate_fiscal_year_end(cls, v):
        if not re.match(r'^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$', v):
            raise ValueError('Fiscal year end must be in MM-DD format')
        return v

    @validator('annual_meeting_month')
    def validate_annual_meeting_month(cls, v):
        months = ['January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
        if v not in months:
            raise ValueError('Annual meeting month must be a valid month name')
        return v

    @validator('company_name')
    def validate_company_name(cls, v):
        if not re.match(r'^[a-zA-Z0-9\s,\.\'&]+$', v):
            raise ValueError('Company name can only contain alphanumeric characters, spaces, commas, periods, apostrophes, and ampersands')
        return v

    @validator('state_of_formation')
    def validate_state(cls, v):
        states = {
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
            'DC', 'PR', 'GU', 'VI', 'AS', 'MP'
        }
        if v.upper() not in states:
            raise ValueError('Invalid US state or territory')
        return v.upper()

def generate_delaware_articles(company_data: CompanyFormation) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Set up the document
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, "CERTIFICATE OF INCORPORATION")
    c.setFont("Helvetica", 12)
    
    # Article First - Company Name
    c.drawString(50, 700, "FIRST: The name of this corporation is:")
    c.drawString(70, 680, company_data.company_name)
    
    # Article Second - Registered Office
    c.drawString(50, 630, "SECOND: Its registered office in the State of Delaware is located at:")
    c.drawString(70, 610, "251 Little Falls Drive, Wilmington, New Castle County, Delaware 19808")
    
    # Article Third - Purpose
    c.drawString(50, 560, "THIRD: The purpose of the corporation is to engage in any lawful act or activity for")
    c.drawString(50, 540, "which corporations may be organized under the General Corporation Law of Delaware.")
    
    # Article Fourth - Authorized Shares
    c.drawString(50, 490, "FOURTH: The total number of shares of stock which this corporation is authorized")
    c.drawString(50, 470, "to issue is 1,000 shares of Common Stock with $0.01 par value per share.")
    
    # Incorporator
    c.drawString(50, 200, f"IN WITNESS WHEREOF, the undersigned, being the incorporator hereinbefore named,")
    c.drawString(50, 180, f"has executed this Certificate of Incorporation this {datetime.now().strftime('%d')} day of")
    c.drawString(50, 160, f"{datetime.now().strftime('%B, %Y')}.")
    
    c.drawString(50, 100, "Incorporator:")
    c.drawString(70, 80, company_data.incorporator_name)
    
    c.save()
    buffer.seek(0)
    return buffer

def generate_delaware_llc_certificate(company_data: CompanyFormation) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Set up the document
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, "CERTIFICATE OF FORMATION")
    c.setFont("Helvetica", 12)
    
    # Article First - Company Name
    c.drawString(50, 700, "FIRST: The name of the limited liability company is:")
    c.drawString(70, 680, company_data.company_name)
    
    # Article Second - Registered Office
    c.drawString(50, 630, "SECOND: The address of its registered office in the State of Delaware is:")
    c.drawString(70, 610, "251 Little Falls Drive, Wilmington, New Castle County, Delaware 19808")
    
    # Article Third - Registered Agent
    c.drawString(50, 560, "THIRD: The name and address of its registered agent in the State of Delaware is:")
    c.drawString(70, 540, "Corporation Service Company")
    c.drawString(70, 520, "251 Little Falls Drive")
    c.drawString(70, 500, "Wilmington, DE 19808")
    
    # Article Fourth - Management
    c.drawString(50, 450, "FOURTH: The limited liability company shall be managed by its members.")
    
    # Execution
    c.drawString(50, 200, f"IN WITNESS WHEREOF, the undersigned has executed this Certificate of Formation this {datetime.now().strftime('%d')} day of")
    c.drawString(50, 180, f"{datetime.now().strftime('%B, %Y')}.")
    
    c.drawString(50, 100, "Authorized Person:")
    c.drawString(70, 80, company_data.incorporator_name)
    
    c.save()
    buffer.seek(0)
    return buffer

def generate_california_articles(company_data: CompanyFormation) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Set up the document
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, "ARTICLES OF INCORPORATION")
    c.setFont("Helvetica", 12)
    
    # Article I - Company Name
    c.drawString(50, 700, "ARTICLE I: The name of this corporation is:")
    c.drawString(70, 680, company_data.company_name)
    
    # Article II - Purpose
    c.drawString(50, 630, "ARTICLE II: The purpose of the corporation is to engage in any lawful act or activity")
    c.drawString(50, 610, "for which a corporation may be organized under the General Corporation Law of California.")
    
    # Article III - Agent for Service
    c.drawString(50, 560, "ARTICLE III: The name and address in California of the corporation's initial agent for service of process is:")
    c.drawString(70, 540, "California Registered Agent, Inc.")
    c.drawString(70, 520, "123 Main Street")
    c.drawString(70, 500, "Los Angeles, CA 90001")
    
    # Incorporator
    c.drawString(50, 200, f"IN WITNESS WHEREOF, the undersigned, being the incorporator hereinbefore named,")
    c.drawString(50, 180, f"has executed these Articles of Incorporation this {datetime.now().strftime('%d')} day of")
    c.drawString(50, 160, f"{datetime.now().strftime('%B, %Y')}.")
    
    c.drawString(50, 100, "Incorporator:")
    c.drawString(70, 80, company_data.incorporator_name)
    
    c.save()
    buffer.seek(0)
    return buffer

def generate_california_llc_certificate(company_data: CompanyFormation) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Set up the document
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, "ARTICLES OF ORGANIZATION")
    c.setFont("Helvetica", 12)
    
    # Article I - Company Name
    c.drawString(50, 700, "ARTICLE I: The name of the limited liability company is:")
    c.drawString(70, 680, company_data.company_name)
    
    # Article II - Purpose
    c.drawString(50, 630, "ARTICLE II: The purpose of the limited liability company is to engage in any lawful business.")
    
    # Article III - Agent for Service
    c.drawString(50, 560, "ARTICLE III: The name and address in California of the LLC's initial agent for service of process is:")
    c.drawString(70, 540, "California Registered Agent, Inc.")
    c.drawString(70, 520, "123 Main Street")
    c.drawString(70, 500, "Los Angeles, CA 90001")
    
    # Execution
    c.drawString(50, 200, f"IN WITNESS WHEREOF, the undersigned has executed these Articles of Organization this {datetime.now().strftime('%d')} day of")
    c.drawString(50, 180, f"{datetime.now().strftime('%B, %Y')}.")
    
    c.drawString(50, 100, "Authorized Person:")
    c.drawString(70, 80, company_data.incorporator_name)
    
    c.save()
    buffer.seek(0)
    return buffer

@app.route('/form-company', methods=['POST'])
def form_company():
    try:
        # Handle both JSON and form data
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                "company_name": request.form.get("company_name"),
                "state_of_formation": request.form.get("state_of_formation"),
                "company_type": request.form.get("company_type"),
                "incorporator_name": request.form.get("incorporator_name")
            }
        
        company_data = CompanyFormation(**data)
        
        if company_data.state_of_formation == 'DE':
            if company_data.company_type == 'corporation':
                pdf_buffer = generate_delaware_articles(company_data)
            elif company_data.company_type == 'LLC':
                pdf_buffer = generate_delaware_llc_certificate(company_data)
            else:
                return jsonify({"error": "Unsupported company type"}), 400
        elif company_data.state_of_formation == 'CA':
            if company_data.company_type == 'corporation':
                pdf_buffer = generate_california_articles(company_data)
            elif company_data.company_type == 'LLC':
                pdf_buffer = generate_california_llc_certificate(company_data)
            else:
                return jsonify({"error": "Unsupported company type"}), 400
        else:
            return jsonify({
                "error": "Only Delaware and California entities are supported at this time"
            }), 400
    
        return send_file(
            pdf_buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"{company_data.company_name}_certificate.pdf"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/form-company-schema', methods=['GET'])
def form_company_schema():
    examples = [
        {
            "company_name": "Acme Corp, Inc.",
            "state_of_formation": "DE",
            "company_type": "corporation",
            "incorporator_name": "John Smith"
        },
        {
            "company_name": "Smith & Sons, LLC",
            "state_of_formation": "DE",
            "company_type": "LLC",
            "incorporator_name": "Jane Doe"
        },
        {
            "company_name": "Tech Innovators Co.",
            "state_of_formation": "CA",
            "company_type": "corporation",
            "incorporator_name": "Michael Johnson"
        },
        {
            "company_name": "California Dreaming, LLC",
            "state_of_formation": "CA",
            "company_type": "LLC",
            "incorporator_name": "Emily Chen"
        }
    ]
    return jsonify(examples)

@app.route('/', methods=['GET'])
def company_form():
    states = [
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
        'DC', 'PR', 'GU', 'VI', 'AS', 'MP'
    ]
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Company Formation</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }}
            form {{ display: grid; gap: 15px; }}
            label {{ font-weight: bold; }}
            input, select {{ padding: 8px; font-size: 16px; }}
            button {{ background: #007bff; color: white; border: none; padding: 10px 20px; cursor: pointer; }}
            button:hover {{ background: #0056b3; }}
        </style>
    </head>
    <body>
        <h1>Company Formation</h1>
        <form action="/form-company" method="POST">
            <label for="company_name">Company Name:</label>
            <input type="text" id="company_name" name="company_name" required>
            
            <label for="state_of_formation">State of Formation:</label>
            <select id="state_of_formation" name="state_of_formation" required>
                <option value="">Select a state</option>
                {"".join(f'<option value="{state}">{state}</option>' for state in states)}
            </select>
            
            <label for="company_type">Company Type:</label>
            <select id="company_type" name="company_type" required>
                <option value="">Select a type</option>
                <option value="corporation">Corporation</option>
                <option value="LLC">LLC</option>
            </select>
            
            <label for="incorporator_name">Incorporator Name:</label>
            <input type="text" id="incorporator_name" name="incorporator_name" required>
            
            <button type="submit">Submit</button>
        </form>
    </body>
    </html>
    '''

def generate_bylaws(bylaws_data: BylawsRequest) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, "CORPORATE BYLAWS OF")
    c.drawCentredString(300, 730, bylaws_data.company_name.upper())
    
    # Article I - Offices
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 680, "ARTICLE I - OFFICES")
    c.setFont("Helvetica", 12)
    c.drawString(50, 660, "The principal office of the corporation shall be located at:")
    c.drawString(70, 640, bylaws_data.principal_office)
    
    # Article II - Shareholders Meetings
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 600, "ARTICLE II - SHAREHOLDERS MEETINGS")
    c.setFont("Helvetica", 12)
    c.drawString(50, 580, f"1. Annual Meeting. The annual meeting of shareholders shall be held in")
    c.drawString(70, 560, f"{bylaws_data.annual_meeting_month} of each year.")
    c.drawString(50, 540, f"2. Quorum. {bylaws_data.quorum_percentage}% of the outstanding shares shall constitute")
    c.drawString(70, 520, "a quorum for the transaction of business.")
    
    # Article III - Board of Directors
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 480, "ARTICLE III - BOARD OF DIRECTORS")
    c.setFont("Helvetica", 12)
    c.drawString(50, 460, f"1. Number. The Board of Directors shall consist of {bylaws_data.board_size}")
    c.drawString(70, 440, "director(s).")
    
    # Article IV - Officers
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 400, "ARTICLE IV - OFFICERS")
    c.setFont("Helvetica", 12)
    c.drawString(50, 380, "1. Officers. The officers of the corporation shall be:")
    y = 360
    for title in bylaws_data.officer_titles:
        c.drawString(70, y, f"- {title}")
        y -= 20
    
    # Article V - Fiscal Year
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y-20, "ARTICLE V - FISCAL YEAR")
    c.setFont("Helvetica", 12)
    c.drawString(50, y-40, f"The fiscal year of the corporation shall end on {bylaws_data.fiscal_year_end}")
    c.drawString(50, y-60, "of each year.")
    
    c.save()
    buffer.seek(0)
    return buffer

@app.route('/generate-bylaws', methods=['POST'])
def generate_company_bylaws():
    try:
        data = request.get_json()
        bylaws_data = BylawsRequest(**data)
        pdf_buffer = generate_bylaws(bylaws_data)
        
        return send_file(
            pdf_buffer,
            download_name=f"{bylaws_data.company_name.replace(' ', '_')}_bylaws.pdf",
            mimetype='application/pdf'
        )
    except ValidationError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, port=port)
