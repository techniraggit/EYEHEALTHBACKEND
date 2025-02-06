from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
from api.models.eye_health import UserModel, UserTestProfile, EyeTestReport
import os


class EyeTestRecordSerializer(serializers.Serializer):
    user_id = serializers.UUIDField(required=True)
    report_id = serializers.CharField(required=False)
    full_name = serializers.CharField(required=True)
    age = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    right_eye = serializers.JSONField()
    left_eye = serializers.JSONField()
    health_score = serializers.FloatField(required=True)
    colour_contrast = serializers.CharField(required=False)
    color_blindness = serializers.CharField(required=False)

    def create(self, validated_data):
        user_id = validated_data.get('user_id', None)
        user_obj = UserModel.objects.get(id=user_id)
        user_profile = UserTestProfile.objects.create(
            user=user_obj,
            full_name=validated_data.get('full_name', ''),
            age=validated_data.get('age', ''),
            email=validated_data.get('email', ''),
            phone_number=validated_data.get('phone_number', ''),
        )

        data = dict(
            report_id=validated_data.get('report_id', 0),
            user_profile=user_profile,
            right_eye=validated_data.get('right_eye', {}),
            left_eye=validated_data.get('left_eye', {}),
            health_score=validated_data.get('health_score', 0),
            colour_contrast=validated_data.get("colour_contrast"),
            color_blindness=validated_data.get("color_blindness"),
        )
        return EyeTestReport.objects.create(**data)


    def validate_user_id(self, validated_data):
        user_id = validated_data
        user_obj = UserModel.objects.filter(id=user_id).first()
        if not user_obj:
            raise serializers.ValidationError("User not found.")
        return user_id
    
    def validate_report_id(self, validated_data):
        report_id = validated_data
        if EyeTestReport.objects.filter(report_id=report_id).exists():
            raise serializers.ValidationError("Report with this id already exists.")
        return report_id


class InsertEyeTestRecord(APIView):
    def post(self, request):
        authorization_key = request.headers.get("Authorization")
        if not authorization_key:
            return Response({"status": "error", "message": "Authorization key is required."}, status=401)

        if authorization_key != os.environ.get("EYE_TEST_WEBHOOK_STATIC_KEY"):
            return Response({"status": "error", "message": "Invalid authorization key."}, status=403)

        serializer = EyeTestRecordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "success"}, status=201)
        else:
            return Response({"status": "error", "errors": serializer.errors}, status=400)