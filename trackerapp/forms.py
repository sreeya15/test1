from django import forms
from .models import Demand, DemandStagePeriod
from datetime import datetime, timedelta

class DemandForm(forms.ModelForm):
    start_date = forms.DateField(
        label='Start Date (t0)', 
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    duration_months = forms.IntegerField(
        label='Duration in Months (end)', 
        min_value=1, 
        required=True,
        help_text='Total duration of the demand in months'
    )

    demand_ID = forms.CharField(
        label='Demand ID',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    file_type = forms.CharField(
        label='File Type',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    demand_amount = forms.DecimalField(
        label='Demand Amount',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    io_name = forms.CharField(
        label='IO Name',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
   
    class Meta:
        model = Demand
        fields = ['name', 'demand_ID', 'file_type', 'demand_amount', 'io_name', 'start_date', 'duration_months']
        
    def save(self, commit=True):
        demand = super().save(commit=False)
        if commit:
            demand.save()
        return demand

class DemandStagePeriodForm(forms.ModelForm):
    class Meta:
        model = DemandStagePeriod
        fields = ['demand', 'stage', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure end_date is not before start_date
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date cannot be before start date')
        
        return cleaned_data
