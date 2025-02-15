from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from nexgen import models
from nexgen.apis.serializers import ChatSerializer, ChatMessageSerializer
from nexgen.apis.helpers import (
    generate_graph,
    get_query_results,
)
# Create your views here.

class ChatListView(viewsets.ViewSet):
    def list(self, request):
        queryset = models.Chat.objects.all()
        serializer = ChatSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = ChatSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class ChatManagementViewSet(viewsets.ModelViewSet):
    queryset = models.ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def create(self, request, pk=None):
        data = request.data
        chat = request.data.get('ChatID')
        if not chat:
            chat = models.Chat.objects.create(Title = request.data.get('Message'))
            data['ChatID'] = chat.ChatID
        else:
            chat = models.Chat.objects.get(ChatID=chat)
            data['ChatID'] = chat.ChatID
        serializer = ChatMessageSerializer(data=data)
        if serializer.is_valid():
            chat_message = serializer.save(ChatID=chat)
            return Response(ChatMessageSerializer(chat_message).data, status=201)
        return Response(serializer.errors, status=400)

    def list(self, request):
        queryset = models.ChatMessage.objects.all()
        serializer = ChatMessageSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def get_chat_messages(self, request, pk=None):
        chat_id = pk
        print(chat_id)
        chat_messages = models.ChatMessage.objects.filter(ChatID=chat_id)
        serializer = ChatMessageSerializer(chat_messages, many=True)
        return Response(serializer.data)
    
class GraphGeneratorViewSet(viewsets.ViewSet):
    def create(self, request):
        generate_graph()
        return Response({"message": "Graph generated successfully"})

class GraphQueryViewSet(viewsets.ViewSet):
    def create(self, request):
        query = request.data.get('Query')
        if not query:
            return Response({"error": "Query is required"}, status=400)
        
        results = get_query_results(query)
        return Response(results)
