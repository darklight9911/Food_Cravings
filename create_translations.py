#!/usr/bin/env python3

import os
from babel.messages import Catalog
from babel.messages.pofile import write_po
from babel.messages.extract import extract_from_dir

# Extract messages
catalog = Catalog()

# Add some basic strings that we'll need
catalog.add('Dashboard', string='Dashboard')
catalog.add('Menu', string='Menu')
catalog.add('Orders', string='Orders')
catalog.add('Login', string='Login')
catalog.add('Logout', string='Logout')
catalog.add('Register', string='Register')
catalog.add('Profile', string='Profile')
catalog.add('Account', string='Account')
catalog.add('Menu Management', string='Menu Management')
catalog.add('Admin Dashboard', string='Admin Dashboard')
catalog.add('Food Cravings', string='Food Cravings')
catalog.add('Language', string='Language')
catalog.add('English', string='English')
catalog.add('বাংলা', string='বাংলা')

# Create directories
os.makedirs('translations/en/LC_MESSAGES', exist_ok=True)
os.makedirs('translations/bn/LC_MESSAGES', exist_ok=True)

# Write English catalog (source language)
en_catalog = Catalog(locale='en')
for msg in catalog:
    en_catalog.add(msg.id, string=msg.string)
with open('translations/en/LC_MESSAGES/messages.po', 'wb') as f:
    write_po(f, en_catalog, locale='en')

# Write Bengali catalog (target language)
bn_catalog = Catalog(locale='bn')
bn_catalog.add('Dashboard', string='ড্যাশবোর্ড')
bn_catalog.add('Menu', string='মেনু')
bn_catalog.add('Orders', string='অর্ডার')
bn_catalog.add('Login', string='লগইন')
bn_catalog.add('Logout', string='লগআউট')
bn_catalog.add('Register', string='নিবন্ধন')
bn_catalog.add('Profile', string='প্রোফাইল')
bn_catalog.add('Account', string='অ্যাকাউন্ট')
bn_catalog.add('Menu Management', string='মেনু ব্যবস্থাপনা')
bn_catalog.add('Admin Dashboard', string='অ্যাডমিন ড্যাশবোর্ড')
bn_catalog.add('Food Cravings', string='খাবারের আকাঙ্ক্ষা')
bn_catalog.add('Language', string='ভাষা')
bn_catalog.add('English', string='ইংরেজি')
bn_catalog.add('বাংলা', string='বাংলা')

with open('translations/bn/LC_MESSAGES/messages.po', 'wb') as f:
    write_po(f, bn_catalog, locale='bn')

print("Translation files created successfully!")