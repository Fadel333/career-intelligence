# test_cvs.py
from app.utils.advanced_cv_parser import AdvancedCVParser
import json

def test_cv_samples():
    """Test the advanced parser with multiple CV samples"""
    
    parser = AdvancedCVParser()
    
    # Sample 1: Junior Developer
    cv1 = """
    Kwame Mensah
    kwame.mensah@email.com | 0244 123 456
    
    SUMMARY
    Motivated Computer Science graduate with internship experience in web development.
    Proficient in HTML, CSS, JavaScript, and React. Eager to contribute to innovative projects.
    
    EDUCATION
    BSc Computer Science, University of Ghana (2021-2025)
    
    INTERNSHIPS
    Web Development Intern at TechHub Accra (Jun 2024 - Aug 2024)
    - Built responsive websites using React and Tailwind CSS
    - Collaborated with senior developers on client projects
    
    PROJECTS
    - Student Portal: Built with React, Node.js, and MongoDB
    - E-commerce Website: Full-stack project using Django
    
    SKILLS
    Technical: React, JavaScript, HTML, CSS, Node.js, MongoDB, Git, Bootstrap
    Languages: English (Fluent), Twi (Native)
    """
    
    # Sample 2: Data Scientist
    cv2 = """
    Abena Osei
    abena.osei@data-science.com | +233 20 123 4567
    
    PROFESSIONAL SUMMARY
    Data Scientist with 3+ years of experience in machine learning and data analysis.
    Expert in Python, SQL, and statistical modeling. Passionate about using data to drive business decisions.
    
    WORK EXPERIENCE
    Data Scientist at Analytics Ghana (2022-Present)
    - Developed ML models predicting customer churn with 85% accuracy
    - Built dashboards using Python and Tableau
    - Led data migration to AWS cloud infrastructure
    
    Junior Data Analyst at Fintech Solutions (2021-2022)
    - Analyzed financial data using Pandas and SQL
    - Created automated reporting systems
    
    EDUCATION
    MSc Data Science, KNUST (2020-2021)
    BSc Statistics, University of Ghana (2016-2020)
    
    CERTIFICATIONS
    AWS Certified Data Analytics Specialty
    Google Professional Data Engineer
    
    SKILLS
    Python, SQL, R, Pandas, NumPy, Scikit-learn, TensorFlow
    AWS, Tableau, Power BI, Statistical Modeling, Machine Learning
    """
    
    # Sample 3: Senior Software Engineer
    cv3 = """
    Kofi Asare
    kofi.asare@tech.com | 024 456 7890 | Ghana
    
    SENIOR SOFTWARE ENGINEER
    8+ years of experience delivering scalable solutions in fintech and e-commerce.
    Strong background in microservices, cloud architecture, and team leadership.
    
    EXPERIENCE
    Senior Software Engineer at BankTech Ghana (2019-Present)
    - Led team of 12 developers building payment processing system
    - Architected microservices using Spring Boot and Docker
    - Migrated legacy systems to AWS with zero downtime
    
    Software Developer at E-Commerce Ghana (2016-2019)
    - Built REST APIs using Flask and PostgreSQL
    - Implemented CI/CD pipeline with Jenkins and Docker
    
    EDUCATION
    MSc Software Engineering, University of Ghana (2014-2016)
    BSc Information Technology, KNUST (2010-2014)
    
    TECHNICAL SKILLS
    Java, Python, Spring Boot, Flask, PostgreSQL, MySQL, MongoDB
    AWS, Docker, Kubernetes, Jenkins, Git, Linux
    Microservices, REST APIs, System Design
    
    CERTIFICATIONS
    AWS Solutions Architect Professional
    Oracle Certified Professional, Java SE
    Certified Kubernetes Administrator (CKA)
    
    SOFT SKILLS
    Leadership, Mentoring, Communication, Problem Solving, Agile Methodologies
    """
    
    # Sample 4: DevOps Engineer
    cv4 = """
    Yaw Boakye
    yaw.devops@cloud.com | +233 50 123 4567
    
    DEVOPS ENGINEER
    5 years of experience in cloud infrastructure and automation.
    Expert in AWS, Kubernetes, Terraform, and CI/CD pipelines.
    
    EXPERIENCE
    DevOps Engineer at CloudTech Solutions (2020-Present)
    - Managed AWS infrastructure for 50+ microservices
    - Implemented Kubernetes clusters for production workloads
    - Automated infrastructure provisioning using Terraform
    
    System Administrator at IT Services Ghana (2018-2020)
    - Maintained Linux servers and network infrastructure
    - Implemented monitoring with Prometheus and Grafana
    
    SKILLS
    AWS, Azure, GCP, Docker, Kubernetes, Terraform, Ansible
    Linux, Bash, Python, Jenkins, Git, Prometheus, Grafana
    CI/CD, Infrastructure as Code, Cloud Security
    
    CERTIFICATIONS
    AWS Certified DevOps Engineer - Professional
    Certified Kubernetes Administrator (CKA)
    HashiCorp Certified: Terraform Associate
    """
    
    # Sample 5: Product Manager (Non-technical)
    cv5 = """
    Esi Ama
    esi.ama@product.com | 020 987 6543
    
    PRODUCT MANAGER
    7 years of experience in product strategy and user experience.
    Track record of launching successful products in the African market.
    
    EXPERIENCE
    Senior Product Manager at FinTech Africa (2019-Present)
    - Launched mobile banking app with 500k+ users
    - Led cross-functional team of 20+ people
    - Defined product roadmap and feature prioritization
    
    Product Owner at E-Commerce Ghana (2016-2019)
    - Managed product backlog and stakeholder communications
    - Conducted user research and market analysis
    
    EDUCATION
    MBA, University of Ghana (2014-2016)
    BSc Business Administration, KNUST (2010-2014)
    
    SKILLS
    Product Strategy, Market Research, User Experience (UX)
    Agile, Scrum, JIRA, Confluence, Data Analysis
    Leadership, Communication, Strategic Planning, Stakeholder Management
    
    CERTIFICATIONS
    Certified Scrum Product Owner (CSPO)
    Project Management Professional (PMP)
    """
    
    # Test all CVs
    cv_samples = [
        ("Junior Developer", cv1),
        ("Data Scientist", cv2),
        ("Senior Software Engineer", cv3),
        ("DevOps Engineer", cv4),
        ("Product Manager", cv5)
    ]
    
    print("=" * 70)
    print("📄 ADVANCED CV PARSER - TEST RESULTS")
    print("=" * 70)
    
    all_results = []
    
    for name, cv_text in cv_samples:
        print(f"\n🔍 Testing: {name}")
        print("-" * 50)
        
        results = parser.parse_cv(cv_text)
        
        # Print results
        print(f"\n📧 Email: {results.get('email', 'Not found')}")
        print(f"📞 Phone: {results.get('phone', 'Not found')}")
        print(f"💼 Job Title: {results.get('current_job_title', 'Not found')}")
        print(f"📅 Experience: {results.get('experience_years', 0)} years")
        
        print("\n🛠️ TECHNICAL SKILLS:")
        for category, skills in results['skills'].items():
            if skills:
                print(f"  {category}: {', '.join(skills)}")
        
        print(f"\n🧠 Soft Skills: {', '.join(results['soft_skills']) if results['soft_skills'] else 'None'}")
        
        print(f"\n📜 Certifications: {', '.join(results['certifications']) if results['certifications'] else 'None'}")
        
        print("\n🎓 Education:")
        for edu in results['education'][:3]:  # Limit to top 3
            print(f"  {edu.get('degree', 'Unknown')} at {edu.get('institution', 'Unknown')}")
        
        print(f"\n💼 Work Experience:")
        for exp in results['work_experience'][:3]:  # Limit to top 3
            print(f"  {exp.get('title', 'Unknown')} at {exp.get('company', 'Unknown')}")
        
        print(f"\n📊 Skill Level: {results['skill_level']['level']} ({results['skill_level']['percentage']}%)")
        print(f"📈 Total Skills Found: {results['total_skills']}")
        print(f"📄 Word Count: {results['word_count']}")
        print("-" * 50)
        
        # Save results
        all_results.append({
            'name': name,
            'results': results
        })
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY STATISTICS")
    print("=" * 70)
    
    avg_skills = sum(r['results']['total_skills'] for r in all_results) / len(all_results)
    avg_exp = sum(r['results']['experience_years'] for r in all_results) / len(all_results)
    
    print(f"Average Skills per CV: {avg_skills:.1f}")
    print(f"Average Experience: {avg_exp:.1f} years")
    print(f"Total CVs Tested: {len(all_results)}")
    
    # Save to JSON
    with open('test_results.json', 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print("\n✅ Test results saved to test_results.json")

if __name__ == "__main__":
    test_cv_samples()