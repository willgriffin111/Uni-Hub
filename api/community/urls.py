from django.urls import path
from .views import CreateCommunityView

urlpatterns = [
    # POST /api/community/community/ to create a new community.
    path('community/', CreateCommunityView.as_view(), name="community-create"),
]
