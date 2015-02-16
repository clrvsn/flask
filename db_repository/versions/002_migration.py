from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
initiative = Table('initiative', post_meta,
    Column('id', String(length=8), primary_key=True, nullable=False),
    Column('name', String(length=64), nullable=False),
    Column('state', String(length=64), nullable=False),
    Column('start', String(length=24)),
    Column('end', String(length=24)),
    Column('type', String(length=24), nullable=False),
    Column('category', String(length=24), nullable=False),
    Column('program_id', String(length=8)),
    Column('function', String(length=64)),
    Column('objective', Text),
    Column('tp_objective', Text),
    Column('tp_pdi_covered', Boolean),
    Column('tp_scope_covered', Boolean),
    Column('ex_scope_approved', Boolean),
    Column('process_id', String(length=8)),
    Column('demand', String(length=64)),
    Column('solution', String(length=64)),
    Column('biz_arch_man_id', String(length=8)),
    Column('it_arch_man_id', String(length=8)),
    Column('sg_chair_id', String(length=8)),
    Column('sg_sponsor_id', String(length=8)),
    Column('sg_tp_rep_id', String(length=8)),
    Column('orderer_id', String(length=8)),
    Column('owner_id', String(length=8)),
    Column('biz_proj_man_id', String(length=8)),
    Column('it_proj_man_id', String(length=8)),
    Column('forums_anchored', Boolean),
    Column('forums', String(length=64)),
    Column('budget_secured', Boolean),
    Column('approved_by_sg', Boolean),
    Column('approach_approved', Boolean),
    Column('forums_pdi_approved', Boolean),
    Column('it_bluprint_done', Boolean),
    Column('sg_appointed', Boolean),
    Column('funds_secured', Boolean),
    Column('biz_study_done', Boolean),
    Column('solution_study_done', Boolean),
    Column('report_approved', Boolean),
    Column('cost_estimate', String(length=24)),
    Column('time_estimate', String(length=24)),
    Column('projs_mapped', Boolean),
    Column('pro_mapped', Boolean),
    Column('org_mapped', Boolean),
    Column('org_dependence', String(length=64)),
    Column('tec_mapped', Boolean),
    Column('tec_dependence', Boolean),
    Column('pro_impact', Enum('NONE', 'L', 'M', 'H', '?')),
    Column('pro_impact_when', String(length=24)),
    Column('org_impact', Enum('NONE', 'L', 'M', 'H', '?')),
    Column('org_impact_users', String(length=64)),
    Column('org_impact_when', String(length=24)),
    Column('tec_impact', Enum('NONE', 'L', 'M', 'H', '?')),
    Column('tec_impact_when', String(length=24)),
    Column('inf_impact', Enum('NONE', 'L', 'M', 'H', '?')),
    Column('inf_impact_when', String(length=24)),
    Column('gut_feeling', String(length=8)),
    Column('important_milestone', String(length=24)),
    Column('dp1_planned', String(length=32)),
    Column('dp1_actual', String(length=32)),
    Column('dp1_critical', String(length=32)),
    Column('dp3_planned', String(length=32)),
    Column('dp3_actual', String(length=32)),
    Column('dp3_critical', String(length=32)),
    Column('dp6_planned', String(length=32)),
    Column('dp6_actual', String(length=32)),
    Column('dp6_critical', String(length=32)),
    Column('dp8_planned', String(length=32)),
    Column('dp8_actual', String(length=32)),
    Column('dp8_critical', String(length=32)),
    Column('byprog_col', Float),
    Column('byprog_row', Float),
    Column('byprog_txt', String(length=64)),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['initiative'].columns['program_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['initiative'].columns['program_id'].drop()
