from django import forms
from .models import Seller, Customer, Product

class SellerCreationForm(forms.ModelForm):
    class Meta:
        model = Seller
        fields = ['founder', 'company_name', 'phone_number']
        
class CustomerRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    
    class Meta:
        model = Customer
        fields = ['username', 'phone_number', 'password']
           
        
    def save(self, commit=True):
        customer = super().save(commit=False)
        customer.set_password(self.cleaned_data['password'])  
        if commit:
            customer.save()
        return customer
    
class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'image', 'category', 'seller']  
