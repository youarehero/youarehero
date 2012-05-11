# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Adventure'
        db.create_table('herobase_adventure', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='adventures', to=orm['auth.User'])),
            ('quest', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['herobase.Quest'])),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('herobase', ['Adventure'])

        # Adding model 'Quest'
        db.create_table('herobase_quest', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('author', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('hero_class', self.gf('django.db.models.fields.IntegerField')()),
            ('level', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('max_heroes', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('due_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('state', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('herobase', ['Quest'])

        # Adding model 'UserProfile'
        db.create_table('herobase_userprofile', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['auth.User'], unique=True)),
            ('experience', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('location', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('hero_class', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('herobase', ['UserProfile'])


    def backwards(self, orm):
        # Deleting model 'Adventure'
        db.delete_table('herobase_adventure')

        # Deleting model 'Quest'
        db.delete_table('herobase_quest')

        # Deleting model 'UserProfile'
        db.delete_table('herobase_userprofile')


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
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
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
        'herobase.adventure': {
            'Meta': {'object_name': 'Adventure'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['herobase.Quest']"}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'adventures'", 'to': "orm['auth.User']"})
        },
        'herobase.quest': {
            'Meta': {'object_name': 'Quest'},
            'author': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {}),
            'hero_class': ('django.db.models.fields.IntegerField', [], {}),
            'heroes': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'quests'", 'symmetrical': 'False', 'through': "orm['herobase.Adventure']", 'to': "orm['auth.User']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'max_heroes': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'state': ('django.db.models.fields.IntegerField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'herobase.userprofile': {
            'Meta': {'object_name': 'UserProfile'},
            'experience': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'hero_class': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'})
        }
    }

    complete_apps = ['herobase']