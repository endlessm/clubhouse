#!/usr/bin/env python3
#
# Copyright © 2020 Endless OS Foundation LLC.
#
# This file is part of clubhouse
# (see https://github.com/endlessm/clubhouse).
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import re


class SimpleMarkupParser:
    """A simple markup parser for Hack

    # We setup custom tags to simplify the checks:
    >>> custom_tags = {
    ...     'inlinecode_start': '<tt><span size="small">',
    ...     'inlinecode_end': '</span></tt>',
    ...     'url_start': '<u><span fg_color="blue">',
    ...     'url_end': '</span></u>',
    ... }

    >>> parser = SimpleMarkupParser(custom_tags)

    >>> parser._do_parse('We have *bold*, _italics_ and `code`.')
    'We have <b>bold</b>, <i>italics</i> and <tt><span size="small">code</span></tt>.'

    >>> parser._do_parse('*I am _very_ excited* about this quest!')
    '<b>I am <i>very</i> excited</b> about this quest!'

    >>> parser._do_parse('I ~despise~ am not a fan of soup.')
    'I <s>despise</s> am not a fan of soup.'

    >>> parser._do_parse('Try setting `gravity = 0` in the code.')
    'Try setting <tt><span size="small">gravity = 0</span></tt> in the code.'

    >>> parser._do_parse('Checkout this site! https://www.w3.org/2000/svg')
    'Checkout this site! <u><span fg_color="blue">https://www.w3.org/2000/svg</span></u>'

    >>> parser._do_parse('Link with an underscore should not break: https://test.org/hello_world')
    'Link with an underscore should not break: \
<u><span fg_color="blue">https://test.org/hello_world</span></u>'

    >>> parser._do_parse('Mixing `code and *bold*` allowed')
    'Mixing <tt><span size="small">code and <b>bold</b></span></tt> allowed'

    >>> parser._do_parse('URL in code `https://www.hack-computer.com/` allowed')
    'URL in code <tt><span size="small"><u><span fg_color="blue">\
https://www.hack-computer.com/</span></u></span></tt> allowed'
    """
    DEFAULT_TAGS = {
        'bold_start': '<b>',
        'bold_end': '</b>',
        'italics_start': '<i>',
        'italics_end': '</i>',
        'strikethrough_start': '<s>',
        'strikethrough_end': '</s>',
        'inlinecode_start': ('<tt><span insert_hyphens="false" '
                             'foreground="#287A8C" background="#FFFFFF">'),
        'inlinecode_end': '</span></tt>',
        'url_start': '<u><span insert_hyphens="false" foreground="#3584E4">',
        'url_end': '</span></u>',
    }
    _convertions = None
    _instance = None

    def __init__(self, custom_tags=None):
        tags = self.DEFAULT_TAGS.copy()
        if isinstance(custom_tags, dict):
            tags.update(custom_tags)

        self._convertions = [
            [re.compile(r'<', re.S), r'&lt;'],
            [re.compile(r'>', re.S), r'&gt;'],
            [re.compile(
                # From http://www.noah.org/wiki/RegEx_Python#URL_regex_pattern
                (r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
                 r'(?:%[0-9a-fA-F][0-9a-fA-F]))+)'), re.S),
             f'{tags["url_start"]}\\1{tags["url_end"]}'],
            [re.compile(r'(?!<span[^>]*?>)(\*)(?=\S)(.+?)(?<=\S)\1(?![^<]*?</span>)', re.S),
             f'{tags["bold_start"]}\\2{tags["bold_end"]}'],
            [re.compile(r'(?!<span[^>]*?>)(_)(?=\S)(.+?)(?<=\S)\1(?![^<]*?</span>)', re.S),
             f'{tags["italics_start"]}\\2{tags["italics_end"]}'],
            [re.compile(r'(?!<span[^>]*?>)(~)(?=\S)(.+?)(?<=\S)\1(?![^<]*?</span>)', re.S),
             f'{tags["strikethrough_start"]}\\2{tags["strikethrough_end"]}'],
            [re.compile(r'(`)(?=\S)(.+?)(?<=\S)\1', re.S),
             f'{tags["inlinecode_start"]}\\2{tags["inlinecode_end"]}'],
        ]

    def _do_parse(self, text):
        for regex, replacement in self._convertions:
            text = regex.sub(replacement, text)
        return text

    @classmethod
    def parse(class_, text):
        if class_._instance is None:
            class_._instance = class_()
        return class_._instance._do_parse(text)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
