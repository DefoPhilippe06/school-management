from django import forms
from django.contrib.auth import get_user_model
from .models import Student, Enrollment
from classes.models import ClassRoom
from core.models import SchoolYear

User = get_user_model()


class StudentRegistrationForm(forms.Form):
    # Informations utilisateur
    first_name = forms.CharField(max_length=150, label="Prénom")
    last_name = forms.CharField(max_length=150, label="Nom")
    email = forms.EmailField(required=False, label="Email (optionnel)")
    username = forms.CharField(max_length=150, label="Nom d'utilisateur")

    # Informations élève
    matricule = forms.CharField(max_length=30, label="Matricule")
    date_of_birth = forms.DateField(
        label="Date de naissance",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    place_of_birth = forms.CharField(max_length=100, required=False, label="Lieu de naissance")
    gender = forms.ChoiceField(choices=[('M', 'Masculin'), ('F', 'Féminin')], label="Sexe")
    address = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}), required=False, label="Adresse")
    phone = forms.CharField(max_length=20, required=False, label="Téléphone")

    # Classe
    classroom = forms.ModelChoiceField(
        queryset=ClassRoom.objects.none(),
        label="Classe"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current_year = SchoolYear.objects.filter(is_current=True).first()
        if current_year:
            self.fields['classroom'].queryset = ClassRoom.objects.filter(school_year=current_year)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Ce nom d'utilisateur existe déjà.")
        return username

    def clean_matricule(self):
        matricule = self.cleaned_data['matricule']
        if Student.objects.filter(matricule=matricule).exists():
            raise forms.ValidationError("Ce matricule existe déjà.")
        return matricule

    def save(self):
        data = self.cleaned_data

        # Générer un mot de passe aléatoire
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(10))

        # 1. Créer l'utilisateur
        user = User.objects.create_user(
            username=data['username'],
            email=data.get('email', ''),
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=User.Role.STUDENT,
            password=password
        )

        # 2. Créer l'élève
        student = Student.objects.create(
            user=user,
            matricule=data['matricule'],
            date_of_birth=data['date_of_birth'],
            place_of_birth=data.get('place_of_birth', ''),
            gender=data['gender'],
            address=data.get('address', ''),
            phone=data.get('phone', ''),
            current_class=data['classroom']
        )

        # 3. Créer l'inscription
        Enrollment.objects.create(
            student=student,
            classroom=data['classroom'],
            school_year=data['classroom'].school_year,
            status=Enrollment.Status.ACTIVE
        )

        return student