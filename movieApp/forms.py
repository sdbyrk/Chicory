from django import forms

from user.models import Member, Relationship

class RecommendForm(forms.ModelForm):
 	
 	followed = forms.ModelChoiceField(
 		queryset=Relationship.objects.all(), label="Kişiler", widget=forms.Select(attrs={'id':'followedList'}))

 	class Meta:
 		model = Relationship
 		fields = [
             "followed",
        ]