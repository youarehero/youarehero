#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Populate

Usage:
  populate.py create <model> [<n> | -n<n> | --number <n>]
  populate.py (-h | --help)
  populate.py --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  -n=<n> --number=<n>   Number of Objects [default: 10]

"""
import codecs
import os
import random
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "youarehero.settings.local")
from django.conf import settings

from docopt import docopt
from datetime import datetime, time, timedelta
from django.db import transaction
from django.db import models
from django_dynamic_fixture import G, P
from django_dynamic_fixture.fixture_algorithms.random_fixture import RandomDataFixture

import names
import words

class HumanReadableRandomDataFixture(RandomDataFixture):
    # Helper
    def random_word(self, capitalize=True):
        if capitalize:
            return random.choice(words.lorem_ipsum).capitalize()
        return random.choice(words.lorem_ipsum)

    def random_sentence(self):
        words = [self.random_word() for _ in range(random.randint(2, 10))]
        return '%s.' % ' '.join(words).capitalize()

    def random_paragraph(self):
        sentences = [self.random_sentence() for _ in range(random.randint(1, 10))]
        return ' '.join(sentences)

    def random_choice(self, choices):
        return random.choice([x for (x, _) in choices._choices])

    def random_choices(self, choices, n=3):
        return ','.join([self.random_choice(choices) for _ in range(random.randint(1, n))])

    def random_date(self):
        d = datetime.now().date()
        d = d - timedelta(random.randint(-1, 400))
        return d

    def random_datetime(self):
        d = self.random_date()
        t = time(random.randint(8, 17), random.choice((0, 15, 30, 45)))
        return datetime.combine(d, t)

    # random data generation functions
    # method name must have the format: FIELDNAME_config
    def charfield_config(self, field, key):
        if field.get_attname() == 'description':
            return self.random_paragraph()
        elif field.get_attname() == 'zip_code':
            return random.randint(10000, 99999)
        elif field.get_attname() == 'street':
            return '%s %s' % (self.random_word(),  random.randint(1, 400))
        elif field.get_attname() == 'first_name':
            return random.choice(names.first_names)
        elif field.get_attname() == 'last_name':
            return random.choice(names.last_names)
        return self.random_word()

    def integerfield_config(self, field, key):
        return random.randint(0, 100000)

    def imagefield_config(self, field, key):
        # use specified assets folder for random images
        return None

    def datetimefield_config(self, field, key):
        if field.get_attname() == 'archived':
            return None
        return super(HumanReadableRandomDataFixture, self).datetimefield_config(field, key)


@transaction.commit_manually
def create_objects(model_class, n):
    print("creating %d %s-objects " % (n, model_class.__name__))
    for i in xrange(n):
        print '\r%s / %s' % (i+1, n),
        obj = G(model_class, data_fixture=HumanReadableRandomDataFixture())
    print ''
    transaction.commit()

if __name__ == '__main__':
    arguments = docopt(__doc__, version='Populate 0.1')
    model = arguments['<model>']
    n = int(arguments['<n>']) if arguments['<n>'] else int(arguments['--number'])

    model_dict = {}
    for m in models.get_models():
        if model.find('.') > 0:
            model_dict['%s.%s' % (m.__module__, m.__name__)] = m
        else:
            model_dict[m.__name__] = m

    if model in model_dict.keys():
        if arguments['create']:
            create_objects(model_dict[model], n)
    else:
        raise Exception('No model named "%s".' % model)
    sys.exit()
