# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        for user in orm['auth.User']:
            orm['herorecommend.UserCombinedProfile'].objects.get_or_create(user=user)
            orm['herorecommend.UserSelectionProfile'].objects.get_or_create(user=user)
            orm['herorecommend.UserRatingProfile'].objects.get_or_create(user=user)

        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."

    def backwards(self, orm):
        "Write your backwards methods here."

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
        'herorecommend.questprofile': {
            'Meta': {'object_name': 'QuestProfile'},
            'arabic': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'audio': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'average': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'biology': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'chemistry': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'chores': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'community': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'computers': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'cooking_baking': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'crafts': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_arabic': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_audio': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_biology': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_chemistry': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_chores': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_community': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_computers': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_cooking_baking': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_crafts': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_design': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_driving': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_economics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_electrics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_english': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_french': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_gardening': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_german': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_graphics_design': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_handicrafts': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_handle_animals': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_history': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_mathematics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_needlework': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_outdoor_action': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_photography': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_programming': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_shopping': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_spanish': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_sports': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_teaching': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_transportation': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_video': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'delta_writing': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'design': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'driving': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'economics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'electrics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'english': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'french': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'gardening': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'german': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'graphics_design': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'handicrafts': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'handle_animals': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'history': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mathematics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'needlework': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'outdoor_action': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'photography': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'programming': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'quest': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'profile'", 'unique': 'True', 'to': "orm['herobase.Quest']"}),
            'root_sum_of_squares': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'shopping': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'spanish': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sports': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'teaching': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'transportation': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'video': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'writing': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'herorecommend.questrating': {
            'Meta': {'object_name': 'QuestRating'},
            'apply': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'like': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'participate': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'participate_plus': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'quest': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['herobase.Quest']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'ratings'", 'to': "orm['auth.User']"})
        },
        'herorecommend.usercombinedprofile': {
            'Meta': {'object_name': 'UserCombinedProfile'},
            'arabic': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'audio': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'biology': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'chemistry': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'chores': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'community': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'computers': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'cooking_baking': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'crafts': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'design': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'driving': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'economics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'electrics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'english': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'french': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'gardening': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'german': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'graphics_design': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'handicrafts': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'handle_animals': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'history': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mathematics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'needlework': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'outdoor_action': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'photography': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'programming': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'shopping': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'spanish': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sports': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'teaching': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'transportation': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'combined_profile'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'writing': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'herorecommend.userratingprofile': {
            'Meta': {'object_name': 'UserRatingProfile'},
            'arabic': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'audio': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'biology': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'chemistry': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'chores': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'community': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'computers': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'cooking_baking': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'crafts': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'design': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'driving': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'economics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'electrics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'english': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'french': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'gardening': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'german': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'graphics_design': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'handicrafts': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'handle_animals': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'history': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mathematics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'needlework': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'outdoor_action': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'photography': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'programming': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'shopping': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'spanish': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sports': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'teaching': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'transportation': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'rating_profile'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'writing': ('django.db.models.fields.FloatField', [], {'default': '0'})
        },
        'herorecommend.userselectionprofile': {
            'Meta': {'object_name': 'UserSelectionProfile'},
            'arabic': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'audio': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'biology': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'chemistry': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'chores': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'community': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'computers': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'cooking_baking': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'crafts': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'design': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'driving': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'economics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'electrics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'english': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'french': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'gardening': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'german': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'graphics_design': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'handicrafts': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'handle_animals': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'history': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mathematics': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'needlework': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'outdoor_action': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'photography': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'programming': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'shopping': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'spanish': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'sports': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'teaching': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'transportation': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'selected_skills'", 'unique': 'True', 'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'writing': ('django.db.models.fields.FloatField', [], {'default': '0'})
        }
    }

    complete_apps = ['herorecommend']
    symmetrical = True
