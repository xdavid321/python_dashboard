from django import forms

class DataSheetUpload(forms.Form):
    headerColumns = forms.IntegerField(min_value=1, initial = 2)
    datasheet = forms.FileField(widget = forms.ClearableFileInput(attrs={'multiple' : True}))

class LoginForm(forms.Form):
    user_name = forms.CharField()
    password = forms.CharField(widget = forms.PasswordInput)

class AssignMarket(forms.Form):
    user_id = forms.CharField()
    markets = forms.CharField()