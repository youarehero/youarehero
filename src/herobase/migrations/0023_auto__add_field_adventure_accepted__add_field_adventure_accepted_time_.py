# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Adventure.accepted'
        db.add_column('herobase_adventure', 'accepted',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Adventure.accepted_time'
        db.add_column('herobase_adventure', 'accepted_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Adventure.rejected'
        db.add_column('herobase_adventure', 'rejected',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Adventure.rejected_time'
        db.add_column('herobase_adventure', 'rejected_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Adventure.canceled'
        db.add_column('herobase_adventure', 'canceled',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Adventure.canceled_time'
        db.add_column('herobase_adventure', 'canceled_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Adventure.done'
        db.add_column('herobase_adventure', 'done',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Adventure.done_time'
        db.add_column('herobase_adventure', 'done_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Quest.open'
        db.add_column('herobase_quest', 'open',
                      self.gf('django.db.models.fields.BooleanField')(default=True),
                      keep_default=False)

        # Adding field 'Quest.canceled'
        db.add_column('herobase_quest', 'canceled',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Quest.canceled_time'
        db.add_column('herobase_quest', 'canceled_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Quest.done'
        db.add_column('herobase_quest', 'done',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Quest.done_time'
        db.add_column('herobase_quest', 'done_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Quest.started'
        db.add_column('herobase_quest', 'started',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Quest.started_time'
        db.add_column('herobase_quest', 'started_time',
                      self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True),
                      keep_default=False)


        # Changing field 'Quest.level'
        db.alter_column('herobase_quest', 'level', self.gf('django.db.models.fields.IntegerField')())

    def backwards(self, orm):
        # Deleting field 'Adventure.accepted'
        db.delete_column('herobase_adventure', 'accepted')

        # Deleting field 'Adventure.accepted_time'
        db.delete_column('herobase_adventure', 'accepted_time')

        # Deleting field 'Adventure.rejected'
        db.delete_column('herobase_adventure', 'rejected')

        # Deleting field 'Adventure.rejected_time'
        db.delete_column('herobase_adventure', 'rejected_time')

        # Deleting field 'Adventure.canceled'
        db.delete_column('herobase_adventure', 'canceled')

        # Deleting field 'Adventure.canceled_time'
        db.delete_column('herobase_adventure', 'canceled_time')

        # Deleting field 'Adventure.done'
        db.delete_column('herobase_adventure', 'done')

        # Deleting field 'Adventure.done_time'
        db.delete_column('herobase_adventure', 'done_time')

        # Deleting field 'Quest.open'
        db.delete_column('herobase_quest', 'open')

        # Deleting field 'Quest.canceled'
        db.delete_column('herobase_quest', 'canceled')

        # Deleting field 'Quest.canceled_time'
        db.delete_column('herobase_quest', 'canceled_time')

        # Deleting field 'Quest.done'
        db.delete_column('herobase_quest', 'done')

        # Deleting field 'Quest.done_time'
        db.delete_column('herobase_quest', 'done_time')

        # Deleting field 'Quest.started'
        db.delete_column('herobase_quest', 'started')

        # Deleting field 'Quest.started_time'
        db.delete_column('herobase_quest', 'started_time')


        # Changing field 'Quest.level'
        db.alter_column('herobase_quest', 'level', self.gf('django.db.models.fields.PositiveIntegerField')())

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'herobase.abusereport': {
            'Meta': {'object_name': 'AbuseReport'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'reporter': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'reported report'", 'to': "orm['auth.User']"}),
            'text': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'herobase.adventure': {
            'Meta': {'object_name': 'Adventure'},
            'accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'accepted_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'canceled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'canceled_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'done_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['herobase.Quest']"}),
            'rejected': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'rejected_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '10000'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'adventures'", 'to': "orm['auth.User']"})
        },
        'herobase.like': {
            'Meta': {'object_name': 'Like'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['herobase.Quest']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'herobase.quest': {
            'Meta': {'object_name': 'Quest'},
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'auto_accept': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'canceled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'canceled_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'done_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {}),
            'experience': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'hero_class': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'heroes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'quests'", 'symmetrical': 'False', 'through': "orm['herobase.Adventure']", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'location_granularity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'max_heroes': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'db_index': 'True', 'blank': 'True'}),
            'open': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'created_quests'", 'to': "orm['auth.User']"}),
            'remote': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'started': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'started_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'state': ('django.db.models.fields.IntegerField', [], {'default': '1000'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'herobase.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'about': ('django.db.models.fields.TextField', [], {'default': "''", 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'experience': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'hero_class': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keep_email_after_gpn': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'location_granularity': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'longitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'public_location': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'receive_private_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'receive_system_email': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['herobase']