from django.db import models


class VectorField(models.Field):

    def db_type(self, connection):
        return 'vector'


class TsVectorField(models.Field):
    def db_type(self, connection):
        return 'tsvector'
