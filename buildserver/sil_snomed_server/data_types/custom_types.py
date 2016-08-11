import sqlalchemy as sa
from sqlalchemy_utils.types.uuid import UUIDType

class UUID(UUIDType):
  def __repr__(self):
    return "sa.dialects.postgresql.UUID()"
