from django import forms
from .models import Demand, DemandStagePeriod
from datetime import datetime, timedelta

class DemandForm(forms.ModelForm):
    # Common style for all form fields
    input_style = 'width: 100%; max-width: 100%;'
    
    start_date = forms.DateField(
        label='Start Date (t0)', 
        widget=forms.DateInput(attrs={'type': 'date', 'style': input_style, 'class': 'form-control'})
    )

    duration_months = forms.IntegerField(
        label='Duration in Months (end)', 
        min_value=1, 
        required=True,
        help_text='Total duration of the demand in months',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'style': input_style})
    )

    demand_ID = forms.CharField(
        label='Demand ID',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': input_style})
    )

    FILE_TYPE_CHOICES = [
        ('GEM', 'GEM'),
        ('LPC', 'LPC'),
        ('CASh', 'CASh')
    ]
    
    FILE_SUBTYPE_CHOICES = [
        ('', '---------'),
        ('Project', 'Project'),
        ('Build up', 'Build up')
    ]
    
    FILE_DETAIL_CHOICES = [
        ('', '---------'),
        ('MTR 21', 'MTR 21'),
        ('MTR 28', 'MTR 28')
    ]
    
    file_type = forms.ChoiceField(
        label='File Type',
        required=True,
        choices=FILE_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'style': input_style, 'id': 'id_file_type'})
    )
    
    file_subtype = forms.ChoiceField(
        label='File Subtype',
        required=True,
        choices=FILE_SUBTYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'style': input_style, 'id': 'id_file_subtype'})
    )
    
    file_detail = forms.ChoiceField(
        label='File Detail',
        required=True,
        choices=FILE_DETAIL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control', 'style': input_style, 'id': 'id_file_detail'})
    )

    demand_amount = forms.DecimalField(
        label='Demand Amount',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': input_style})
    )

    io_name = forms.CharField(
        label='IO Name',
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'style': input_style})
    )
   
    class Meta:
        model = Demand
        fields = ['name', 'demand_ID', 'file_type', 'file_subtype', 'file_detail', 'demand_amount', 'io_name', 'start_date', 'duration_months']
        
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
