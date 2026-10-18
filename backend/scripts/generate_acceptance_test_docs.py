"""
Generate test documents for final manual acceptance testing in sample_documents/
"""
import os
import docx
from docx.shared import Pt, Inches, RGBColor

sample_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sample_documents")
os.makedirs(sample_dir, exist_ok=True)

def create_employment_agreement():
    doc = docx.Document()
    doc.add_heading("EMPLOYMENT AGREEMENT", level=1)
    
    p = doc.add_paragraph()
    p.add_run("This Employment Agreement (the \"Agreement\") is made and entered into on this ")
    p.add_run("1st day of April, 2026").bold = True
    p.add_run(", at Bengaluru, Karnataka, India.")
    
    doc.add_heading("PARTIES", level=2)
    doc.add_paragraph(
        "BETWEEN:\n"
        "Meridian Technologies Pvt. Ltd., a company incorporated under the Companies Act, 2013, "
        "having its registered corporate office at Electronic City, Phase 1, Bengaluru, Karnataka, 560100 "
        "(hereinafter referred to as the \"Company\" or \"Employer\");\n\n"
        "AND:\n"
        "Priya Sharma, residing at Indiranagar, Bengaluru, Karnataka, 560038 "
        "(hereinafter referred to as the \"Employee\")."
    )
    
    doc.add_heading("1. APPOINTMENT AND TERM", level=2)
    doc.add_paragraph(
        "The Company hereby employs the Employee as Senior Software Architect. The effective commencement "
        "date of employment shall be 1 April 2026, and the term of this employment shall continue until "
        "31 March 2027, unless terminated earlier in accordance with Clause 5 of this Agreement."
    )
    
    doc.add_heading("2. COMPENSATION AND SALARY PAYMENT", level=2)
    doc.add_paragraph(
        "The Company shall pay the Employee a monthly gross salary of INR 65,000 (Rupees Sixty Five Thousand only) "
        "payable on or before the last working day of each calendar month. The Company shall deduct applicable "
        "income tax and statutory contributions in accordance with the Income Tax Act, 1961."
    )
    
    doc.add_heading("3. DUTIES AND RESPONSIBILITIES", level=2)
    doc.add_paragraph(
        "The Employee shall perform all duties faithfully and diligently. The Employee shall devote full business time "
        "and attention to the business affairs of the Company and shall not engage in any conflicting commercial activities."
    )
    
    doc.add_heading("4. CONFIDENTIALITY AND NON-DISCLOSURE", level=2)
    doc.add_paragraph(
        "The Employee acknowledges that during the employment, the Employee will have access to confidential proprietary "
        "information, trade secrets, software source code, customer records, and technical architecture. "
        "The Employee shall keep all Confidential Information strictly confidential and shall not disclose, copy, "
        "or distribute any proprietary data without prior written authorization from the Company. "
        "This confidentiality obligation shall survive the termination of employment."
    )
    
    doc.add_heading("5. INTELLECTUAL PROPERTY RIGHTS", level=2)
    doc.add_paragraph(
        "All inventions, software codes, algorithms, documentation, designs, and patentable works developed by the "
        "Employee during the course of employment shall be the sole and exclusive intellectual property of the Company. "
        "The Employee hereby assigns all worldwide intellectual property rights and patents to Meridian Technologies Pvt. Ltd."
    )
    
    doc.add_heading("6. TERMINATION AND NOTICE PERIOD", level=2)
    doc.add_paragraph(
        "Either party may terminate this Agreement by giving thirty (30) days prior written notice to the other party, "
        "or by payment of salary in lieu of such thirty (30) days notice. The Company reserves the right to terminate "
        "employment immediately for cause in cases of gross misconduct, fraud, or material breach of confidentiality."
    )
    
    doc.add_heading("7. DISPUTE RESOLUTION AND ARBITRATION", level=2)
    doc.add_paragraph(
        "All disputes or claims arising under this Agreement shall be referred to and resolved by arbitration administered "
        "under the Arbitration and Conciliation Act, 1996, before a sole arbitrator appointed by mutual consent."
    )
    
    doc.add_heading("8. GOVERNING LAW AND JURISDICTION", level=2)
    doc.add_paragraph(
        "This Agreement shall be governed by and construed in accordance with the substantive laws of India. "
        "The civil courts at Bengaluru, Karnataka shall have exclusive supervisory jurisdiction over all legal proceedings."
    )
    
    p_sign = doc.add_paragraph()
    p_sign.add_run("\nIN WITNESS WHEREOF, the parties hereto have signed this Agreement.\n\n")
    p_sign.add_run("For Meridian Technologies Pvt. Ltd.             Priya Sharma\n")
    p_sign.add_run("Authorized Signatory                            Employee Signatory")
    
    out_path = os.path.join(sample_dir, "01_Employment_Agreement.docx")
    doc.save(out_path)
    print(f"Created {out_path}")

