
class PersonaLiteRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'database' and model.__name__ == 'PersonaLite':
            return 'otra_db'  # lectura en la segunda BD
        return None  # usa la lógica por defecto (default)

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'database' and model.__name__ == 'PersonaLite':
            return 'otra_db'  # escritura en la segunda BD
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'database' and model_name == 'personalite':
            return db == 'otra_db'
        return db == 'default'


