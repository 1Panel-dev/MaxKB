from django.db import models


class VectorField(models.Field):

    def db_type(self, connection):
        return 'vector'