def create_nda():
    doc = docx.Document()
    doc.add_heading("MUTUAL NON-DISCLOSURE AND CONFIDENTIALITY AGREEMENT", level=1)
    
    p = doc.add_paragraph()
    p.add_run("This Mutual Non-Disclosure Agreement (the \"Agreement\") is executed on this ")
    p.add_run("15th day of May, 2026").bold = True
    p.add_run(", at Hyderabad, Telangana, India.")
    
    doc.add_heading("BY AND BETWEEN", level=2)
    doc.add_paragraph(
        "Nova Labs Pvt. Ltd., a private limited company incorporated under the Companies Act, 2013, "
        "having its corporate registered office at Hitec City, Hyderabad, Telangana, 500081 "
        "(hereinafter referred to as the \"Disclosing Party\");\n\n"
        "AND:\n"
        "Orbit Systems LLP, a limited liability partnership registered under the Limited Liability Partnership Act, 2008, "
        "having its principal office at Whitefield, Bengaluru, Karnataka, 560066 "
        "(hereinafter referred to as the \"Receiving Party\")."
    )
    
    doc.add_heading("1. DEFINITION OF CONFIDENTIAL INFORMATION", level=2)
    doc.add_paragraph(
        "Confidential Information includes all technical, business, financial, software, source code, trade secrets, "
        "and client data disclosed by either party, whether in oral, written, magnetic, or electronic format. "
        "Information shall be protected whether marked proprietary or reasonably understood to be confidential."
    )
    
    doc.add_heading("2. NON-DISCLOSURE AND NON-USE OBLIGATIONS", level=2)
    doc.add_paragraph(
        "The Receiving Party shall maintain all Confidential Information in strict confidence using the highest standard "
        "of care. The Receiving Party shall not disclose, publish, or disseminate any proprietary data to any third party "
        "without the prior written consent of the Disclosing Party. The Receiving Party shall limit access solely to its "
        "key employees with a strict need-to-know."
    )
    
    doc.add_heading("3. DURATION AND TERM OF CONFIDENTIALITY", level=2)
    doc.add_paragraph(
        "This Agreement and all obligations of confidentiality herein shall remain in full force and effect for a period of "
        "three (3) years from the effective date of execution."
    )
    
    doc.add_heading("4. RETURN OR DESTRUCTION OF CONFIDENTIAL MATERIAL", level=2)
    doc.add_paragraph(
        "Upon written demand by the Disclosing Party or upon expiration of discussions, the Receiving Party shall, within "
        "ten (10) days, return or certify the permanent destruction of all original and copied confidential documents, "
        "electronic files, summaries, notes, and backup media."
    )
    
    doc.add_heading("5. REMEDIES AND INJUNCTIVE RELIEF", level=2)
    doc.add_paragraph(
        "Both parties acknowledge that unauthorized disclosure causes irreparable harm for which monetary damages alone "
        "would be inadequate. Accordingly, the Disclosing Party shall be entitled to seek immediate injunctive relief and "
        "restraining orders from any court of competent jurisdiction."
    )
    
    doc.add_heading("6. GOVERNING LAW AND JURISDICTION", level=2)
    doc.add_paragraph(
        "This Agreement shall be construed and governed in accordance with the laws of India. The courts at Bengaluru, "
        "Karnataka shall have exclusive jurisdiction over any disputes arising under or relating to this Agreement."
    )
    
    p_sign = doc.add_paragraph()
    p_sign.add_run("\nFor Nova Labs Pvt. Ltd.                         For Orbit Systems LLP\n")
    p_sign.add_run("Authorized Director                             Designated Partner")
    
    out_path = os.path.join(sample_dir, "02_Confidentiality_NDA.docx")
    doc.save(out_path)
    print(f"Created {out_path}")

