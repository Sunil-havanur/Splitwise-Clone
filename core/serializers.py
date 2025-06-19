from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Group, GroupMember, Expense, Split
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal
#user serializer basic info

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

#group serializer

class GroupSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ['id', 'name', 'created_at', 'members','member_ids']

    def create(self, validated_data):
        member_ids = validated_data.pop('member_ids', [])
        group = Group.objects.create(**validated_data)

        for user_id in member_ids:
            try:
                user = User.objects.get(id=user_id)
                GroupMember.objects.create(group=group, user=user)
            except ObjectDoesNotExist:
                raise serializers.ValidationError(f"User ID {user_id} does not exist")

        return group  

#group member serializer

class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupMember
        fields = ['id', 'group', 'user', 'joined_at']
        read_only_fields = ['group']

#expense serializer

class ExpenseSerializer(serializers.ModelSerializer):
    paid_by = UserSerializer(read_only=True)
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())

    class Meta:
        model = Expense
        fields = ['id', 'description', 'amount', 'paid_by', 'group', 'split_type', 'created_at']

#Split serializer

class SplitSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    expense = serializers.PrimaryKeyRelatedField(queryset=Expense.objects.all())

    class Meta:
        model = Split
        fields = ['id', 'expense', 'user', 'amount', 'percentage']


class SplitInputSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    percentage = serializers.FloatField(required=False)

class ExpenseCreateSerializer(serializers.ModelSerializer):
    splits = SplitInputSerializer(many=True)
    paid_by_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Expense
        fields = ['id', 'group', 'description', 'amount', 'paid_by_id', 'split_type', 'created_at', 'splits']

    def validate(self, data):
        if data['split_type'] == 'equal':
            if not data.get('splits'):
                raise serializers.ValidationError("Splits are required.")
        elif data['split_type'] == 'percentage':
            total = sum(split['percentage'] for split in data['splits'])
            if total != 100:
                raise serializers.ValidationError("Total percentage must be 100.")
        return data

    def create(self, validated_data):
        splits_data = validated_data.pop('splits')
        paid_by_id = validated_data.pop('paid_by_id')
        paid_by = User.objects.get(id=paid_by_id)

        expense = Expense.objects.create(paid_by=paid_by, **validated_data)

        if expense.split_type == 'equal':
            share = expense.amount / len(splits_data)
            for split in splits_data:
                user = User.objects.get(id=split['user_id'])
                Split.objects.create(expense=expense, user=user, amount=share)
        elif expense.split_type == 'percentage':
            for split in splits_data:
                user = User.objects.get(id=split['user_id'])
                percent = split['percentage']
                amount = (expense.amount * Decimal(percent)) / Decimal(100)
                Split.objects.create(expense=expense, user=user, amount=amount, percentage=percent)

        return expense
