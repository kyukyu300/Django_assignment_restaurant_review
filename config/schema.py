from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

schema_view = get_schema_view(
   openapi.Info(
      title="Tasty Restaurant Review API",
      default_version='v1',
      description="맛집을 등록하고 맛집에 대한 리뷰를 남길 수 있습니다.",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="myemail@example.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.IsAdminUser,],
)