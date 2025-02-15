from rest_framework import serializers
from nexgen import models

class ChatSerializer(serializers.ModelSerializer):
    Title = serializers.CharField(max_length=255, default='Default Title')
    class Meta:
        model = models.Chat
        fields = ['ChatID', 'Title', 'CreatedAt']

class ChatMessageSerializer(serializers.ModelSerializer):
    ChatID = serializers.PrimaryKeyRelatedField(queryset=models.Chat.objects.all(), source='chat', allow_null=True)
    class Meta:
        model = models.ChatMessage
        fields = '__all__'