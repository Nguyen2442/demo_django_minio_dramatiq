from rest_framework import status, generics
from rest_framework.response import Response
from core.worker.worker import process_file
from file_handler.utils import get_url_from_minio
from .models import FileTemplate
from .serializers import FileSerializer, GenerateFileSerializer



class FileView(generics.ListCreateAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        return FileTemplate.objects.all()

    def create(self, request, *args, **kwargs):
        file_serializer = self.get_serializer(data=self.request.data)

        if not file_serializer.is_valid():
            return Response(
                {"message": "Created File unsuccessfully!", "success": False},
                status=status.HTTP_400_BAD_REQUEST,
            )
        file_serializer.save()
        
        return Response(
            data={"message": "Created File successfully!", "success": True},
            status=status.HTTP_201_CREATED,
        )
        
class GenerateFileView(generics.ListCreateAPIView):
    serializer_class = GenerateFileSerializer
    queryset = FileTemplate.objects.none()
    
    def create(self, request, *args, **kwargs):
        file_data = request.body
        result = process_file.send(
            {
                "name" : file_data.name,
                "type" : file_data.type
            }
        )
        return Response(
            data={
                    "message" : f"File {file_data.name} will be process soon",
                    "message_id" : result.message_id,
                    "success": True
                },
            status=status.HTTP_201_CREATED,
        )
        
        
class DownloadFileView(generics.ListCreateAPIView):
    serializer_class = GenerateFileSerializer
    queryset = FileTemplate.objects.none()
    
    def create(self, request, *args, **kwargs):
        file_data = request.body
        result = get_url_from_minio(file_data)
        return Response(
            data=result,
            status=status.HTTP_201_CREATED,
        )