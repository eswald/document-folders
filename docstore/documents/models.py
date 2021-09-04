from django.db.models.deletion import PROTECT
from django.db.models.fields import CharField, TextField
from django.db.models.fields.related import ForeignKey

from ..accounts.models import Account
from ..libs.models import BasicModel


class Document(BasicModel):
    account = ForeignKey(Account, on_delete=PROTECT)
    name = CharField(max_length=127)
    content = TextField()
    
    def __str__(self):
        return super().__str__() + ': ' + repr(self.name)
