from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.auth import logout
from django.views.generic import CreateView, TemplateView, View, ListView
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from .models import History
from .forms import CreateUserForm
import requests
from django.db.models import *

def logout_view(request):
    logout(request)
    return redirect('login') 

def getBalance(user):
    total_deposits = History.objects.filter(user=user,type="deposit",status= "success").aggregate(total=Sum('amount'))['total'] 
    total_debits = History.objects.filter(user=user,type="withdraw",status= "success").aggregate(total=Sum('amount'))['total']

    if total_deposits is None:
        total_deposits = 0
    if total_debits is None:
        total_debits = 0

    balance = total_deposits - total_debits
    return float(balance)    
'''
    Write a function that finds the user's balance and returns it with the float data type. 
    To calculate the balance, calculate the sum of all user's deposits and the sum of all withdrawals.
    Then subtract the withdrawal amount from the deposit amount and return the result.
    '''
def getCurrencyParams():
    url ="https://fake-api.apps.berlintech.ai/api/currency_exchange"
    
    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            string_list = [(currency,f'{currency} ({rate})') for currency,rate in data.items()]
            return [data, string_list]
        else:
            return [None, None]
    except requests.RequestException as e:
        print(f'An error occured : {e}')  
        return [None, None]     
    '''
    Write a function that makes a GET request to the following address 
    https://fake-api.apps.berlintech.ai/api/currency_exchange

    if the response code is 200 return a list of two values:
    - a dictionary of data that came from the server
    - a list of strings based on the received data 
    mask to form the string f'{currency} ({rate})'.
    example string: 'USD (1.15)'

    if the server response code is not 200 you should 
    return the list [None, None]
    '''


class CreateUserView(CreateView):
    model = User
    form_class = CreateUserForm
    template_name = 'app/create_account.html'
    success_url = reverse_lazy('login')

   

    def form_valid(self, form):
        user = form.save()
        # Redirect to a specific URL after successful form submission
        return redirect('login') 
    
    def form_invalid(self, form):
        # Handle invalid form submission (typically render the form with errors)
        return self.render_to_response(self.get_context_data(form=form))
    
        '''
        If the user is authenticated, then add the 'username' key with the value of username to the context.
        '''
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['username'] = self.request.user.username
        return context    
    


    '''
    Finalize this class. It should create a new user.
    The model should be the User model
    The CreateUserForm model should be used as a form.
    The file create_account.html should be used as a template.
    If the account is successfully created, it should redirect to the page with the name login
    '''
    
    

class CustomLoginView(LoginView):
    template_name = 'app/login.html'
    success_url = reverse_lazy("main_menu")
    '''"
    Modify this class. 
    specify the login.html file as the template
    if authentication is positive, add redirect to main_menu page
    '''

    def get_success_url(self):
        return self.success_url

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            context['username']= self.request.user.username
        return context
        
            
        ''' 
        If the user is authenticated, then add the 'username' key with the value of username to the context.
        '''
        

class MainMenuView(LoginRequiredMixin, TemplateView):
    template_name = 'app/main_menu.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['username'] = self.request.user.username
        if self.request.user.is_authenticated:
            return context

        '''
        If the user is authenticated, then add the 'username' key with the value of username to the context.
        '''
       

class BalanceOperationsView(LoginRequiredMixin, View):
    template_name = 'app/operations.html'

    def get(self, request):
        balance = getBalance(request.user)
        context = {
            'balance': balance,
            'username': request.user.username
        }
        return render(request, self.template_name, context)       
        '''
        This method should return the page given in template_name with a context.

        Context is a dictionary with balance and username keys.
        The balance key contains the result of the getBalance function
        username contains the username of the user.
        '''

    def post(self, request):
        type = request.POST.get('type')
        amount = float(request.POST.get('amount'))  # Get the amount from the form
        user = request.user
        balance = getBalance(user)  # Get the current balance

        if type == 'withdraw':
            if balance >= amount:
                balance -= amount  # Deduct the amount
                status = 'success'
            else:
                messages.error(request, "Insufficient balance")
                status = 'failure'
        elif type == 'deposit':
            balance += amount  # Add the amount
            status = 'success'
        else:
            messages.error(request, "Invalid operation type")
            return self.get(request)

    # Log the transaction
        History.objects.create(
            status=status,
            amount=amount,
            type=type,
            user=user
        )

    # Update user's balance
        getBalance(user)  # Call the function to update the balance

        context = {
            'balance': balance,
            'username': user.username
        }
        return render(request, self.template_name, context)


class ViewTransactionHistoryView(LoginRequiredMixin, ListView):
    model = History
    template_name = 'app/history.html'
    context_object_name = 'transactions'
    ordering = ['-datetime']
    

    def get_queryset(self):
        return History.objects.filter(user=self.request.user)
        '''
        This method should return the entire transaction history of the current user
        '''

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add the 'username' key with the value of username to the context.
        context['username'] = self.request.user.username
        return context
        '''
        Add the 'username' key with the value of username to the context.
        '''
        

class CurrencyExchangeView(LoginRequiredMixin, View):
    template_name = 'app/currency_exchange.html'
    empty_context = {'currency_choices': [], 'amount': None, 'currency': None, 'exchanged_amount': None}

    def get(self, request):
        _, currency_choices = getCurrencyParams()
        context = {
            **self.empty_context, 
            'currency_choices': currency_choices,  
        }
        return render(request, self.template_name, context)

    
    def post(self, request):
        data, currency_choices = getCurrencyParams()
    
    # Process the 'amount' from the form
        amount = request.POST.get('amount')
        try:
            amount = float(amount) if amount else None
        except ValueError:
            amount = None  # Set to None if conversion fails

    #  Get the currency value from the form
        currency = request.POST.get('currency')

    # Check if 'data' or 'amount' is None
        if data is None or amount is None:
            context = self.empty_context
            return render(request, self.template_name, context)

    # Generate the exchange_rate
        exchange_rate = data.get(currency) 

    # Step 5: Calculate exchanged_amount
        if exchange_rate is not None:
            exchanged_amount = round(amount * exchange_rate, 2)
        else:
            exchanged_amount = None  # Handle case where exchange rate is not found

    # Step 6: Form the context and return the template
        context = {
            'currency_choices': currency_choices,
            'amount': amount,
            'currency': currency,
            'exchanged_amount': exchanged_amount,
            'username': request.user.username
    }
    
        return render(request, self.template_name, context)
        '''
            Improve this method:
            1) add the process of forming the variable amount.
            If the amount value from the form is converted to float type, then write the amount value from the form converted to float to the amount variable. Otherwise, write None.
            2) add a currency variable that contains the currency value from the form.
            3) if the variables data or amount contain None, return page with empty context (empty_context). Otherwise, perform the following steps
            4) generate the exchange_rate variable by calculating the corresponding value from the data variable
            5) generate the exchanged_amount variable, which contains the converted currency to two decimal places.
            6) form a context from the previously created variables and return a template with it.
        '''
