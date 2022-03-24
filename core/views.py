from rest_framework import viewsets
from .serializers import *
from rest_framework.response import Response
from django.shortcuts import get_object_or_404


class DistributionStatsView(viewsets.ModelViewSet):

    queryset = Distribution.objects.all()
    serializer_class = DistributionSerializer

    def statistic(self, request, pk=None):
        queryset = self.queryset
        distribution = get_object_or_404(queryset, pk=pk)
        serializer = self.serializer_class(distribution)
        return Response(serializer.data)

    def all_statistic(self, request):
        queryset = self.queryset
        serializer = DistributionSerializer(queryset, many=True)
        return Response(serializer.data)


class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer


class MessageViewSet(viewsets.ModelViewSet):

    queryset = Message.objects.all()
    serializer_class = MessageSerializer


class OperatorViewSet(viewsets.ModelViewSet):

    queryset = Operator.objects.all()
    serializer_class = OperatorSerializer


class TagViewSet(viewsets.ModelViewSet):

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
