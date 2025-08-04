from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Photo, Video, Album

class CustomUserCreationForm(UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your phone number'}),
        label='Phone Number'
    )
    gmail = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your Gmail address'}),
        label='Gmail'
    )

    def clean_gmail(self):
        gmail = self.cleaned_data.get('gmail')
        if not gmail or not gmail.endswith('@gmail.com'):
            raise forms.ValidationError('Please enter a valid Gmail address.')
        return gmail

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter a password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })

class PhotoUploadForm(forms.ModelForm):
    albums = forms.ModelMultipleChoiceField(
        queryset=Album.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Photo
        fields = ['title', 'description', 'image', 'albums']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter photo title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter photo description'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['albums'].queryset = Album.objects.filter(user=user)

class VideoUploadForm(forms.ModelForm):
    albums = forms.ModelMultipleChoiceField(
        queryset=Album.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    class Meta:
        model = Video
        fields = ['title', 'description', 'video_file', 'thumbnail', 'albums']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter video title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter video description'}),
            'video_file': forms.FileInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['albums'].queryset = Album.objects.filter(user=user)

class MultiPhotoUploadForm(forms.Form):
    dummy = forms.CharField(widget=forms.HiddenInput(), required=False)
    title = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title for all (optional)'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description for all (optional)'}))
    albums = forms.ModelMultipleChoiceField(
        queryset=Album.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['albums'].queryset = Album.objects.filter(user=user)

class MultiVideoUploadForm(forms.Form):
    dummy = forms.CharField(widget=forms.HiddenInput(), required=False)
    title = forms.CharField(max_length=200, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Title for all (optional)'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description for all (optional)'}))
    albums = forms.ModelMultipleChoiceField(
        queryset=Album.objects.none(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-select'})
    )
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['albums'].queryset = Album.objects.filter(user=user) 