# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function

import contextlib
import os
import platform
import unittest
from django import test
from django.core.management import call_command
from django.db.models.fields.files import FieldFile
from django.test import tag
import shutil
import time

from django.conf import settings

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

class BrowserTest(test.LiveServerTestCase, test.TestCase):

    @classmethod
    def setUpClass(cls):

        call_command('collectstatic', verbosity=0, interactive=False)

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
                        self.click(option)
                        break
                else:
                    self.fail('{} not one of {}'.format(
                        value, [o.text for o in options]),
                    )
            elif (e.tag_name == 'input' and
                          e.get_attribute('type') in ('checkbox', 'radio')):
                if value != e.is_selected():
                    self.click(e)
            else:
                self.fail('unhandled input element (' + e.tag_name + '): ' +
                          e.get_attribute('outerHTML'))

        if submit_id is not None:
            submit = self.browser.find_element_by_id(submit_id)
        else:
            submit = self.browser.find_element_by_css_selector(
                "input[type=submit]",
            )
        self.click(submit)

    def click(self, element):
        self.browser.execute_script("arguments[0].scrollIntoView();", element)
        element.click()


# self.await_staleness(submit)

    logged_in = False

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
        self.logged_in = False

    def login(self, user=USERNAME, password=PASSWORD, expected=True, force=False):
        print("BrowserTest.login(%s,%s,%s,%s)" % (user, password, expected, force))
        if force or not self.logged_in:
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
                self.assertPage('/frontpage/')
            else:
                self.assertPage('/login/')
            self.logged_in = True

    def element_text(self, elem_id):
        return self.browser.find_element_by_id(elem_id).text.strip().lower()

    def assertPage(self, expected_page):
        self.assertEquals(
            self.live_server_url + expected_page,
            self.browser.current_url,
            "expected: %s, got %s" % (self.live_server_url + expected_page, self.browser.current_url)
        )


@tag('selenium')
@unittest.skipIf(not selenium, 'selenium not installed')
class LoginTest(BrowserTest):

    def test_login(self):
        time.sleep(1)
        self.login(force=True)
        self.login(user="bogus", password="fail", expected=False, force=True)


