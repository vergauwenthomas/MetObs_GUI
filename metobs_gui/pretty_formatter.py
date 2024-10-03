#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  3 10:30:25 2024

@author: thoverga
"""



def set_prompt_subsection(text, prompt):
    prompt_html=f'<p style="font-family:courier;color:blue;">{text} \n\n</p>'
    prompt.appendHtml(prompt_html)
    prompt.centerCursor()