# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-03 02:23

# Issues with performance forced us to take drastic measures denormalize translation models.
# We create btree_gin index and enabled pg_trgm extension in order to gain better performance of
# search filters.

from __future__ import unicode_literals

import django.contrib.postgres.search
from django.contrib.postgres.operations import TrigramExtension, CreateExtension
from django.db import migrations

from pontoon.db.migrations import (
    MultiFieldTRGMIndex,
)

entity_document_update_sql = """
    UPDATE base_translation AS t 
      SET entity_document = (e.key || ' ' || e.string || ' ' || e.string_plural || ' ' || e.comment)
      FROM base_entity AS e
      WHERE t.entity_id=e.id;
"""

entity_document_update_trigger_create_sql = """
    CREATE FUNCTION base_translation_entity_document_update() RETURNS TRIGGER AS $$
        BEGIN
          NEW.entity_document = (
            SELECT (e.key || ' ' || e.string || ' ' || e.string_plural || ' ' || e.comment) as document
            FROM base_entity as e
            WHERE id=NEW.entity_id
          );
        RETURN NEW;
    END;
    $$ LANGUAGE 'plpgsql';
    CREATE TRIGGER base_translation_entity_document_update BEFORE INSERT OR UPDATE ON "base_translation"
    FOR EACH ROW EXECUTE PROCEDURE base_translation_entity_document_update()
"""
entity_document_update_trigger_drop_sql = '''
    DROP TRIGGER base_translation_entity_document_update ON "base_translation";
    DROP FUNCTION base_translation_entity_document_update();
'''

class Migration(migrations.Migration):

    dependencies = [
        ('base', '0090_entity_date_created'),
    ]

    operations = [
        CreateExtension('btree_gin'),
        TrigramExtension(),
        migrations.AddField(
            model_name='translation',
            name='entity_document',
            field=django.db.models.fields.TextField(blank=True)
        ),

        migrations.RunSQL(
            entity_document_update_sql,
            migrations.RunSQL.noop,
        ),

        migrations.RunSQL(
            entity_document_update_trigger_create_sql,
            entity_document_update_trigger_drop_sql,
        ),

        MultiFieldTRGMIndex(
            table='base_translation',
            from_fields=['entity_document', 'string'],
            field='entity_document'
        ),
    ]