class CrudTestMixin(object):

    frontpage = '/frontpage/'

    def choice_label_to_id(self, choices, label):
        for (id, choice_label) in choices:
            if choice_label == label:
                return id

    def choice_id_to_label(self, choices, id):
        for (choice_id, label) in choices:
            if choice_id == id:
                return label

    def convert_form_params(self, params):
        out = {}
        for (key, value) in params.items():
            field = self.model._meta.get_field(key)
            if field.choices is not None and len(field.choices) > 0:
                value = self.choice_label_to_id(field.choices, value)
            out[key] = value
        return out

    def compare_result(self, created_object, params):
        for (key, expected) in self.convert_form_params(params).items():
            actual = getattr(created_object, key)
            if isinstance(actual, FieldFile):
                continue
            self.assertEquals(expected, actual)

    def test_create(self):
        print("%s.test_create" % self.__class__.__name__)
        self.login()
        self.browser.get(self.live_server_url + self.frontpage)
        self.browser.find_element_by_id(
            self.create_button_id
        ).click()
        self.assertPage(self.create_page)
        self.fill_in_form('submit_save', **self.create_form_params)
        self.assertPage(self.list_page)

        created_object = self.model.objects.filter(name=self.create_form_params['name']).first()
        self.assertIsNotNone(created_object)
        self.compare_result(created_object, self.create_form_params)

        rows = self.browser.find_elements_by_css_selector(".update_%s_queryset_body>table>tbody>tr" % self.base_name)
        self.assertEquals(2, len(rows), 'must contain header and one row')
        actual_titles = [element.text for element in rows[0].find_elements_by_class_name('ordering')]
        self.assertListEqual(self.expected_titles, actual_titles, "List headers don't match what's expected")
        actual_values = [element.text for element in rows[1].find_elements_by_class_name('txtdata')]
        self.assertListEqual(self.expected_values, actual_values, "List data doesn't match what's expected")

    def test_edit(self):
        print("%s.test_edit" % self.__class__.__name__)
        self.login()
        for file in self.files:
            shutil.copy(file, settings.MEDIA_ROOT)
        create_params = {'changed_by': USERNAME}
        create_params.update(self.convert_form_params(self.create_form_params))

        for (key, value) in create_params.items():
            if value in self.files:
                create_params[key] = settings.MEDIA_ROOT + os.sep + value[value.rindex(os.sep):]

        created_object = self.model(**create_params)
        created_object.save()

        # Test that the item exists in the item list
        self.browser.get(self.live_server_url + self.list_page)
        rows = self.browser.find_elements_by_css_selector(".update_%s_queryset_body>table>tbody>tr" % self.base_name)
        self.assertEquals(2, len(rows), 'must contain header and one row')
        actual_values = [element.text for element in rows[1].find_elements_by_class_name('txtdata')]
        self.assertListEqual(self.expected_values, actual_values, "List data doesn't match what's expected")
        link = rows[1].find_elements_by_css_selector('.txtdata>a')[0]
        link.click()
        self.assertPage(self.edit_page % created_object.pk)

        # Test that the item can be searched
        name = self.create_form_params['name']
        self.browser.get(self.live_server_url + self.frontpage)
        search_field = self.browser.find_element_by_id('search_org_user_system')
        search_field.clear()
        search_field.send_keys(name[0:6])
        time.sleep(5)
        # self.browser.implicitly_wait(5)

        resultList = self.browser.find_elements_by_css_selector('#search_org_user_system_results>a')
        resultLink = None
        sought_text = "%s: %s" % (self.model._meta.verbose_name.title(), name)
        for link in resultList:
            if link.text == sought_text:
                resultLink = link
                break
        self.assertIsNotNone(resultLink)
        resultLink.click()
        self.assertPage(self.edit_page % created_object.pk)

        # Edit the form
        self.fill_in_form('submit_save', **self.edit_form_params)
        self.assertPage(self.list_page)

        updated_params = dict(self.create_form_params.items() + self.edit_form_params.items())
        # Same as:
        # updated_params = {}
        # updated_params.update(self.create_form_params)
        # updated_params.update(self.edit_form_params)

        created_object = self.model.objects.filter(name=updated_params['name']).first()
        self.compare_result(created_object, updated_params)



@tag('selenium')
@unittest.skipIf(not selenium, 'selenium not installed')
class IdentityProviderAccountTest(CrudTestMixin, BrowserTest):

    model = IdentityProviderAccount
    base_name = 'identityprovideraccount'
    create_button_id = 'create_identityprovider_account'
    create_page = '/organisation/add/'
    list_page = '/organisation/list/'
    edit_page = '/organisation/%d/'
    expected_titles = [u'Navn', u'Navn på kontaktperson', u'E-mailadresse på kontaktperson', u'IdP type', u'IdP Entity ID', u'Status']
    expected_values = [u'Magenta ApS', u'Peter Rasmussen', u'pera@magenta.dk', u'Primær IdP (ingen validering af brugerprofiler)', u'https://accounts.google.com/o/saml2?idpid=foobar', u'Aktiv']

    resource_path = os.path.abspath(os.getcwd() + "/../testresources")
    files = [
        resource_path + "/test_metadata.xml"
    ]

    create_form_params = {
        'name': 'Magenta ApS',
        'contact_name': 'Peter Rasmussen',
        'contact_email': 'pera@magenta.dk',
        'idp_type': u'Primær IdP (ingen validering af brugerprofiler)',
        'metadata_xml_file': resource_path + "/test_metadata.xml",
        'userprofile_attribute': 'urn:user_profiles',
        'userprofile_attribute_format': 'Kommasepareret liste',
        'userprofile_adjustment_filter_type': 'Ingen tilpasninger',
        'organisation': u'Magenta leverer Grønlands datafordeler'
    }

    edit_form_params = {
        'idp_type': u'Sekundær IdP (kan kun udstede angivne brugerprofiler)',
        'metadata_xml_file': resource_path + "/test_metadata.xml",
    }
