from django.db import models
from django.contrib.auth.models import User

class Group(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, through='GroupMember')

    def __str__(self):
        return self.name

class GroupMember(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user')

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"

class Expense(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='expenses_paid')
    split_type = models.CharField(max_length=20, choices=[('equal', 'Equal'), ('percentage', 'Percentage')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description} - {self.amount} in {self.group.name}"

class Split(models.Model):
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE, related_name='splits')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.FloatField(null=True, blank=True)  # Optional: used only for percentage splits

    def __str__(self):
        return f"{self.user.username} owes {self.amount} for {self.expense.description}"

class User(models.Model):
    username = models.CharField(max_length=100)

    def __str__(self):
        return self.username