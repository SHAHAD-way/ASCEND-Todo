from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm
)

from .models import Profile


class RegisterForm(UserCreationForm):

    email = forms.EmailField(
        required=True
    )

    class Meta:
        model = User
        fields = [
            'username',
            'email',
            'password1',
            'password2'
        ]


class CustomPasswordChangeForm(PasswordChangeForm):

    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter current password'
            }
        )
    )

    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Enter new password'
            }
        )
    )

    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(
            attrs={
                'placeholder': 'Confirm new password'
            }
        )
    )


class ProfilePictureForm(forms.ModelForm):

    class Meta:
        model = Profile
        fields = [
            'profile_picture'
        ]

    def clean_profile_picture(self):

        picture = self.cleaned_data.get(
            'profile_picture'
        )

        uploaded_picture = self.files.get(
            'profile_picture'
        )

        # No new image was uploaded.
        # Keep the existing profile picture.
        if not uploaded_picture:
            return picture

        # Maximum file size: 2 MB

        if uploaded_picture.size > 2 * 1024 * 1024:

            raise forms.ValidationError(
                'Profile picture must be smaller than 2 MB.'
            )

        # Allowed image types

        allowed_types = [
            'image/jpeg',
            'image/png',
            'image/webp'
        ]

        if uploaded_picture.content_type not in allowed_types:

            raise forms.ValidationError(
                'Only JPG, PNG, and WEBP images are allowed.'
            )

        return picture