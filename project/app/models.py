from django.db import models
from django.contrib.auth.models import User




class History(models.Model):
    STATUS_CHOICES = (
        ('success', 'Success'),
        ('failure', 'Failure'),
    )
    TRANSACTION_CHOICES = (
        ('deposit', 'Deposit'),
        ('debit', 'Debit'),
    )

    status = models.CharField(max_length=10,choices=STATUS_CHOICES)
    amount = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    type = models.CharField(max_length=10,choices=TRANSACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.type} - {self.amount} - {self.status}'

    