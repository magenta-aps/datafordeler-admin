
from __future__ import absolute_import, unicode_literals, print_function

import contextlib
import datetime
import functools
import io
import os
import unittest
import uuid
import platform

# import freezegun
# import openpyxl
import pycodestyle
# import pytz
from pyvirtualdisplay import Display

from django import apps, db, test
from django.conf import settings
from django.core import exceptions
from django.utils import translation
from django.test import tag
from selenium import webdriver

try:
    import selenium.webdriver
except ImportError:
    selenium = None


DUMMY_DOMAIN = 'http://localhost'


class CodeStyleTests(test.SimpleTestCase):

    @property
    def rootdir(self):
        return os.path.dirname(os.path.dirname(__file__))

    @property
    def source_files(self):
        """Generator that yields Python sources to test"""

        for dirpath, dirs, fns in os.walk(self.rootdir):
            dirs[:] = [
                dn for dn in dirs
                if dn != 'migrations' and not dn.startswith('venv-')
            ]

            for fn in fns:
                if fn[0] != '.' and fn.endswith('.py'):
                    yield os.path.join(dirpath, fn)
    #
    # @tag('pep8')
    # def test_pep8(self):
    #     pep8style = pycodestyle.StyleGuide()
    #     pep8style.init_report(pycodestyle.StandardReport)
    #
    #     buf = io.StringIO()
    #
    #     with
    #         for fn in self.source_files:
    #             pep8style.check_files([fn])
    #
    #     assert not buf.getvalue(), \
    #         "Found code style errors and/or warnings:\n\n" + buf.getvalue()

    def test_source_files(self):
        sources = list(self.source_files)
        self.assert_(sources)
        self.assertGreater(len(sources), 1, sources)

    @staticmethod
    @contextlib.contextmanager
    def capture():
        import sys
        from cStringIO import StringIO
        oldout,olderr = sys.stdout, sys.stderr
        try:
            out=[StringIO(), StringIO()]
            sys.stdout,sys.stderr = out
            yield out
        finally:
            sys.stdout,sys.stderr = oldout, olderr
            out[0] = out[0].getvalue()
            out[1] = out[1].getvalue()




SAFARI_PREVIEW_DRIVER = ('/Applications/Safari Technology Preview.app'
                         '/Contents/MacOS/safaridriver')
CHROME_UBUNTU_DRIVER = '/usr/local/bin/chromedriver'

class BrowserTest(test.LiveServerTestCase):

    @classmethod
    def setUpClass(cls):

        default_driver = (
            'Safari'
            if platform.system() == 'Darwin'
            else 'Chrome'
        )
        driver_name = os.environ.get('BROWSER', default_driver)

        driver = getattr(selenium.webdriver, driver_name, None)

        if not driver:
            raise unittest.SkipTest('$BROWSER unset or invalid')

        args = {}

        if driver_name == 'Safari' and os.path.isfile(SAFARI_PREVIEW_DRIVER):
            args.update(executable_path=SAFARI_PREVIEW_DRIVER)

        if driver_name == 'Chrome' and platform.dist()[0] == 'Ubuntu':
            args.update(executable_path=CHROME_UBUNTU_DRIVER)

        try:
            cls.browser = driver(**args)
        except Exception as exc:
            print(exc)
            raise unittest.SkipTest(exc.args[0])

        super(BrowserTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(BrowserTest, cls).tearDownClass()

        cls.browser.quit()


    def await_staleness(self, element):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        WebDriverWait(self.browser, 1).until(
            EC.staleness_of(element),
        )
        self.browser.find_element_by_id("content")

    def fill_in_form(self, **kwargs):
        for field, value in kwargs.items():
            e = self.browser.find_element_by_id("id_" + field)

            if (e.tag_name == 'input' and
                        e.get_attribute('type') in ('text', 'password', 'number')):
                e.clear()
                e.send_keys(
                    value,
                )
            elif e.tag_name == 'select':
                options = e.find_elements_by_tag_name('option')

                for option in options:
                    if option.text.strip() == value:
                        option.click()
                        break
                else:
                    self.fail('{} not one of {}'.format(
                        value, [o.text for o in options]),
                    )
            elif (e.tag_name == 'input' and
                          e.get_attribute('type') in ('checkbox', 'radio')):
                if value != e.is_selected():
                    e.click()
            else:
                self.fail('unhandled input element (' + e.tag_name + '): ' +
                          e.get_attribute('outerHTML'))

        submit = self.browser.find_element_by_css_selector(
            "input[type=submit]",
        )
        submit.click()
        # self.await_staleness(submit)


    def login(self, user, password='password', expected=True):
        # logout
        self.browser.delete_all_cookies()
        self.browser.get(self.live_server_url + '/admin/logout/')
        self.browser.delete_all_cookies()
        self.browser.get(self.live_server_url + '/login')

        self.assertNotEqual(self.live_server_url, self.browser.current_url,
                            'logout failed!')

        # sanitity check the credentials
        self.client.logout()
        login_status = self.client.login(username=user, password=password)

        self.assertEqual(login_status, expected,
                         'Unexpected login status (credentials)!')

        self.fill_in_form(username=user, password=password)
        if expected:
            self.assertEquals(self.live_server_url + '/frontpage/',
                              self.browser.current_url,
                              'login failed')
        else:
            self.assertNotEquals(self.live_server_url + '/login/',
                                 self.browser.current_url,
                                 'login successful')

    def element_text(self, elem_id):
        return self.browser.find_element_by_id(elem_id).text.strip().lower()


@tag('selenium')
@unittest.skipIf(not selenium, 'selenium not installed')
class LoginTest(BrowserTest):

    def test_login(self):
        self.login("jakob@data.nanoq.gl", "jacob")
