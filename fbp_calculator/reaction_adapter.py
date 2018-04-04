# -*- coding: utf-8 -*-

def reaction_adapter(text):
    return text.replace(',', '__')

def reaction_invadapter(text):
    return text.replace('__', ',')
