from django import forms
from .models import Topic,Post

class NewTopicForm(forms.ModelForm):
    subject = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 1, 'placeholder': 'Subject name?'}),
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'What do you want to talk about?'}),
        max_length=4000,
        help_text='The maximum length of the text is 4000.'
    )

    class Meta:
        model = Topic
        fields = ['subject', 'message']


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message', ]
