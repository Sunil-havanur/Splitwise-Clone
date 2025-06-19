from django import forms
from .models import Group, Expense, Split
from django.contrib.auth.models import User

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'members']
        widgets = {
            'members' : forms.CheckboxSelectMultiple()
        }

class ExpenseForm(forms.Form):
    group = forms.ModelChoiceField(queryset=Group.objects.all())
    description = forms.CharField(max_length=255)
    amount = forms.DecimalField(decimal_places=2, max_digits=10)
    paid_by = forms.ModelChoiceField(queryset=User.objects.all())
    split_type = forms.ChoiceField(choices=[('equal', 'Equal'), ('percentage', 'Percentage')])
    members = forms.ModelMultipleChoiceField(queryset=User.objects.all(), widget=forms.CheckboxSelectMultiple)
    percentages = forms.CharField(required=False, help_text="Comma-separated percentages if split_type is percentage (e.g., 50,30,20)")


