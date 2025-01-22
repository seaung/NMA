from rest_framework import viewsets, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone

from app.models.workflow.ticket import VulnerabilityTicket, TicketHistory, TicketComment
from .serializers import VulnerabilityTicketSerializer, TicketHistorySerializer, TicketCommentSerializer


class VulnerabilityTicketViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    serializer_class = VulnerabilityTicketSerializer
    queryset = VulnerabilityTicket.objects.all()

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_queryset(self):
        user = self.request.user
        return VulnerabilityTicket.objects.filter(creator=user) | VulnerabilityTicket.objects.filter(assignee=user)

    @action(detail=True, methods=['post'])
    def assign(self, request: Request, pk=None) -> Response:
        ticket = self.get_object()
        assignee_id = request.data.get('assignee_id')
        
        if not assignee_id:
            return Response({'error': '处理人ID不能为空'}, status=status.HTTP_400_BAD_REQUEST)
        
        old_status = ticket.status
        ticket.status = 'assigned'
        ticket.assignee_id = assignee_id
        ticket.save()

        TicketHistory.objects.create(
            ticket=ticket,
            operator=request.user,
            action='assign',
            old_status=old_status,
            new_status='assigned',
            comment=f'分配给用户ID: {assignee_id}'
        )

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def change_status(self, request: Request, pk=None) -> Response:
        ticket = self.get_object()
        new_status = request.data.get('status')
        comment = request.data.get('comment', '')

        if new_status not in dict(VulnerabilityTicket.STATUS_CHOICES):
            return Response({'error': '无效的状态'}, status=status.HTTP_400_BAD_REQUEST)

        old_status = ticket.status
        ticket.status = new_status
        
        if new_status == 'resolved':
            ticket.resolution = request.data.get('resolution', '')
        
        ticket.save()

        TicketHistory.objects.create(
            ticket=ticket,
            operator=request.user,
            action='change_status',
            old_status=old_status,
            new_status=new_status,
            comment=comment
        )

        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def add_comment(self, request: Request, pk=None) -> Response:
        ticket = self.get_object()
        content = request.data.get('content')

        if not content:
            return Response({'error': '评论内容不能为空'}, status=status.HTTP_400_BAD_REQUEST)

        TicketComment.objects.create(
            ticket=ticket,
            author=request.user,
            content=content
        )

        return Response(status=status.HTTP_201_CREATED)