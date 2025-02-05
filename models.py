from neomodel import (StructuredNode, StringProperty, IntegerProperty, RelationshipTo)


class Folder(StructuredNode):
    filepath = StringProperty(unique=True)
    # size = IntegerProperty()
    # disk_usage = IntegerProperty()
    is_in = RelationshipTo('Folder', 'IN')

class File(StructuredNode):
    filepath = StringProperty(unique=True)
    # size = IntegerProperty()
    # disk_usage = IntegerProperty()
    is_in = RelationshipTo('Folder', 'IN')
