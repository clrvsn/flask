#-------------------------------------------------------------------------------
# Name:        models
# Purpose:
#
# Author:      MAKEE2
#
# Created:     12-02-2015
# Copyright:   (c) MAKEE2 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------

from app import db

class Person(db.Model): # PSN
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(64))


class Process(db.Model): # PCS
    id = db.Column(db.String(8), primary_key=True)
    title = db.Column(db.Text, nullable=False)
    level = db.Column(db.Integer, nullable=False)
    owner_id = db.Column(db.String(8), db.ForeignKey('person.id'))
    leader_id = db.Column(db.String(8), db.ForeignKey('person.id'))

    owner = db.relationship('Person', backref='owns_procs', foreign_keys=[owner_id])#, lazy='dynamic')
    leader = db.relationship('Person', backref='leads_procs', foreign_keys=[leader_id])#, lazy='dynamic')


class Program(db.Model): # PGM
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(64), nullable=False)


class Initiative(db.Model): # NTV
    id = db.Column(db.String(8), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    state = db.Column(db.String(64), nullable=False)
    start = db.Column(db.String(24))
    end = db.Column(db.String(24))
    type = db.Column(db.String(24), nullable=False)
    category = db.Column(db.String(24), nullable=False)
    program_id = db.Column(db.String(8), db.ForeignKey('program.id'))#, nullable=False)
    program = db.relationship('Program', backref='initiatives')
    function = db.Column(db.String(64))
    objective  = db.Column(db.Text)
    tp_objective = db.Column(db.Text)
    tp_pdi_covered = db.Column(db.Boolean)
    tp_scope_covered = db.Column(db.Boolean)
    ex_scope_approved = db.Column(db.Boolean)
    process_id = db.Column(db.String(8), db.ForeignKey('process.id'))
    process = db.relationship('Process', backref='initiatives') #, lazy='dynamic')
    demand = db.Column(db.String(64))
    solution = db.Column(db.String(64))
    biz_arch_man_id = db.Column(db.String(8), db.ForeignKey('person.id'))
    it_arch_man_id = db.Column(db.String(8), db.ForeignKey('person.id'))
    sg_chair_id = db.Column(db.String(8), db.ForeignKey('person.id'))
    sg_sponsor_id = db.Column(db.String(8), db.ForeignKey('person.id'))
    sg_tp_rep_id = db.Column(db.String(8), db.ForeignKey('person.id'))
    orderer_id = db.Column(db.String(8), db.ForeignKey('person.id'))
    owner_id = db.Column(db.String(8), db.ForeignKey('person.id'))
    biz_proj_man_id = db.Column(db.String(8), db.ForeignKey('person.id'))
    it_proj_man_id = db.Column(db.String(8), db.ForeignKey('person.id'))
    biz_arch_man = db.relationship('Person', backref='biz_arch_man_of', foreign_keys=[biz_arch_man_id])#, lazy='dynamic')
    it_arch_man = db.relationship('Person', backref='it_arch_man_of', foreign_keys=[it_arch_man_id])#, lazy='dynamic')
    sg_chair = db.relationship('Person', backref='sg_chair_of', foreign_keys=[sg_chair_id])#, lazy='dynamic')
    sg_sponsor = db.relationship('Person', backref='sg_sponsor_of', foreign_keys=[sg_sponsor_id])#, lazy='dynamic')
    sg_tp_rep = db.relationship('Person', backref='sg_tp_rep_of', foreign_keys=[sg_tp_rep_id])#, lazy='dynamic')
    orderer = db.relationship('Person', backref='orderer_of', foreign_keys=[orderer_id])#, lazy='dynamic')
    owner = db.relationship('Person', backref='owns_inits', foreign_keys=[owner_id])#, lazy='dynamic')
    biz_proj_man = db.relationship('Person', backref='biz_proj_man_of', foreign_keys=[biz_proj_man_id])#, lazy='dynamic')
    it_proj_man = db.relationship('Person', backref='it_proj_man_of', foreign_keys=[it_proj_man_id])#, lazy='dynamic')
    forums_anchored = db.Column(db.Boolean)
    forums = db.Column(db.String(64))
    budget_secured = db.Column(db.Boolean)
    approved_by_sg = db.Column(db.Boolean)
    approach_approved = db.Column(db.Boolean)
    forums_pdi_approved = db.Column(db.Boolean)
    it_bluprint_done = db.Column(db.Boolean)
    sg_appointed = db.Column(db.Boolean)
    funds_secured = db.Column(db.Boolean)
    biz_study_done = db.Column(db.Boolean)
    solution_study_done = db.Column(db.Boolean)
    report_approved = db.Column(db.Boolean)
    cost_estimate = db.Column(db.String(24))
    time_estimate = db.Column(db.String(24))
    projs_mapped = db.Column(db.Boolean)
    pro_mapped = db.Column(db.Boolean)
    org_mapped = db.Column(db.Boolean)
    org_dependence = db.Column(db.String(64))
    tec_mapped = db.Column(db.Boolean)
    tec_dependence = db.Column(db.Boolean)
    pro_impact = db.Column(db.Enum('NONE','L','M','H','?'))
    pro_impact_when = db.Column(db.String(24))
    org_impact = db.Column(db.Enum('NONE','L','M','H','?'))
    org_impact_users = db.Column(db.String(64))
    org_impact_when = db.Column(db.String(24))
    tec_impact = db.Column(db.Enum('NONE','L','M','H','?'))
    tec_impact_when = db.Column(db.String(24))
    inf_impact = db.Column(db.Enum('NONE','L','M','H','?'))
    inf_impact_when = db.Column(db.String(24))
    gut_feeling = db.Column(db.String(8))
    important_milestone = db.Column(db.String(24))
    dp1_planned = db.Column(db.String(32))
    dp1_actual = db.Column(db.String(32))
    dp1_critical = db.Column(db.String(32))
    dp3_planned = db.Column(db.String(32))
    dp3_actual = db.Column(db.String(32))
    dp3_critical = db.Column(db.String(32))
    dp6_planned = db.Column(db.String(32))
    dp6_actual = db.Column(db.String(32))
    dp6_critical = db.Column(db.String(32))
    dp8_planned = db.Column(db.String(32))
    dp8_actual = db.Column(db.String(32))
    dp8_critical = db.Column(db.String(32))
    #comments = db.Column(db.Text)
    #status = db.Column(db.String(64))
    #responsible
    #deadline = db.Column(db.String(64))
    byprog_col = db.Column(db.Float)
    byprog_row = db.Column(db.Float)
    byprog_txt = db.Column(db.String(64))



def main():
    pass

if __name__ == '__main__':
    main()
