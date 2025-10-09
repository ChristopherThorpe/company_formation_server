from flask import Flask, request, jsonify, send_file
from pydantic import BaseModel, Field, validator
from typing import Literal
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

def generate_massachusetts_articles(company_data: CompanyFormation) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Set up the document
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, "ARTICLES OF ORGANIZATION")
    c.setFont("Helvetica", 12)

    # Article I - Company Name
    c.drawString(50, 700, "ARTICLE I: The name of the corporation is:")
    c.drawString(70, 680, company_data.company_name)

    # Article II - Purpose
    c.drawString(50, 630, "ARTICLE II: The corporation is formed for the purpose of engaging in any lawful business")
    c.drawString(50, 610, "permitted under Massachusetts law.")

    # Article III - Principal Office
    c.drawString(50, 560, "ARTICLE III: The street address of the corporation's principal office is:")
    c.drawString(70, 540, "84 State Street")
    c.drawString(70, 520, "Boston, Massachusetts 02109")

    # Incorporator
    c.drawString(50, 200, f"IN WITNESS WHEREOF, the undersigned incorporator executes these Articles this {datetime.now().strftime('%d')} day of")
    c.drawString(50, 180, f"{datetime.now().strftime('%B, %Y')}.")

    c.drawString(50, 100, "Incorporator:")
    c.drawString(70, 80, company_data.incorporator_name)

    c.save()
    buffer.seek(0)
    return buffer

