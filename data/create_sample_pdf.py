"""
Generates a realistic 3-page Amazon SDE Job Description PDF for testing and demonstration.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


def generate_sample_jd():
    output_dir = os.path.join(os.path.dirname(__file__), "sample_jds")
    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, "Amazon_SDE_JD.pdf")

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#FF9900')
    )
    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#146EB4')
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14
    )

    story = []

    # PAGE 1: Overview and Responsibilities
    story.append(Paragraph("Amazon - Job Description", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Role: Software Development Engineer I (SDE-1)", heading_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Job ID: AMZ-IN-98231<br/>"
        "Location: Hyderabad / Bangalore, India<br/>"
        "Department: Amazon Retail Platforms & Core Backend Services",
        body_style
    ))
    story.append(Spacer(1, 14))
    story.append(Paragraph("About the Team & Role", heading_style))
    story.append(Paragraph(
        "Amazon is seeking innovative, passionate, and detail-oriented Software Development Engineers (SDE-1) "
        "to build planet-scale e-commerce architectures. As an SDE-1, you will collaborate with Senior SDEs and "
        "Product Managers to build highly available backend microservices handling millions of transactions per day.",
        body_style
    ))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Key Responsibilities:", heading_style))
    story.append(Paragraph(
        "• Design, develop, test, deploy, and maintain customer-facing web services and backend APIs.<br/>"
        "• Write clean, robust, maintainable, and well-tested code following Object-Oriented principles.<br/>"
        "• Participate in code reviews, architectural discussions, and automated deployment pipelines.<br/>"
        "• Identify and resolve performance bottlenecks, system reliability issues, and scale constraints.<br/>"
        "• Support operational excellence and production systems with monitoring and metrics.",
        body_style
    ))

    # Force Page Break to Page 2
    from reportlab.platypus import PageBreak
    story.append(PageBreak())

    # PAGE 2: Basic Qualifications
    story.append(Paragraph("Amazon SDE-1 - Qualifications (Page 2)", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Basic Qualifications", heading_style))
    story.append(Paragraph(
        "To be considered for this position, candidates must meet the following baseline requirements:<br/><br/>"
        "• Bachelor’s degree in Computer Science, Computer Engineering, or related STEM field.<br/>"
        "• 0 to 2 years of relevant professional experience or demonstrable software projects.<br/>"
        "• Strong proficiency in at least one modern programming language: <b>C++, Python, or Java</b>.<br/>"
        "• Solid foundation in computer science fundamentals: <b>Data Structures, Algorithms</b>, and complexity analysis.<br/>"
        "• Strong understanding of Object-Oriented Programming (OOP) and software design patterns.<br/>"
        "• Sound understanding of basic database querying and relational data modeling with <b>SQL</b>.<br/>"
        "• Excellent problem-solving skills and capability to write clean, unit-tested code in technical interviews.",
        body_style
    ))
    story.append(Spacer(1, 16))
    story.append(Paragraph("Interview Process & Topics", heading_style))
    story.append(Paragraph(
        "Candidates will go through online coding assessments followed by virtual rounds focusing on:<br/>"
        "1. Data Structures & Algorithms (Trees, Graphs, Dynamic Programming, Arrays, HashMaps).<br/>"
        "2. Low-Level Object Oriented Design (LLD) and clean code architecture.<br/>"
        "3. Amazon Leadership Principles (Customer Obsession, Ownership, Bias for Action, Dive Deep).",
        body_style
    ))

    # Force Page Break to Page 3
    story.append(PageBreak())

    # PAGE 3: Preferred Qualifications & Compensation
    story.append(Paragraph("Amazon SDE-1 - Preferred Skills & Benefits (Page 3)", title_style))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Preferred Qualifications", heading_style))
    story.append(Paragraph(
        "Candidates possessing any of the following additional skills will be prioritized:<br/><br/>"
        "• Practical experience with cloud computing platforms, particularly <b>Amazon Web Services (AWS)</b> (EC2, S3, Lambda, SQS).<br/>"
        "• Experience with containerization technologies such as <b>Docker</b> and orchestration with Kubernetes.<br/>"
        "• Experience working with relational databases such as <b>PostgreSQL or MySQL</b>.<br/>"
        "• Familiarity with NoSQL distributed data stores such as <b>DynamoDB, Redis, or MongoDB</b>.<br/>"
        "• Knowledge of asynchronous event-driven messaging systems like Apache Kafka or RabbitMQ.<br/>"
        "• Familiarity with CI/CD deployment pipelines and automated integration testing tools.",
        body_style
    ))
    story.append(Spacer(1, 16))
    story.append(Paragraph("Compensation & Benefits", heading_style))
    story.append(Paragraph(
        "• Expected Salary Package: <b>16.0 LPA to 28.0 LPA</b> (inclusive of base salary, joining bonus, and Restricted Stock Units - RSUs).<br/>"
        "• Comprehensive health insurance, wellness coverage, and employee assistance programs.<br/>"
        "• Hybrid working model with modern development workstations and ongoing technical training credits.",
        body_style
    ))

    doc.build(story)
    print(f"Sample Job Description PDF generated at: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    generate_sample_jd()
