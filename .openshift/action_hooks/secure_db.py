#!/usr/bin/env python
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
except ImportError:  # Before Django 1.5
    from django.contrib.auth.models import User

from django.contrib.auth.hashers import get_random_string, make_password

password = get_random_string(12)
user, created = User.objects.get_or_create(username='admin',
        defaults={'password': make_password(password)})
if created:
    print "Django application credentials:\n\tuser: admin\n\t" + password
