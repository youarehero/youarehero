# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):
    def translate_state_flags(self, queryset, state_flag_map):
        for state, flags in state_flag_map.items():
            times = {}
            for field, flag in flags.items():
                if field != 'open':
                    times['%s_time' % field] = models.F('modified') if flag else None
            times.update(flags)
            queryset.filter(state=state).update(**times)

    def forwards(self, orm):
        Quest = orm['herobase.Quest']
        Adventure = orm['herobase.Adventure']

        Adventure.STATE_NOT_SET = 0
        Adventure.STATE_HERO_APPLIED = 1
        Adventure.STATE_OWNER_REFUSED = 2
        Adventure.STATE_HERO_CANCELED = 3
        Adventure.STATE_OWNER_ACCEPTED = 4
        Adventure.STATE_HERO_DONE = 5
        Adventure.STATE_OWNER_DONE = 6
        Adventure.STATE_NO_STATE = 10000

        Quest.STATE_NOT_SET = 0
        Quest.STATE_OPEN = 1
        Quest.STATE_FULL = 2
        Quest.STATE_OWNER_DONE = 3
        Quest.STATE_OWNER_CANCELED = 4
        Quest.STATE_NO_STATE = 1000

        adventure_states = {
            Adventure.STATE_HERO_APPLIED: {
                'accepted': False,
                'rejected': False,
                'canceled': False,
                'done': False,
                },
            Adventure.STATE_OWNER_REFUSED: {
                'accepted': False,
                'rejected': True,
                'canceled': False,
                'done': False,
                },
            Adventure.STATE_HERO_CANCELED: {
                'accepted': False,
                'rejected': False,
                'canceled': True,
                'done': False,
                },
            Adventure.STATE_OWNER_ACCEPTED: {
                'accepted': True,
                'rejected': False,
                'canceled': False,
                'done': False,
                },
            Adventure.STATE_HERO_DONE: {
                'accepted': True,
                'rejected': False,
                'canceled': False,
                'done': False,
                },
            Adventure.STATE_OWNER_DONE: {
                'accepted': True,
                'rejected': False,
                'canceled': False,
                'done': True,
                },
            Adventure.STATE_NO_STATE: {
                'accepted': False,
                'rejected': False,
                'canceled': False,
                'done': False,
                },
            Adventure.STATE_NOT_SET: {
                'accepted': False,
                'rejected': False,
                'canceled': False,
                'done': False,
                },
        }

        quest_states = {
            Quest.STATE_NO_STATE: {
                'canceled': False,
                'done': False,
                'started': False,
                'open': False
            },
            Quest.STATE_NOT_SET: {
                'canceled': False,
                'done': False,
                'started': False,
                'open': False
            },
            Quest.STATE_OPEN: {
                'canceled': False,
                'done': False,
                'started': False,
                'open': True
            },
            Quest.STATE_OWNER_DONE: {
                'canceled': False,
                'done': True,
                'started': True,
                'open': False
            },
            Quest.STATE_OWNER_CANCELED: {
                'canceled': True,
                'done': False,
                'started': False,
                'open': False
            },
        }
        self.translate_state_flags(Adventure.objects.all(), adventure_states)
        self.translate_state_flags(Quest.objects.all(), quest_states)

    def backwards(self, orm):
        pass


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
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'adventures'", 'to': "orm['herobase.Quest']"}),
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
            'canceled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'canceled_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'db_index': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'done': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'done_time': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'expiration_date': ('django.db.models.fields.DateTimeField', [], {}),
            'heroes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'quests'", 'symmetrical': 'False', 'through': "orm['herobase.Adventure']", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.FloatField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
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
            'time_effort': ('django.db.models.fields.IntegerField', [], {'null': 'True'}),
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
    symmetrical = True
