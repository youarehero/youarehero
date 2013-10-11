# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Coupon'
        db.create_table(u'herocoupon_coupon', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='single', max_length=255)),
            ('xp', self.gf('django.db.models.fields.PositiveSmallIntegerField')(default=0)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal(u'herocoupon', ['Coupon'])


    def backwards(self, orm):
        # Deleting model 'Coupon'
        db.delete_table(u'herocoupon_coupon')


    models = {
        u'herocoupon.coupon': {
            'Meta': {'object_name': 'Coupon'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'single'", 'max_length': '255'}),
            'xp': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'})
        }
    }

    complete_apps = ['herocoupon']