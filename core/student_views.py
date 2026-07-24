from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.mixins import CreateModelMixin
from django.shortcuts import get_object_or_404
from .models import (
    Student, Passport, Health, Military, Family,
    FamilyMember, EducationInstitution
)
from .student_serializers import (
    StudentProfileSerializer, PassportSerializer, HealthSerializer,
    MilitarySerializer, FamilySerializer, FamilyMemberSerializer,
    EducationInstitutionSerializer
)


class StudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(Student, user=self.request.user)


class PassportView(CreateModelMixin, generics.RetrieveUpdateAPIView):
    serializer_class = PassportSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        student = get_object_or_404(Student, user=self.request.user)
        passport, created = Passport.objects.get_or_create(
            pk=student.passport_id
        ) if student.passport_id else (Passport.objects.create(), True)
        if created and not student.passport_id:
            student.passport = passport
            student.save()
        return passport
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        student = get_object_or_404(Student, user=self.request.user)
        context['student'] = student
        return context
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        student = get_object_or_404(Student, user=self.request.user)
        instance = serializer.save()
        student.passport = instance
        student.save()


class HealthView(CreateModelMixin, generics.RetrieveUpdateAPIView):
    serializer_class = HealthSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        student = get_object_or_404(Student, user=self.request.user)
        health, created = Health.objects.get_or_create(
            pk=student.health_id
        ) if student.health_id else (Health.objects.create(), True)
        if created and not student.health_id:
            student.health = health
            student.save()
        return health
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        student = get_object_or_404(Student, user=self.request.user)
        instance = serializer.save()
        student.health = instance
        student.save()


class MilitaryView(CreateModelMixin, generics.RetrieveUpdateAPIView):
    serializer_class = MilitarySerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        student = get_object_or_404(Student, user=self.request.user)
        military, created = Military.objects.get_or_create(
            pk=student.military_id
        ) if student.military_id else (Military.objects.create(), True)
        if created and not student.military_id:
            student.military = military
            student.save()
        return military
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        student = get_object_or_404(Student, user=self.request.user)
        instance = serializer.save()
        student.military = instance
        student.save()


class FamilyView(CreateModelMixin, generics.RetrieveUpdateAPIView):
    serializer_class = FamilySerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        student = get_object_or_404(Student, user=self.request.user)
        family, created = Family.objects.get_or_create(
            pk=student.family_id
        ) if student.family_id else (Family.objects.create(), True)
        if created and not student.family_id:
            student.family = family
            student.save()
        return family
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        student = get_object_or_404(Student, user=self.request.user)
        instance = serializer.save()
        student.family = instance
        student.save()


class FamilyMemberListCreateView(generics.ListCreateAPIView):
    serializer_class = FamilyMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        student = get_object_or_404(Student, user=self.request.user)
        # Автоматически создаём семью, если её нет
        if not student.family_id:
            family = Family.objects.create()
            student.family = family
            student.save()
        context['family'] = student.family
        return context
    
    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        if not student.family_id:
            return FamilyMember.objects.none()
        return FamilyMember.objects.filter(family=student.family)
    
    def perform_create(self, serializer):
        student = get_object_or_404(Student, user=self.request.user)
        serializer.save(family=student.family)


class FamilyMemberDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FamilyMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        if not student.family_id:
            return FamilyMember.objects.none()
        return FamilyMember.objects.filter(family=student.family)


class EducationInstitutionView(CreateModelMixin, generics.RetrieveUpdateAPIView):
    serializer_class = EducationInstitutionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        student = get_object_or_404(Student, user=self.request.user)
        context['student'] = student
        return context
    
    def get_object(self):
        student = get_object_or_404(Student, user=self.request.user)
        education, created = EducationInstitution.objects.get_or_create(
            pk=student.education_id
        ) if student.education_id else (EducationInstitution.objects.create(), True)
        if created and not student.education_id:
            student.education = education
            student.save()
        return education
    
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        student = get_object_or_404(Student, user=self.request.user)
        instance = serializer.save()
        student.education = instance
        student.save()
