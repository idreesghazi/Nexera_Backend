from django.urls import path, include
from rest_framework import routers
from nexgen.apis import views

router = routers.DefaultRouter()

router.register(r'ChatList', views.ChatListView, basename='ChatList')
router.register(r'Chat', views.ChatManagementViewSet, basename='Chat')
router.register(r'Graph', views.GraphGeneratorViewSet, basename='Graph')
router.register(r'GraphChat', views.GraphQueryViewSet, basename='GraphChat')
router.register(r'TaxReportGenerate', views.TextDocumentGenerationViewSet, basename='TaxReportGenerate')
router.register(r'DocumentGraph', views.DocumentGraphGenerationViewSet, basename='DocumentGraph')
router.register(r'Insights', views.LitigationSupportViewSet, basename='Insights')
urlpatterns = [
    path('', include(router.urls)),
]