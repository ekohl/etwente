#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "etwente.settings")

    if 'OPENSHIFT_REPO_DIR' in os.environ:
        sys.path.append(os.path.join(os.environ['OPENSHIFT_REPO_DIR'], 'wsgi',
            'etwente'))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
