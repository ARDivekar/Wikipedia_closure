# -*- coding: utf-8 -*-
#test.py
import hyperlink_fetch
import re
import text_manip
from bs4 import BeautifulSoup
hyperlink_fetch.wiki_get_all(root_link="https://en.wikipedia.org/wiki/Greater_London_Authority_Act_1999", max_depth=1, input_root_folderpath="F:\Workspaces\Python\Wikipedia_closure\example", force_redo=True)
