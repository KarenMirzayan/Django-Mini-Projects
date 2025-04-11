class DBRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'core':
            if model.__name__ in ['User', 'JobListing']:
                return 'default'
            elif model.__name__ == 'Log':
                return 'mysql'
        return None

    def db_for_write(self, model, **hints):
        return self.db_for_read(model, **hints)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'core':
            if model_name in ['user', 'joblisting']:
                return db == 'default'
            elif model_name == 'log':
                return db == 'mysql'
            elif model_name == 'resume':
                return False  # MongoDB
        return None
