import datetime
import unittest

from eosclubhouse.utils import convert_variant_arg, SimpleMarkupParser


class TestVariantConversion(unittest.TestCase):

    def test_can_convert_variant(self):
        """Tests that we can convert Python dicts to GLib.Variant."""

        variant = convert_variant_arg({'hints_given': True})
        self.assertTrue(variant.unpack() == {'hints_given': True})

        with self.assertRaises(TypeError):
            convert_variant_arg({'no_serializable': datetime.datetime.now()})


class TestMarkup(unittest.TestCase):

    def test_can_foo(self):
        """Tests that we can FOO."""

        # We setup custom tags to simplify the checks:
        custom_tags = {
            'inlinecode_start': '<tt><span size="small">',
            'inlinecode_end': '</span></tt>',
            'url_start': '<u><span fg_color="blue">',
            'url_end': '</span></u>',
        }
        parser = SimpleMarkupParser(custom_tags)

        values_to_test = [
            ('We have *bold*, _italics_ and `code`.',
             'We have <b>bold</b>, <i>italics</i> and <tt><span size="small">code</span></tt>.'),
            ('*I am _very_ excited* about this quest!',
             '<b>I am <i>very</i> excited</b> about this quest!'),
            ('I ~despise~ am not a fan of soup.',
             'I <s>despise</s> am not a fan of soup.'),
            ('Try setting `gravity = 0` in the code.',
             'Try setting <tt><span size="small">gravity = 0</span></tt> in the code.'),
            ('Checkout this site! https://www.w3.org/2000/svg',
             'Checkout this site! <u><span fg_color="blue">https://www.w3.org/2000/svg</span></u>'),
            ('Link with an underscore should not break: https://test.org/hello_world',
             ('Link with an underscore should not break: '
              '<u><span fg_color="blue">https://test.org/hello_world</span></u>')),
            ('Mixing `code and *bold*` allowed',
             'Mixing <tt><span size="small">code and <b>bold</b></span></tt> allowed'),
            ('URL in code `https://www.hack-computer.com/` allowed',
             ('URL in code <tt><span size="small"><u><span fg_color="blue">'
              'https://www.hack-computer.com/</span></u></span></tt> allowed')),
        ]

        for in_, out in values_to_test:
            self.assertEqual(out, parser._do_parse(in_))
