from django import forms
from django.forms import ModelForm

from .models import Meeting, MeetingDetails
from accounts.models import User, Student, Professor

class MeetingForm(ModelForm):
    attendee = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Συμμετέχων'
    )
    
    class Meta:
        model = Meeting
        fields = ('name', 'attendee', 'url', 'duration', 'description')
        labels = {
            'name': '',
            'url': '',
            'duration': '',
            'description': '',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Τίτλος'}),
            'url': forms.TextInput(attrs={'class':'form-control', 'placeholder':'Σύνδεσμος εκδήλωσης (προαιρετικό)'}),
            'description': forms.Textarea(attrs={'class':'form-control', 'placeholder':'Περιγραφή'}),
            'duration': forms.Select(attrs={'class': 'form-select', 'placeholder':'Διάρκεια'})
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extract the user from kwargs
        self.date = kwargs.pop('date', None)  # Capture the date
        self.time = kwargs.pop('time', None)  # Capture the time
        super().__init__(*args, **kwargs)
        
        if self.user is not None:
            # Populate attendee choices based on user role
            if self.user.is_student():
                # If the user is a student, populate professors
                self.fields['attendee'].choices = [
                    (professor.user.email, professor.user.get_full_name())
                    for professor in Professor.objects.all()
                ]
            elif self.user.is_professor():
                # If the user is a professor, populate students
                self.fields['attendee'].choices = [
                    (student.user.email, student.user.get_full_name())
                    for student in Student.objects.all()
                ]
            else:
                # Default to an empty choice
                self.fields['attendee'].choices = []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.duration:
            instance.duration = None
        if not instance.pk:  # Only set the date and created_by on new instances
            instance.date = self.date
            instance.time = self.time
            instance.created_by = self.user
        return super().save(commit=commit)

class MeetingDetailsForm(forms.ModelForm):
    professor_first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 
                'readonly': 'readonly'
                }), 
        label="Όνομα"
    )
    
    professor_last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 
                'readonly': 'readonly'
            }), 
        label="Επώνυμο"
    )
    
    student_first_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 
                'readonly': 'readonly'
                }), 
        label="Όνομα"
    )
    
    student_last_name = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 
                'readonly': 'readonly'
            }), 
        label="Επώνυμο"
    )
    
    student_email = forms.CharField(
        widget=forms.TextInput(
            attrs={
                'class': 'form-control', 
                'readonly': 'readonly'
            }), 
        label="Email"
    )
    
    topics = forms.MultipleChoiceField(
        widget=forms.SelectMultiple(
            attrs={
                'class': 'form-select select2'
            }), 
        choices=MeetingDetails.TOPICS_CHOICES,
        label="Θέματα που καλύφθηκαν"
    )
    
    class Meta:
        model = MeetingDetails
        fields = [
            'academic_year', 'semester', 
            'duration', 'topics', 'comments'
        ]
        widgets = {
            'academic_year': forms.TextInput(attrs={'class': 'form-control'}),
            'semester': forms.TextInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'comments': forms.Textarea(attrs={'class':'form-control'}),
        }
        labels = {
            'academic_year': 'Ακαδημαϊκό Έτος',
            'semester': 'Ακαδημαϊκό Εξάμηνο',
            'duration': 'Διάρκεια συνάντησης (σε λεπτά)',
            'comments': 'Σχόλια/Παρατηρήσεις',
        }
    
    def __init__(self, *args, **kwargs):
        professor = kwargs.pop('professor', None)  # Professor passed during form initialization
        student = kwargs.pop('student', None)  # Student passed during form initialization
        super().__init__(*args, **kwargs)
        
        print(student.first_name, student.last_name)
        
        if professor:
            self.fields['professor_first_name'].initial = professor.first_name
            self.fields['professor_last_name'].initial = professor.last_name
        
        if student:
            self.fields['student_first_name'].initial = student.first_name
            self.fields['student_last_name'].initial = student.last_name
            self.fields['student_email'].initial = student.email
        
        # Dynamically generate choices for the topics field from the model's TOPICS_CHOICES
        self.fields['topics'].choices = MeetingDetails.TOPICS_CHOICES