from django.shortcuts import render, redirect, get_object_or_404
from collections import defaultdict
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import generics, status
from .models import Group, Expense, Split, User
from .serializers import GroupSerializer, ExpenseCreateSerializer
from django.db.models import Sum
from .forms import GroupForm, ExpenseForm
from decimal import Decimal

@api_view(['GET'])
def api_overview(request):
    return Response({"message": "Splitwise API is running!"})


class GroupCreateView(generics.CreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

@api_view(['POST'])
def create_group_api(request):
    serializer = GroupSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ExpenseCreateView(generics.CreateAPIView):
    queryset = Expense.objects.all()
    serializer_class = ExpenseCreateSerializer

class GroupBalanceView(APIView):
    def get(self, request, group_id):
        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            return Response({"error": "Group not found"}, status=404)

        users = group.members.all()
        balances = {}

        for user in users:
            paid = Expense.objects.filter(group=group, paid_by=user).aggregate(total=Sum('amount'))['total'] or 0
            owed = Split.objects.filter(expense__group=group, user=user).aggregate(total=Sum('amount'))['total'] or 0
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

        return Response({"balances": transactions})


class UserBalanceView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        groups = Group.objects.filter(members=user)
        total_paid = Expense.objects.filter(group__in=groups, paid_by=user).aggregate(total=Sum('amount'))['total'] or 0
        total_owed = Split.objects.filter(user=user, expense__group__in=groups).aggregate(total=Sum('amount'))['total'] or 0

        return Response({
            "user": user.username,
            "total_paid": total_paid,
            "total_owed": total_owed,
            "net_balance": round(total_paid - total_owed, 2)
        })

def create_group_view(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('create-group')
    else:
        form = GroupForm()
    return render(request, 'create_group.html', {'form': form})

def add_expense(request):
    if request.method == "POST":
        form = ExpenseForm(request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            description = form.cleaned_data['description']
            amount = form.cleaned_data['amount']
            paid_by = form.cleaned_data['paid_by']
            split_type = form.cleaned_data['split_type']
            members = form.cleaned_data['members']
            percentages = form.cleaned_data['percentages']

            expense = Expense.objects.create(
                group=group, description=description,
                amount=amount, paid_by=paid_by, split_type=split_type
            )

            if split_type == 'equal':
                per_head = amount / members.count()
                for user in members:
                    Split.objects.create(expense=expense, user=user, amount=per_head)
            elif split_type == 'percentage':
                perc_list = [Decimal(p.strip()) for p in percentages.split(",")]
                for user, perc in zip(members, perc_list):
                    amt = (amount * perc) / Decimal(100)
                    Split.objects.create(expense=expense, user=user, amount=amt, percentage=perc)

            return redirect('add-expense')
    else:
        form = ExpenseForm()
    
    return render(request, 'add_expense.html', {'form': form})

def group_balances_page(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    expenses = group.expense_set.all()

    # Track how much each user paid and owes
    paid = defaultdict(float)
    owed = defaultdict(float)

    for expense in expenses:
        paid[expense.paid_by.username] += float(expense.amount)
        for split in expense.splits.all():
            owed[split.user.username] += float(split.amount)

    balances = []
    for user in group.members.all():
        username = user.username
        net = paid[username] - owed[username]
        if net < 0:
            balances.append(f"{username} owes ₹{abs(net):.2f}")
        elif net > 0:
            balances.append(f"{username} is owed ₹{net:.2f}")
        else:
            balances.append(f"{username} is settled up")

    return render(request, 'group_balances.html', {'balances': balances})

def user_summary_page(request, user_id):
    user = get_object_or_404(User, id=user_id)

    total_paid = 0
    total_owed = 0

    # Get all expenses where this user paid
    paid_expenses = Expense.objects.filter(paid_by=user)
    for expense in paid_expenses:
        total_paid += float(expense.amount)

    # Get all splits where this user owes money
    owed_splits = Split.objects.filter(user=user)
    for split in owed_splits:
        total_owed += float(split.amount)

    net_balance = total_paid - total_owed

    summary = {
        "user": user.username,
        "total_paid": total_paid,
        "total_owed": total_owed,
        "net_balance": net_balance
    }

    return render(request, 'user_summary.html', {'summary': summary})

def dashboard(request):
    context = {
        'group_count': Group.objects.count(),
        'user_count': User.objects.count(),
        'recent_expenses': Expense.objects.order_by('-created_at')[:5],
    }
    return render(request, 'dashboard.html', context)