def generate_massachusetts_llc_certificate(company_data: CompanyFormation) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)

    # Set up the document
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(300, 750, "CERTIFICATE OF ORGANIZATION")
    c.setFont("Helvetica", 12)

    # Article I - Company Name
    c.drawString(50, 700, "ARTICLE I: The name of the limited liability company is:")
    c.drawString(70, 680, company_data.company_name)

    # Article II - General Character
    c.drawString(50, 630, "ARTICLE II: The general character of the business is to engage in any lawful business")
    c.drawString(50, 610, "for which a limited liability company may be organized under the laws of Massachusetts.")

    # Article III - Principal Office
    c.drawString(50, 560, "ARTICLE III: The street address of the office in the Commonwealth is:")
    c.drawString(70, 540, "84 State Street")
    c.drawString(70, 520, "Boston, Massachusetts 02109")

    # Execution
    c.drawString(50, 200, f"IN WITNESS WHEREOF, the undersigned signs this Certificate of Organization this {datetime.now().strftime('%d')} day of")
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
        elif company_data.state_of_formation == 'MA':
            if company_data.company_type == 'corporation':
                pdf_buffer = generate_massachusetts_articles(company_data)
            elif company_data.company_type == 'LLC':
                pdf_buffer = generate_massachusetts_llc_certificate(company_data)
            else:
                return jsonify({"error": "Unsupported company type"}), 400
        else:
            return jsonify({
                "error": "Only Delaware, California, and Massachusetts entities are supported at this time"
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
        },
        {
            "company_name": "Boston Tech Ventures, Inc.",
            "state_of_formation": "MA",
            "company_type": "corporation",
            "incorporator_name": "Avery Thompson"
        },
        {
            "company_name": "Mass Makers, LLC",
            "state_of_formation": "MA",
            "company_type": "LLC",
            "incorporator_name": "Jordan Riley"
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
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Company Formation</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            :root {{ --primary: #4f46e5; --primary-dark: #4338ca; --accent: #0ea5e9; --surface: rgba(255, 255, 255, 0.82); --text: #1f2933; --muted: #64748b; }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; }}
            body {{ font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; color: var(--text); background: linear-gradient(135deg, #eef2ff 0%, #f8fafc 100%); min-height: 100vh; position: relative; display: flex; justify-content: center; align-items: flex-start; padding: 48px 16px; }}
            body::before {{ content: ""; position: absolute; inset: 0; background-image: radial-gradient(circle at 20% 20%, rgba(79, 70, 229, 0.12) 0, rgba(79, 70, 229, 0) 60%), radial-gradient(circle at 80% 0, rgba(14, 165, 233, 0.1) 0, rgba(14, 165, 233, 0) 55%); z-index: 0; }}
            main {{ position: relative; z-index: 1; width: 100%; max-width: 720px; display: grid; gap: 32px; }}
            .hero {{ text-align: center; display: grid; gap: 12px; }}
            .hero h1 {{ font-size: 2.4rem; font-weight: 700; color: var(--primary-dark); letter-spacing: -0.02em; }}
            .hero p {{ color: var(--muted); font-size: 1.05rem; }}
            .card {{ background: var(--surface); backdrop-filter: blur(18px); border-radius: 28px; box-shadow: 0 24px 60px rgba(15, 23, 42, 0.12); padding: 32px; border: 1px solid rgba(79, 70, 229, 0.08); display: grid; gap: 24px; }}
            .card-header {{ display: flex; align-items: center; gap: 12px; }}
            .badge {{ background: rgba(79, 70, 229, 0.12); color: var(--primary-dark); padding: 6px 14px; border-radius: 999px; font-weight: 600; font-size: 0.85rem; letter-spacing: 0.02em; }}
            .card-header h2 {{ font-size: 1.45rem; font-weight: 600; color: var(--text); }}
            form {{ display: grid; gap: 20px; }}
            .field {{ display: grid; gap: 8px; }}
            label {{ font-weight: 600; font-size: 0.95rem; color: var(--text); letter-spacing: 0.01em; }}
            input, select {{ background: rgba(255, 255, 255, 0.92); border: 1px solid rgba(100, 116, 139, 0.3); border-radius: 16px; padding: 14px 16px; font-size: 1rem; transition: border-color 0.3s ease, box-shadow 0.3s ease, transform 0.3s ease; appearance: none; }}
            input:focus, select:focus {{ outline: none; border-color: var(--primary); box-shadow: 0 0 0 4px rgba(79, 70, 229, 0.1); transform: translateY(-1px); }}
            select {{ background-image: linear-gradient(45deg, transparent 50%, rgba(79, 70, 229, 0.45) 50%), linear-gradient(135deg, rgba(79, 70, 229, 0.45) 50%, transparent 50%), linear-gradient(to right, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.92)); background-position: calc(100% - 22px) calc(1.1em + 2px), calc(100% - 17px) calc(1.1em + 2px), calc(100% - 2.5em) 0.7em; background-size: 6px 6px, 6px 6px, 1px 1.6em; background-repeat: no-repeat; }}
            .field small {{ color: var(--muted); font-size: 0.85rem; }}
            .form-footer {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 12px; }}
            .helper {{ color: var(--muted); font-size: 0.9rem; display: flex; align-items: center; gap: 8px; }}
            .submit {{ background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%); color: #fff; border: none; border-radius: 18px; padding: 14px 28px; font-size: 1rem; font-weight: 600; cursor: pointer; letter-spacing: 0.02em; box-shadow: 0 18px 30px rgba(79, 70, 229, 0.26); transition: transform 0.3s ease, box-shadow 0.3s ease; display: inline-flex; align-items: center; gap: 8px; }}
            .submit:hover {{ transform: translateY(-2px); box-shadow: 0 22px 34px rgba(79, 70, 229, 0.28); }}
            .submit:active {{ transform: translateY(0); box-shadow: 0 12px 20px rgba(79, 70, 229, 0.24); }}
            .footer-note {{ text-align: center; color: var(--muted); font-size: 0.9rem; }}
            @media (max-width: 640px) {{
                body {{ padding: 32px 16px; }}
                .card {{ padding: 24px; border-radius: 22px; }}
                .hero h1 {{ font-size: 2rem; }}
                .form-footer {{ flex-direction: column; align-items: stretch; }}
                .submit {{ width: 100%; justify-content: center; }}
            }}
        </style>
    </head>
    <body>
        <main>
            <section class="hero">
                <span class="badge">Fast-track filing</span>
                <h1>Launch your company paperwork in minutes</h1>
                <p>Fill in a few details and download a ready-to-file certificate tailored to Delaware, California, or Massachusetts.</p>
            </section>
            <section class="card">
                <header class="card-header">
                    <div>
                        <h2>Formation details</h2>
                        <p class="helper">We'll use this information to generate a compliant certificate for your chosen state.</p>
                    </div>
                </header>
                <form action="/form-company" method="POST">
                    <div class="field">
                        <label for="company_name">Company Name</label>
                        <input type="text" id="company_name" name="company_name" placeholder="e.g. Horizon Labs, Inc." required>
                        <small>Include entity suffixes like "Inc." or "LLC" if applicable.</small>
                    </div>
                    <div class="field">
                        <label for="state_of_formation">State of Formation</label>
                        <select id="state_of_formation" name="state_of_formation" required>
                            <option value="">Select a state</option>
                            {"".join(f'<option value="{state}">{state}</option>' for state in states)}
                        </select>
                        <small>Currently supporting Delaware, California, and Massachusetts filings.</small>
                    </div>
                    <div class="field">
                        <label for="company_type">Company Type</label>
                        <select id="company_type" name="company_type" required>
                            <option value="">Select a type</option>
                            <option value="corporation">Corporation</option>
                            <option value="LLC">LLC</option>
                        </select>
                    </div>
                    <div class="field">
                        <label for="incorporator_name">Incorporator Name</label>
                        <input type="text" id="incorporator_name" name="incorporator_name" placeholder="Your full legal name" required>
                    </div>
                    <div class="form-footer">
                        <div class="helper">💡 Tip: Downloaded PDFs are ready for signature and filing.</div>
                        <button class="submit" type="submit">Generate formation PDF</button>
                    </div>
                </form>
            </section>
            <p class="footer-note">Prefer APIs? Explore the <a href="/form-company-schema" style="color: var(--accent); font-weight: 600; text-decoration: none;">JSON schema</a> for automated filings.</p>
        </main>
    </body>
    </html>
    '''

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, port=port)