def create_service_agreement_v1():
    doc = docx.Document()
    doc.add_heading("MASTER PROFESSIONAL SERVICES AGREEMENT (VERSION 1.0)", level=1)
    
    p = doc.add_paragraph()
    p.add_run("This Master Services Agreement is entered into on ")
    p.add_run("10th January 2026").bold = True
    p.add_run(", at Mumbai, Maharashtra, India.")
    
    doc.add_heading("PARTIES", level=2)
    doc.add_paragraph(
        "BETWEEN:\n"
        "Apex Digital Solutions Pvt. Ltd., having its principal office at Nariman Point, Mumbai (the \"Service Provider\");\n\n"
        "AND:\n"
        "Horizon Retail Enterprises, having its corporate office at Connaught Place, New Delhi (the \"Client\")."
    )
    
    doc.add_heading("1. SCOPE OF SERVICES", level=2)
    doc.add_paragraph(
        "The Service Provider shall deliver software engineering, enterprise cloud migration, and IT consulting services."
    )
    
    doc.add_heading("2. SERVICE FEES AND BILLING", level=2)
    doc.add_paragraph(
        "The Client shall pay the Service Provider a recurring service fee of INR 120,000 per month. "
        "Invoices shall be rendered at the end of each monthly billing cycle."
    )
    
    doc.add_heading("3. PAYMENT PERIOD", level=2)
    doc.add_paragraph(
        "The Client shall remit payment within thirty (30) days from the invoice issuance date."
    )
    
    doc.add_heading("4. CONTRACT TERM", level=2)
    doc.add_paragraph(
        "This Agreement shall remain valid for an initial term of one (1) year. There shall be no automatic renewal."
    )
    
    doc.add_heading("5. TERMINATION NOTICE", level=2)
    doc.add_paragraph(
        "Either party may terminate this Agreement by providing thirty (30) days advance written notice."
    )
    
    doc.add_heading("6. DEFAULT AND TERMINATION CONDITION", level=2)
    doc.add_paragraph(
        "Either party may immediately terminate this contract if the other party breaches any obligation under this Agreement."
    )
    
    doc.add_heading("7. LIMITATION OF LIABILITY", level=2)
    doc.add_paragraph(
        "The total aggregate liability of either party under this Agreement shall be capped at INR 500,000."
    )
    
    doc.add_heading("8. GOVERNING LAW", level=2)
    doc.add_paragraph(
        "This Agreement shall be governed by the laws of India, subject to the jurisdiction of the High Court of Bombay."
    )
    
    out_path = os.path.join(sample_dir, "03_Service_Agreement_V1.docx")
    doc.save(out_path)
    print(f"Created {out_path}")

def create_service_agreement_v2():
    doc = docx.Document()
    doc.add_heading("MASTER PROFESSIONAL SERVICES AGREEMENT (VERSION 2.0)", level=1)
    
    p = doc.add_paragraph()
    p.add_run("This Master Services Agreement is entered into on ")
    p.add_run("10th January 2026 (Revised)").bold = True
    p.add_run(", at Mumbai, Maharashtra, India.")
    
    doc.add_heading("PARTIES", level=2)
    doc.add_paragraph(
        "BETWEEN:\n"
        "Apex Digital Solutions Pvt. Ltd., having its principal office at Nariman Point, Mumbai (the \"Service Provider\");\n\n"
        "AND:\n"
        "Horizon Retail Enterprises, having its corporate office at Connaught Place, New Delhi (the \"Client\")."
    )
    
    doc.add_heading("1. SCOPE OF SERVICES", level=2)
    doc.add_paragraph(
        "The Service Provider shall deliver software engineering, enterprise cloud migration, and IT consulting services."
    )
    
    doc.add_heading("2. SERVICE FEES AND BILLING", level=2)
    doc.add_paragraph(
        "The Client shall pay the Service Provider a revised recurring service fee of INR 145,000 per month. "
        "Invoices shall be rendered at the end of each monthly billing cycle."
    )
    
    doc.add_heading("3. PAYMENT PERIOD", level=2)
    doc.add_paragraph(
        "The Client shall remit payment within fifteen (15) days from the invoice issuance date."
    )
    
    doc.add_heading("4. CONTRACT TERM AND AUTOMATIC RENEWAL", level=2)
    doc.add_paragraph(
        "This Agreement shall remain valid for an initial term of one (1) year. Upon expiration of the initial term, "
        "this Agreement shall be subject to automatic six (6) month renewal terms unless written notice is given."
    )
    
    doc.add_heading("5. TERMINATION NOTICE", level=2)
    doc.add_paragraph(
        "Either party may terminate this Agreement by providing sixty (60) days advance written notice."
    )
    
    doc.add_heading("6. DEFAULT AND MATERIAL BREACH CURE MECHANISM", level=2)
    doc.add_paragraph(
        "In the event of an alleged material breach, the non-breaching party must provide written notice detailing the breach. "
        "The breaching party shall have a cure period of thirty (30) days to remedy such material breach before termination takes effect."
    )
    
    doc.add_heading("7. LIMITATION OF LIABILITY", level=2)
    doc.add_paragraph(
        "The total aggregate liability of either party under this Agreement shall be capped at INR 750,000."
    )
    
    doc.add_heading("8. GOVERNING LAW", level=2)
    doc.add_paragraph(
        "This Agreement shall be governed by the laws of India, subject to the jurisdiction of the High Court of Bombay."
    )
    
    out_path = os.path.join(sample_dir, "04_Service_Agreement_V2.docx")
    doc.save(out_path)
    print(f"Created {out_path}")

if __name__ == "__main__":
    create_employment_agreement()
    create_nda()
    create_service_agreement_v1()
    create_service_agreement_v2()
    print("All 4 sample test documents created successfully.")
