from rcportal_migration.settings import CRAMS_DB


class AccountRouter(object):
    """
    A router to control all database operations on models in the
    crams application.
    """
    def db_for_read(self, model, **hints):
        """
        Attempts to read crams models go to CRAMS_DB.
        """
        if model._meta.app_label == 'account':
            return CRAMS_DB
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write crams models go to CRAMS_DB.
        """
        if model._meta.app_label == 'account':
            return CRAMS_DB
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the crams app is involved.
        """
        if obj1._meta.app_label == 'account' or \
           obj2._meta.app_label == 'account':
            return True
        return None

    def allow_migrate(self, db, app_label, model=None, **hints):
        """
        Make sure the crams app only appears in the CRAMS_DB
        database.
        """
        if app_label == 'account':
            return db == CRAMS_DB
        return None
