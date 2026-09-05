from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from users.permissions import IsInspectorOfficer

from scanner.models import Inspection
from scanner.audit import record_audit
from .models import ComplianceEvaluation, Rule
from .serializers import ComplianceEvaluationSerializer, RuleSerializer
from .services.rule_engine import save_evaluation

class ComplianceStatusView(APIView):
    """
    Placeholder endpoint for Legal Metrology compliance rules engine (to be implemented in Prompt 2+).
    """
    permission_classes = [IsInspectorOfficer]

    def get(self, request):
        return Response(
            {
                "module": "compliance",
                "status": "scaffolded",
                "phase": "Prompt 1/15 Foundation",
                "rules_reference": "Legal Metrology (Packaged Commodities) Rules, 2011",
                "message": "Compliance evaluation engine ready for rule definitions & verification."
            },
            status=status.HTTP_200_OK
        )


def owned_inspection(request, inspection_id):
    queryset = Inspection.objects.all()
    profile = getattr(request.user, "officer_profile", None)
    if not profile or profile.role != "ADMIN":
        queryset = queryset.filter(officer=request.user)
    try:
        return queryset.get(inspection_id=inspection_id)
    except Inspection.DoesNotExist:
        raise PermissionDenied("Inspection not found or not accessible.")


class RuleListView(generics.ListAPIView):
    permission_classes = [IsInspectorOfficer]
    serializer_class = RuleSerializer
    queryset = Rule.objects.filter(is_active=True)


class ComplianceEvaluateView(APIView):
    permission_classes = [IsInspectorOfficer]

    def post(self, request, inspection_id):
        inspection = owned_inspection(request, inspection_id)
        evaluation, applicability = save_evaluation(inspection)
        record_audit(request, inspection, "COMPLIANCE_RE_RUN" if evaluation.evaluation_version > 1 else "COMPLIANCE_RUN", "Compliance evaluation completed.", {"evaluation_version": evaluation.evaluation_version, "overall_status": evaluation.overall_status})
        return Response({"applicability": applicability, "evaluation": ComplianceEvaluationSerializer(evaluation).data}, status=status.HTTP_200_OK)


class ComplianceDetailView(APIView):
    permission_classes = [IsInspectorOfficer]

    def get(self, request, inspection_id):
        inspection = owned_inspection(request, inspection_id)
        evaluation = inspection.compliance_evaluations.filter(is_current=True).first()
        if not evaluation:
            return Response({"message": "Compliance has not been evaluated yet."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ComplianceEvaluationSerializer(evaluation).data)


class ComplianceSummaryView(APIView):
    permission_classes = [IsInspectorOfficer]

    def get(self, request, inspection_id):
        inspection = owned_inspection(request, inspection_id)
        evaluation = inspection.compliance_evaluations.filter(is_current=True).first()
        if not evaluation:
            return Response({"message": "Compliance has not been evaluated yet."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ComplianceEvaluationSerializer(evaluation).data)
