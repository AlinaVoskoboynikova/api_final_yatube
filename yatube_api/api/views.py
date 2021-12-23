from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, serializers, viewsets
from rest_framework.pagination import LimitOffsetPagination

from posts.models import Follow, Group, Post, User

from .permissions import AuthorOrReading
from .serializers import (CommentSerializer, FollowSerializer, GroupSerializer,
                          PostSerializer)

User = get_user_model()


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для обработки групп"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


class PostViewSet(viewsets.ModelViewSet):
    """Вьюсет для обработки постов"""
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        AuthorOrReading]

    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = LimitOffsetPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для обработки комментариев"""
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        AuthorOrReading
    ]

    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        return post.comments

    def perform_create(self, serializer):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id)
        serializer.save(author=self.request.user, post=post)


class FollowViewSet(viewsets.ModelViewSet):
    """Вьюсет для обработки подписок"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FollowSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['user__username', 'following__username']

    def get_queryset(self):
        return Follow.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        queryset = Follow.objects.filter(
            user=self.request.user
        )
        if queryset.exists():
            raise serializers.ValidationError(
                'Нельзя повторно подписаться на пользователя'
                'или на самого себя.'
            )
        serializer.save(user=self.request.user)

    # def perform_create(self, serializer):
    #         following = serializer.validated_data.get('following')
    #         queryset = Follow.objects.filter(
    #             user=self.request.user,
    #             following__username=following
    #         )
    #         if queryset.exists():
    #             raise serializers.ValidationError(
    #                 'Нельзя повторно подписаться на пользователя'
    #                 'или на самого себя.'
    #             )
    #         serializer.save(user=self.request.user)
