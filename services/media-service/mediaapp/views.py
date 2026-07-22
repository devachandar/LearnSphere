from django.http import FileResponse, Http404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import MediaFile
from .permissions import IsAuthenticatedStateless
from .storage import UPLOAD_DIR, save_file

ALLOWED_TYPES = {"video/mp4", "video/webm", "application/pdf", "image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 200 * 1024 * 1024
MAX_FILES = 5


class UploadView(APIView):
    permission_classes = [IsAuthenticatedStateless]
    parser_classes = [MultiPartParser]

    def post(self, request):
        files = request.FILES.getlist("files")
        if not files:
            return Response({"error": "No valid files were provided under the 'files' field"}, status=400)
        if len(files) > MAX_FILES:
            return Response({"error": f"You can upload at most {MAX_FILES} files at once"}, status=400)

        results = []
        for f in files:
            if f.content_type not in ALLOWED_TYPES or f.size > MAX_SIZE:
                continue
            url = save_file(f)
            record = MediaFile.objects.create(
                uploader_id=request.user.id,
                organization_id=request.user.organization_id,
                url=url,
                content_type=f.content_type,
                original_name=f.name,
            )
            results.append(
                {"id": str(record.id), "url": record.url, "content_type": record.content_type, "original_name": record.original_name}
            )

        if not results:
            return Response({"error": "No valid files were provided under the 'files' field"}, status=400)
        return Response({"files": results}, status=201)


class MyUploadsView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        qs = MediaFile.objects.filter(uploader_id=request.user.id).order_by("-created_at")
        return Response(
            [
                {"id": str(m.id), "url": m.url, "content_type": m.content_type, "original_name": m.original_name, "created_at": m.created_at}
                for m in qs
            ]
        )


class ServeUploadView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, filename):
        import os

        path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.isfile(path):
            raise Http404
        return FileResponse(open(path, "rb"))
