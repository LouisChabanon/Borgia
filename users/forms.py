from django import forms
from users.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Permission, Group


# Formulaire de création d'un user
class UserCreationCustomForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'surname', 'family', 'campus', 'year',
                  'user_permissions', 'groups')

    def clean_username(self):
        username = self.cleaned_data['username']

        try:
            self.Meta.model.objects.get(username=username)
        except self.Meta.model.DoesNotExist:
            return username

        raise forms.ValidationError(
            self.error_messages['duplicate_username'],
            code='duplicate_username',
        )

    first_name = forms.CharField(label='Prénom', max_length=255)
    last_name = forms.CharField(label='Nom', max_length=255)
    surname = forms.CharField(label='Buque', max_length=255)
    family = forms.CharField(label='Fam\'ss', max_length=255)
    campus = forms.CharField(label='Tabagn\'s', max_length=2)
    year = forms.IntegerField(label='Prom\'ss')
    user_permissions = forms.ModelMultipleChoiceField(label='Permissions', required=False,
                                                      widget=forms.CheckboxSelectMultiple,
                                                      queryset=Permission.objects.all())
    groups = forms.ModelMultipleChoiceField(label='Groupes', required=False,
                                            widget=forms.CheckboxSelectMultiple,
                                            queryset=Group.objects.all())
