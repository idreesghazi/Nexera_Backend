from django.db import models

# Create your models here.
class Chat(models.Model):
    ChatID = models.AutoField(primary_key=True)
    Title = models.CharField(max_length=255)
    CreatedAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.Title


class ChatMessage(models.Model):
    ChatMessageID = models.AutoField(primary_key=True)
    ChatID = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    Message = models.TextField()
    CreatedAt = models.DateTimeField(auto_now_add=True)
    HumanFlag = models.BooleanField(default=True)

    def __str__(self):
        return self.Message[:50]
    

class GraphData(models.Model):
    DOMAIN = models.CharField(max_length=255)
    QUERIES = models.JSONField()
    ENTITY_TYPES = models.JSONField()

    def __str__(self):
        return self.DOMAIN