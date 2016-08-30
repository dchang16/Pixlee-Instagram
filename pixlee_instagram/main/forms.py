from django import forms
import datetime

class SearchForm(forms.Form):
	tag_field = forms.CharField(initial="SanFrancisco")
	start_date = forms.DateField(initial=datetime.date.today)
	end_date = forms.DateField(initial=datetime.date.today)

class NameForm(forms.Form):
	name = forms.CharField()