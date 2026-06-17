from app.utils.advanced_cv_parser import AdvancedCVParser

# Sample CV text
sample_cv = """
John Doe
Software Engineer with 5+ years of experience
Email: john.doe@email.com | Phone: +233 123 456 789

SUMMARY
Experienced Python Developer with expertise in Machine Learning and Cloud Computing.
Strong background in Django, Flask, and AWS.

WORK EXPERIENCE
Senior Python Developer at TechCompany (2020-2024)
- Built ML models using TensorFlow
- Deployed applications on AWS
- Led team of 5 developers

EDUCATION
MSc Computer Science, University of Ghana (2018)
BSc Information Technology, KNUST (2015)

SKILLS
Python, JavaScript, Django, Flask, TensorFlow, AWS, Docker, PostgreSQL
Leadership, Communication, Problem Solving

CERTIFICATIONS
AWS Certified Solutions Architect
Certified Scrum Master
"""

parser = AdvancedCVParser()
results = parser.parse_cv(sample_cv)

print("=" * 50)
print("📄 ADVANCED CV PARSING RESULTS")
print("=" * 50)

print(f"\n👤 Name: {results.get('email', 'Not found')}")
print(f"📧 Email: {results.get('email', 'Not found')}")
print(f"📞 Phone: {results.get('phone', 'Not found')}")
print(f"💼 Job Title: {results.get('current_job_title', 'Not found')}")
print(f"📅 Experience: {results.get('experience_years', 0)} years")

print("\n🛠️ TECHNICAL SKILLS:")
for category, skills in results['skills'].items():
    if skills:
        print(f"  {category}: {', '.join(skills)}")

print(f"\n🧠 Soft Skills: {', '.join(results['soft_skills']) if results['soft_skills'] else 'None'}")

print(f"\n📜 Certifications: {', '.join(results['certifications']) if results['certifications'] else 'None'}")

print(f"\n🎓 Education:")
for edu in results['education']:
    print(f"  {edu['degree']} at {edu['institution']}")

print(f"\n💼 Work Experience:")
for exp in results['work_experience']:
    print(f"  {exp['title']} at {exp['company']}")

print(f"\n📊 Skill Level: {results['skill_level']['level']} ({results['skill_level']['percentage']}%)")
print(f"📈 Total Skills Found: {results['total_skills']}")
print(f"📄 Word Count: {results['word_count']}")