#!/usr/bin/env python
import hashlib
import inspect
import os
import random
import sys

from django.core.exceptions import ImproperlyConfigured


# See https://www.openshift.com/page/openshift-environment-variables


ON_OPENSHIFT = 'OPENSHIFT_APP_NAME' in os.environ

# TODO: On python 2.7+ an OrderedDict would be better
DATABASE_ENGINES = (
        ('POSTGRESQL', 'django.db.backends.postgresql_psycopg2'),
        ('MYSQL', 'django.db.backends.mysql'),
)


# Gets the secret token provided by OpenShift
# or generates one (this is slightly less secure, but good enough for now)
def get_openshift_secret_token():
    token = os.getenv('OPENSHIFT_SECRET_TOKEN')
    name = os.getenv('OPENSHIFT_APP_NAME')
    uuid = os.getenv('OPENSHIFT_APP_UUID')
    if token is not None:
        return token
    elif (name is not None and uuid is not None):
        return hashlib.sha256(name + '-' + uuid).hexdigest()
    return None


# This function transforms default keys into per-deployment random keys;
def make_secure_key(key_info):
    hashcode = key_info['hash']
    original = key_info['original']

    # These are the legal password characters
    # as per the Django source code
    # (django/contrib/auth/models.py)
    chars = 'abcdefghjkmnpqrstuvwxyz'
    chars += 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    chars += '23456789'

    # Use the hash to seed the RNG
    random.seed(int("0x" + hashcode[:8], 0))

    # Create a random string the same length as the default
    rand_key = ''.join(random.choice(chars) for _ in range(len(original)))

    # Reset the RNG
    random.seed()

    # Set the value
    return rand_key


# Loop through all provided variables and generate secure versions
# If not running on OpenShift, returns defaults and logs an error message
#
# This function calls secure_function and passes an array of:
#  {
#    'hash':     generated sha hash,
#    'variable': name of variable,
#    'original': original value
#  }
def openshift_secure(default_keys, secure_function=make_secure_key):
    # Attempts to get secret token
    my_token = get_openshift_secret_token()

    # Only generate random values if on OpenShift
    my_list = default_keys

    if my_token is not None:
        # Loop over each default_key and set the new value
        for key, value in default_keys.iteritems():
            # Create hash out of token and this key's name
            sha = hashlib.sha256(my_token + '-' + key).hexdigest()
            # Pass a dictionary so we can add stuff without breaking existing calls
            vals = {'hash': sha, 'variable': key, 'original': value}
            # Call user specified function or just return hash
            my_list[key] = sha
            if secure_function is not None:
                my_list[key] = secure_function(vals)
    else:
        calling_file = inspect.stack()[1][1]
        if os.getenv('OPENSHIFT_REPO_DIR'):
            base = os.getenv('OPENSHIFT_REPO_DIR')
            calling_file.replace(base, '')
        sys.stderr.write("OPENSHIFT WARNING: Using default values for secure variables, please manually modify in " + calling_file + "\n")

    return my_list


def get_database_config(database_server, engine=None):
    prefix = 'OPENSHIFT_' + database_server + '_DB_'

    if prefix + 'URL' not in os.environ:
        raise ImproperlyConfigured('Database server %s is not configured' %
                database_server)

    if not engine:
        try:
            engine = dict(DATABASE_ENGINES)[database_server]
        except KeyError:
            raise ValueError('No engine passed in for unknown server %s' %
                    database_server)

    return {
        'ENGINE': engine,
        'NAME': os.environ['OPENSHIFT_APP_NAME'],
        'USER': os.environ[prefix + 'USERNAME'],
        'PASSWORD': os.environ[prefix + 'PASSWORD'],
        'HOST': os.environ[prefix + 'HOST'],
        'PORT': os.environ[prefix + 'PORT'],
    }


def get_databases_config():
    """
    Get the database configuration.

    To do this, it iterates DATABASE_ENGINES and uses the first one where
    OPENSHIFT_key_DB_URL is found in the environment. If none is found, sqlite3
    is used.
    """

    # https://docs.djangoproject.com/en/dev/ref/settings/#databases
    # https://www.openshift.com/page/openshift-environment-variables#Database

    for database, engine in DATABASE_ENGINES:
        prefix = 'OPENSHIFT_' + database + '_DB_'
        if prefix + 'URL' in os.environ:
            default = {
                'ENGINE': engine,
                'NAME': os.environ['OPENSHIFT_APP_NAME'],
                'USER': os.environ[prefix + 'USERNAME'],
                'PASSWORD': os.environ[prefix + 'PASSWORD'],
                'HOST': os.environ[prefix + 'HOST'],
                'PORT': os.environ[prefix + 'PORT'],
            }
            break
    else:
        default = {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(os.environ['OPENSHIFT_DATA_DIR'],
                    'sqlite3.db'),
        }

    return {'default': default}


def get_secret_key(default):
    """
    Return a secret key.

    See https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
    """
    return openshift_secure({'SECRET_KEY': default})['SECRET_KEY']
