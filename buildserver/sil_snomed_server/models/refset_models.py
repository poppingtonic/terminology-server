from sil_snomed_server.app import db

from sil_snomed_server.data_types.custom_types import UUID
import uuid

class Refset(db.Model):
    __abstract__ = True

    id = db.Column(UUID(binary=False), primary_key=True)
    effective_time = db.Column(db.Date, primary_key=True)
    active = db.Column(db.Boolean, primary_key=True)
    module_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    refset_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    referenced_component_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)


class AssociationReferenceSet(Refset):
    __tablename__ = 'curr_associationrefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    target_component_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)


class LanguageReferenceSet(Refset):
    __tablename__ = 'curr_langrefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    acceptability_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)


class ComplexMapReferenceSet(Refset):
    __tablename__ = 'curr_complexmaprefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    map_group = db.Column(db.Integer, primary_key=True, autoincrement=False)
    map_priority = db.Column(db.Integer, primary_key=True, autoincrement=False)
    map_rule = db.Column(db.Unicode)
    map_target = db.Column(db.Unicode)
    correlation_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    map_advice = db.Column(db.Unicode)
    map_block = db.Column(db.Integer, autoincrement=False)


class AttributeValueReferenceSet(Refset):
    __tablename__ = 'curr_attributevaluerefset_f'


    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    value_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)


class SimpleMapReferenceSet(Refset):
    __tablename__ = 'curr_simplemaprefset_f'


    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    map_target = db.Column(db.Unicode)


class SimpleReferenceSet(Refset):
    __tablename__ = 'curr_simplerefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)


class OrderedReferenceSet(Refset):
    __tablename__ = 'curr_orderedrefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    order = db.Column(db.Integer, primary_key=True, autoincrement=False)
    linked_to_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)


class QuerySpecificationReferenceSet(Refset):
    __tablename__ = 'curr_queryspecificationrefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    query = db.Column(db.Unicode)


class ModuleDependencyReferenceSet(Refset):
    __tablename__ = 'curr_moduledependencyrefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    source_effective_time = db.Column(db.Date, primary_key=True)
    target_effective_time = db.Column(db.Date, primary_key=True)


class ReferenceSetDescriptorReferenceSet(Refset):
    __tablename__ = 'curr_referencesetdescriptorrefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    attribute_description_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    attribute_type_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    attribute_order = db.Column(db.Integer, primary_key=True, autoincrement=False)


class ExtendedMapReferenceSet(Refset):
    __tablename__ = 'curr_extendedmaprefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    map_group = db.Column(db.Integer, primary_key=True, autoincrement=False)
    map_priority = db.Column(db.Integer, primary_key=True, autoincrement=False)
    map_rule = db.Column(db.Unicode)
    map_target = db.Column(db.Unicode)
    correlation_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    map_category_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    map_advice = db.Column(db.Unicode)


class AnnotationReferenceSet(Refset):
    __tablename__ = 'curr_annotationrefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    annotation = db.Column(db.Text)


class DescriptionFormatReferenceSet(Refset):
    __tablename__ = 'curr_descriptionformatrefset_f'

    __table_args__ = (
        db.Index('sct_%s_index_effective_time' % __tablename__,
                 'effective_time',
                 postgresql_using='brin'
        ),)

    description_format_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    description_length = db.Column(db.Integer, primary_key=True, autoincrement=False)
