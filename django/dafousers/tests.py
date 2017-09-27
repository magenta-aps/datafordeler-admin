# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

import contextlib
import time
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
from django.db.models.fields.files import FieldFile
from pyvirtualdisplay import Display

from django import apps, db, test
from django.conf import settings
from django.core import exceptions
from django.utils import translation
from django.test import tag
from selenium import webdriver
from abc import ABCMeta, abstractmethod

from .models import IdentityProviderAccount

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

USERNAME = "jakob@data.nanoq.gl"
PASSWORD = "jacob"

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

    def fill_in_form(self, submit_id=None, **kwargs):
        for field, value in kwargs.items():
            e = self.browser.find_element_by_id("id_" + field)

            if ((
                e.tag_name == 'input' and
                e.get_attribute('type') in ('text', 'password', 'number', 'email', 'file')
            ) or (
                e.tag_name == 'textarea'
            )):
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

        if submit_id is not None:
            submit = self.browser.find_element_by_id(submit_id)
        else:
            submit = self.browser.find_element_by_css_selector(
                "input[type=submit]",
            )
        submit.click()
        # self.await_staleness(submit)

    def logout(self):
        self.browser.delete_all_cookies()
        self.browser.get(self.live_server_url + '/logout')
        self.browser.delete_all_cookies()
        self.browser.get(self.live_server_url + '/login')

        self.assertNotEqual(
            self.live_server_url, self.browser.current_url, 'logout failed!'
        )

        # sanitity check the credentials
        self.client.logout()

    def login(self, user=USERNAME, password=PASSWORD, expected=True):
        print("BrowserTest.login(%s,%s,%s)" % (user, password, expected))
        # logout
        self.logout()

        login_status = self.client.login(username=user, password=password)

        print("user: %s" % user)
        print("password: %s" % password)
        print("login_status: %s" % login_status)
        print("expected: %s" % expected)

        self.assertEqual(login_status, expected,
                         'Unexpected login status (credentials)!')

        self.fill_in_form(username=user, password=password)
        if expected:
            self.assertPage('/frontpage/', 'login failed')
        else:
            self.assertPage('/login/', 'login successful')

    def element_text(self, elem_id):
        return self.browser.find_element_by_id(elem_id).text.strip().lower()

    def assertPage(self, expected_page, fail_message):
        print("expected: %s" % self.live_server_url + expected_page)
        print("got: %s" % self.browser.current_url)
        self.assertEquals(
            self.live_server_url + expected_page,
            self.browser.current_url,
            fail_message
        )


# @tag('selenium')
# @unittest.skipIf(not selenium, 'selenium not installed')
# class LoginTest(BrowserTest):
#
#     def test_login(self):
#         time.sleep(1)
#         self.login()
#         self.login(user="bogus", password="fail", expected=False)


class CrudTestMixin(object):

    def compare_result(self, created_object):
        for (key, expected) in self.form_params.items():
            actual = getattr(created_object, key)
            field = self.model._meta.get_field(key)
            if isinstance(actual, FieldFile):
                continue
            if field.choices is not None and len(field.choices) > 0:
                for (id, label) in field.choices:
                    if id == actual:
                        actual = label
                        break
            self.assertEquals(expected, actual)

    def test_create(self):
        print("%s.test_create" % self.__class__.__name__)
        self.login()
        self.browser.get(self.live_server_url + '/frontpage/')
        self.browser.find_element_by_id(
            self.create_button_id
        ).click()
        self.assertPage(self.create_page, "didn't end up on the correct page")
        self.fill_in_form('submit_save', **self.form_params)
        self.assertPage(self.list_page, "didn't end up on the correct page")

        created_object = self.model.objects.filter(name=self.form_params['name']).first()
        self.assertIsNotNone(created_object)
        self.compare_result(created_object)

        rows = self.browser.find_elements_by_css_selector(".update_%s_queryset_body>table>tbody>tr" % self.base_name)
        self.assertEquals(2, len(rows), 'must contain header and one row')
        actual_titles = [element.text for element in rows[0].find_elements_by_class_name('ordering')]
        self.assertListEqual(self.expected_titles, actual_titles, "List headers don't match what's expected")
        actual_values = [element.text for element in rows[1].find_elements_by_class_name('txtdata')]
        self.assertListEqual(self.expected_values, actual_values, "List data doesn't match what's expected")




@tag('selenium')
@unittest.skipIf(not selenium, 'selenium not installed')
class IdentityProviderAccountTest(CrudTestMixin, BrowserTest):

    model = IdentityProviderAccount
    base_name = 'identityprovideraccount'
    create_button_id = 'create_identityprovider_account'
    create_page = '/organisation/add/'
    list_page = '/organisation/list/'
    expected_titles = [u'Navn', u'Navn på kontaktperson', u'E-mailadresse på kontaktperson', u'IdP type', u'IdP Entity ID', u'Status']
    expected_values = [u'Magenta ApS', u'Peter Rasmussen', u'pera@magenta.dk', u'Primær IdP (ingen validering af brugerprofiler)', u'https://accounts.google.com/o/saml2?idpid=foobar', u'Aktiv']

    form_params = {
        'name': 'Magenta ApS',
        'contact_name': 'Peter Rasmussen',
        'contact_email': 'pera@magenta.dk',
        'idp_type': u'Primær IdP (ingen validering af brugerprofiler)',
        'metadata_xml_file': os.getcwd() +
                             "/static_files/testresources/test_metadata.xml",
        'userprofile_attribute': 'urn:user_profiles',
        'userprofile_attribute_format': 'Kommasepareret liste',
        'userprofile_adjustment_filter_type': 'Ingen tilpasninger',
        'organisation': u'Magenta leverer Grønlands datafordeler'
    }

