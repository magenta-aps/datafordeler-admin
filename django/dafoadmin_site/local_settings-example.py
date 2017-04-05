DATABASES = {
    'default': {
        'NAME': 'dafo_users',
        'ENGINE': 'sqlserver_ado',
        'HOST': '127.0.0.1',
        'PORT': '1433',
        'USER': 'dafo_useradmin',
        'PASSWORD': 'dafo_useradmin',
        'OPTIONS': {
            'provider': 'SQLOLEDB',
            'use_legacy_date_fields': 'True'
        }
    }
}