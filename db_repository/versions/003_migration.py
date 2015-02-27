from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
dependency = Table('dependency', post_meta,
    Column('id', String(length=8), primary_key=True, nullable=False),
    Column('from_init_id', String(length=8)),
    Column('to_init_id', String(length=8)),
    Column('type', Enum('HARD', 'SOFT')),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['dependency'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['dependency'].drop()
