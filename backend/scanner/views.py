from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.permissions import IsInspectorOfficer

class ScannerStatusView(APIView):
    """
    Placeholder endpoint for commodity scanner services (to be implemented in Prompt 2+).
    """
    permission_classes = [IsInspectorOfficer]

    def get(self, request):
        return Response(
            {
                "module": "scanner",
                "status": "scaffolded",
                "phase": "Prompt 1/15 Foundation",
                "message": "Commodity scanner module ready for OCR & image capture pipeline implementation."
            },
            status=status.HTTP_200_OK
        )
