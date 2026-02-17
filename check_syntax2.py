#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast

with open('D:/easywork/app.py', 'r', encoding='utf-8-sig') as f:
    content = f.read()

try:
    ast.parse(content)
    print('No syntax errors!')
except SyntaxError as e:
    print(f'Syntax error at line {e.lineno}: {e.msg}')
