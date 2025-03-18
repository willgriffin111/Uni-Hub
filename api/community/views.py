from django.shortcuts import render
from rest_framework.views import APIView

# Create your views here.
class community_view_api(APIView):
    def community_view_api(request):
        print("hi")