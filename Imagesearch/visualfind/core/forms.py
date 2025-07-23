from django import forms
class UploadForm(forms.Form):
    image = forms.ImageField(required=False)
    image_url = forms.CharField(required=False)
    camera_image = forms.CharField(required=False)