from django import forms
from .models import Demand, DemandStagePeriod, WeeklyUpdate, Stage
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
        ('CASH', 'CASH')
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
        required=False,  # Changed to False as we'll validate it conditionally
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
        
    def clean(self):
        cleaned_data = super().clean()
        file_subtype = cleaned_data.get('file_subtype')
        file_detail = cleaned_data.get('file_detail')
        
        # Only require file_detail if file_subtype is 'Project'
        if file_subtype == 'Project' and not file_detail:
            self.add_error('file_detail', 'This field is required when File Subtype is Project.')
            
        return cleaned_data
        
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

class WeeklyUpdateForm(forms.ModelForm):
    class Meta:
        model = WeeklyUpdate
        fields = ['week_number', 'week_start_date', 'week_end_date', 'current_stage', 'challenges', 'achievements']
        widgets = {
            'week_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select start date'
            }),
            'week_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': 'Select end date'
            }),
            'challenges': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe any challenges faced this week...'}),
            'achievements': forms.Textarea(attrs={'rows': 3, 'placeholder': 'List key achievements for this week...'}),
        }

    def __init__(self, *args, **kwargs):
        demand = kwargs.pop('demand', None)
        super().__init__(*args, **kwargs)
        
        # Filter choices based on selected stages for this demand
        if demand and demand.selected_stages:
            # Only show stages that were selected when creating the demand
            available_choices = [('', 'Select Stage')]
            # print(f"DEBUG: Demand {demand.id} selected_stages: {demand.selected_stages}")
            # print(f"DEBUG: Selected stages type: {type(demand.selected_stages)}")
            
            for stage_value in demand.selected_stages:
                # print(f"DEBUG: Processing stage_value: {stage_value}")
                # Get the stage label from Stage.choices
                stage_label = None
                for choice_value, choice_label in Stage.choices:
                    if choice_value == stage_value:
                        stage_label = choice_label
                        break
                
                if stage_label:
                    available_choices.append((stage_value, stage_label))
                    # print(f"DEBUG: Added stage {stage_value} with label {stage_label}")
                else:
                    # Fallback to the value itself if label not found
                    available_choices.append((stage_value, stage_value))
                    # print(f"DEBUG: Added stage {stage_value} with fallback label")
            
            # print(f"DEBUG: Final available choices: {available_choices}")
            self.fields['current_stage'].choices = available_choices
        else:
            # If no stages were selected, show only the default option
            # print(f"DEBUG: No selected stages for demand {demand.id if demand else 'None'}")
            self.fields['current_stage'].choices = [('', 'No stages selected for this demand')]
        
        # Set date restrictions based on demand duration
        if demand and demand.start_date and demand.get_end_date():
            demand_start = demand.start_date
            demand_end = demand.get_end_date()
            
            # Format dates for HTML date input (YYYY-MM-DD)
            min_date = demand_start.strftime('%Y-%m-%d')
            max_date = demand_end.strftime('%Y-%m-%d')
            
            # Update widget attributes to restrict date selection
            self.fields['week_start_date'].widget.attrs.update({
                'min': min_date,
                'max': max_date,
                'data-demand-start': min_date,
                'data-demand-end': max_date
            })
            
            self.fields['week_end_date'].widget.attrs.update({
                'min': min_date,
                'max': max_date,
                'data-demand-start': min_date,
                'data-demand-end': max_date
            })
            
            # Update help text to show demand duration
            self.fields['week_start_date'].help_text = f'Select the start date of this week (Demand duration: {demand_start.strftime("%b %d, %Y")} to {demand_end.strftime("%b %d, %Y")})'
            self.fields['week_end_date'].help_text = f'Select the end date of this week (Demand duration: {demand_start.strftime("%b %d, %Y")} to {demand_end.strftime("%b %d, %Y")})'
        else:
            # Add help text for date fields
            self.fields['week_start_date'].help_text = 'Select the start date of this week'
            self.fields['week_end_date'].help_text = 'Select the end date of this week'
        
    def clean(self):
        cleaned_data = super().clean()
        week_start_date = cleaned_data.get('week_start_date')
        week_end_date = cleaned_data.get('week_end_date')
        current_stage = cleaned_data.get('current_stage')
        
        # Ensure end_date is not before start_date
        if week_start_date and week_end_date and week_end_date < week_start_date:
            self.add_error('week_end_date', 'End date cannot be before start date')
        
        # Validate current_stage if provided
        if current_stage:
            # Check if the stage is in the available choices
            available_stages = [choice[0] for choice in self.fields['current_stage'].choices if choice[0]]
            if current_stage not in available_stages:
                self.add_error('current_stage', f'Select a valid choice. {current_stage} is not one of the available choices.')
        
        return cleaned_data
