from django import forms
from .models import MarketingPreference

class MarketingPreferenceForm(forms.ModelForm):
	subscribed = forms.BooleanField(label='Receive Marketing Email?')
	class Meta:
		model = MarketingPreference
		fields = ['subscribed']