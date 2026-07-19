# app/recruiter/forms.py
try:
    from flask_wtf import FlaskForm
    from wtforms import StringField, TextAreaField, SelectField, FloatField, BooleanField, DateField
    from wtforms.validators import DataRequired, Optional, NumberRange, Length
except ImportError:
    # Fallback if flask_wtf is not installed
    print("WARNING: flask_wtf not installed. Using dummy forms.")
    from flask import request
    
    class FlaskForm:
        def validate_on_submit(self):
            return request.method == 'POST'
        
        def __init__(self, *args, **kwargs):
            pass
    
    class StringField:
        def __init__(self, label='', validators=None, **kwargs):
            self.label = label
            self.data = ''
            self.errors = []
    class TextAreaField(StringField): pass
    class SelectField(StringField): pass
    class FloatField(StringField): pass
    class BooleanField(StringField): pass
    class DateField(StringField): pass  # Changed from DateTimeField to DateField
    class DataRequired: pass
    class Optional: pass
    class NumberRange: pass
    class Length: pass

class JobForm(FlaskForm):
    title = StringField('Job Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Job Description', validators=[DataRequired()])
    requirements = TextAreaField('Requirements (one per line)', validators=[Optional()])
    responsibilities = TextAreaField('Responsibilities (one per line)', validators=[Optional()])
    employment_type = SelectField('Employment Type', choices=[
        ('', 'Select...'),  # Added empty option
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote')
    ], validators=[DataRequired()])
    experience_level = SelectField('Experience Level', choices=[
        ('', 'Select...'),  # Added empty option
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('lead', 'Lead'),
        ('manager', 'Manager')
    ], validators=[DataRequired()])
    salary_min = FloatField('Minimum Salary', validators=[Optional(), NumberRange(min=0)])
    salary_max = FloatField('Maximum Salary', validators=[Optional(), NumberRange(min=0)])
    currency = SelectField('Currency', choices=[
        ('GHS', 'GHS'), 
        ('USD', 'USD'), 
        ('EUR', 'EUR'),
        ('NGN', 'NGN')
    ], default='GHS')
    location = StringField('Location', validators=[DataRequired()])
    remote_available = BooleanField('Remote Available', default=False)
    required_skills = TextAreaField('Required Skills (comma separated)', validators=[DataRequired()])
    preferred_skills = TextAreaField('Preferred Skills (comma separated)', validators=[Optional()])
    
    # CHANGED: DateTimeField -> DateField
    expires_at = DateField('Expiry Date', validators=[Optional()], format='%Y-%m-%d')
    
    save_as_draft = BooleanField('Save as Draft', default=False)