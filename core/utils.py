# core/utils.py
from django.db.models import Sum
from decimal import Decimal
from .models import Group, Expense, Split

def calculate_group_balances(group_id):
    try:
        group = Group.objects.get(id=group_id)
    except Group.DoesNotExist:
        return {"error": "Group not found"}

    users = group.members.all()
    balances = {}

    for user in users:
        paid = Expense.objects.filter(group=group, paid_by=user).aggregate(total=Sum('amount'))['total'] or Decimal(0)
        owed = Split.objects.filter(expense__group=group, user=user).aggregate(total=Sum('amount'))['total'] or Decimal(0)
        balances[user.username] = round(paid - owed, 2)

    # Format as 'X owes Y ₹Z'
    transactions = []
    usernames = list(balances.keys())
    amounts = list(balances.values())

    for i in range(len(usernames)):
        for j in range(len(usernames)):
            if amounts[i] < 0 and amounts[j] > 0:
                amount_to_pay = min(abs(amounts[i]), amounts[j])
                transactions.append(f"{usernames[i]} owes {usernames[j]} ₹{amount_to_pay:.2f}")
                amounts[i] += amount_to_pay
                amounts[j] -= amount_to_pay

    return {"balances": transactions}
