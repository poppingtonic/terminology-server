from sil_snomed_server.app import db


class Component(db.Model):
    __abstract__  = True

    id = db.Column(db.BigInteger, primary_key=True, index=True, autoincrement=False)
    effective_time = db.Column(db.Date, primary_key=True)
    active = db.Column(db.Boolean, primary_key=True)
    module_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)


class Concept(Component):
    __tablename__ = 'curr_concept_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    definition_status_id = db.Column(db.BigInteger)


class Description(Component):
    __tablename__ = 'curr_description_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    concept_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    language_code = db.Column(db.Unicode)
    type_id = db.Column(db.BigInteger)
    term = db.Column(db.Text)
    case_significance_id = db.Column(db.BigInteger)


class Relationship(Component):
    __tablename__ = 'curr_relationship_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    source_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    destination_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    relationship_group = db.Column(db.Integer, primary_key=True, autoincrement=False)
    type_id = db.Column(db.BigInteger)
    characteristic_type_id = db.Column(db.BigInteger)
    modifier_id = db.Column(db.BigInteger)
