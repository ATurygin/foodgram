from functools import wraps

from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError


def m2m_set(related_manager_name, already_added_err):
    def m2m_set_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            view = args[0]
            request = args[1]
            obj = view.get_object()
            manager = getattr(request.user, related_manager_name)
            if obj in manager.all():
                raise ValidationError(already_added_err)
            func(*args, **kwargs)
            manager.add(obj)
            serializer = view.get_serializer(instance=obj,
                                             context={'request': request})
            return Response(serializer.data,
                            status=status.HTTP_201_CREATED)
        return inner
    return m2m_set_wrapper


def m2m_unset(related_manager_name, delete_nonexist_err):
    def m2m_unset_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            view = args[0]
            request = args[1]
            obj = view.get_object()
            manager = getattr(request.user, related_manager_name)
            if obj not in manager.all():
                raise ValidationError(delete_nonexist_err)
            func(*args, **kwargs)
            manager.remove(obj)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return inner
    return m2m_unset_wrapper
