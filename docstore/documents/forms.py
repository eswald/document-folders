from django.forms import ModelForm

from .models import Document


class DocumentCreationForm(ModelForm):
    class Meta:
        model = Document
        fields = [
            'name',
            'content',
        ]
    
    def save(self, account=None, commit=True):
        if account is not None:
            self.instance.account = account
        return super().save(commit=commit)
