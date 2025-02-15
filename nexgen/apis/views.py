from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action

from nexgen import models
from nexgen.apis.serializers import ChatSerializer, ChatMessageSerializer
from nexgen.apis.helpers import (
    generate_graph,
    get_query_results,
    tax_report_generation,
    generate_title,
)
# Create your views here.

class ChatListView(viewsets.ViewSet):
    allow_methods = ['GET', 'POST']
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
    allow_methods = ['GET', 'POST']
    queryset = models.ChatMessage.objects.all()
    serializer_class = ChatMessageSerializer

    def create(self, request, pk=None):
        data = request.data
        chat = request.data.get('ChatID')
        if not chat:
            chat = models.Chat.objects.create(Title = generate_title(request.data.get('Message')))
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
    allow_methods = ['GET', 'POST']
    def create(self, request):
        generate_graph()
        return Response({"message": "Graph generated successfully"})

class GraphQueryViewSet(viewsets.ViewSet):
    allow_methods = ['GET', 'POST']
    def create(self, request):
        chat_id = request.data.get('ChatID')
        query = request.data.get('Query')
        if not query:
            return Response({"error": "Query is required"}, status=400)
        if not chat_id:
            chat = models.Chat.objects.create(Title = generate_title(request.data.get('Query')))
            chat_id = chat.ChatID
        results = get_query_results(query)

        if chat_id:
            models.ChatMessage.objects.create(ChatID_id=chat_id, Message=query, HumanFlag=True)
            models.ChatMessage.objects.create(ChatID_id=chat_id, Message=results, HumanFlag=False)


        return Response({"results": results.response, "chat_id": chat_id})
    

class TextDocumentGenerationViewSet(viewsets.ViewSet):
    allow_methods = ['GET', 'POST']
    def create(self, request):
        text_data = request.data
        if not text_data:
            return Response({"error": "Text data is required"}, status=400)
        
        # Assuming generate_text_document is a helper function that generates a document from text
        document = tax_report_generation(request.data)
        
        return Response({"message": "Document generated successfully", "document": document})
