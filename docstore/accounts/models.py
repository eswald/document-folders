from uuid import uuid4

from django.db.models.deletion import PROTECT
from django.db.models.fields import CharField, UUIDField
from django.db.models.fields.related import ForeignKey

from ..libs.models import BasicModel


class Account(BasicModel):
    name = CharField(max_length=127)
    
    def __str__(self):
        return super().__str__() + ': ' + repr(self.name)


class Token(BasicModel):
    account = ForeignKey(Account, on_delete=PROTECT)
    uuid = UUIDField(default=uuid4, editable=False, db_index=True)
    
    def __str__(self):
        return super().__str__() + ': ' + str(self.token)
