# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals, print_function
from dafousers import models
from django import test
from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.core.management import call_command
from django.db.models.fields.files import FieldFile
from django.db.models.fields.related import ManyToManyField
from django.test import tag

import contextlib
import datetime
import os
import platform
import shutil
import time
import unittest

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


    @classmethod
    def tearDownClass(cls):
        super(BrowserTest, cls).tearDownClass()
        cls.browser.quit()

    def fill_in_form(self, submit_id=None, **kwargs):
        for field, value in kwargs.items():

            if field in ['user_profiles', 'system_roles', 'area_restrictions']:
                id = "id_" + field
                select = self.browser.find_element_by_id(id + '_from')
                options = select.find_elements_by_tag_name('option')
                for option in options:
                    if option.text.strip() in value:
                        self.click(option)
                add_button = self.browser.find_element_by_id(id + '_add_link')
                self.click(add_button)

            else:
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

            self.assertEqual(login_status, expected,
                             'Unexpected login status (credentials)!')

            self.fill_in_form(username=user, password=password)
            if expected:
                self.assert_page('/frontpage/')
            else:
                self.assert_page('/login/')
            self.logged_in = True

    def element_text(self, elem_id):
        return self.browser.find_element_by_id(elem_id).text.strip().lower()

    def assert_page(self, expected_page):
        self.assertEquals(
            self.live_server_url + expected_page,
            self.browser.current_url,
            "expected: %s, got %s" % (self.live_server_url + expected_page, self.browser.current_url)
        )

    def assert_lists(self, expected_list, actual_list, list_name):
        for expected, actual in zip(expected_list, actual_list):
            if type(expected) == datetime.datetime:
                expected = expected.strftime("%Y-%m-%d")
                try:
                    assert expected in actual
                except AssertionError as e:
                    raise(
                        AssertionError(
                            "%s %s doesn't contain what is expected %s." % (list_name, actual, expected)
                        )
                    )

            else:
                self.assertEqual(
                    expected,
                    actual,
                    "%s %s doesn't match what is expected %s." % (list_name, actual, expected)
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
    create_page = 'add/'
    list_page = 'list/'
    edit_page = '%d/'

    def m2m_label_to_id(self, related_model, value):
        return related_model.objects.get(name=value).pk

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
            try:
                field = self.model._meta.get_field(key)
                if field.related_model is not None:
                    value = self.m2m_label_to_id(field.related_model, value)
                if field.choices is not None and len(field.choices) > 0:
                    value = self.choice_label_to_id(field.choices, value)
                out[key] = value
            except FieldDoesNotExist:
                if key != u'certificate_years_valid':
                    print("The field %s does not exist." % key)
        return out

    def compare_result(self, created_object, params):
        for (key, expected) in self.convert_form_params(params).items():
            actual = getattr(created_object, key)
            field = self.model._meta.get_field(key)
            if isinstance(actual, FieldFile):
                continue
            if isinstance(field, ManyToManyField):
                continue
            self.assertEquals(expected, actual)

    def get_row_with_name(self, rows, name):
        for row in rows:
            elements = row.find_elements_by_class_name('txtdata')
            if len(elements) > 0:
                if elements[0].text == name:
                    return row

    def test_create(self):
        print("%s.test_create" % self.__class__.__name__)
        self.login()
        self.browser.get(self.live_server_url + self.frontpage)
        self.browser.find_element_by_id(
            self.create_button_id
        ).click()
        self.assert_page(self.page + self.create_page)
        self.fill_in_form('submit_save', **self.create_form_params)
        self.assert_page(self.page + self.list_page)

        created_object = self.model.objects.search(self.object_name).first()
        self.assertIsNotNone(created_object)
        self.compare_result(created_object, self.create_form_params)

        rows = self.browser.find_elements_by_css_selector(".update_%s_queryset_body>table>tbody>tr" % self.base_name)
        self.assertEquals(
            self.expected_number_of_objects, len(rows) - 1,
                          'must contain %s rows, however %s found' %
                          (self.expected_number_of_objects, len(rows) - 1)
        )
        actual_titles = [element.text for element in rows[0].find_elements_by_class_name('ordering')]
        self.assert_lists(self.expected_titles, actual_titles, "List headers")
        object_row = self.get_row_with_name(rows, self.object_name)
        actual_values = [element.text for element in object_row.find_elements_by_class_name('txtdata')]
        self.assert_lists(self.expected_values, actual_values, "List data")

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

        # First save the object and then m2m fields
        singleton_params = {
            key: value for key, value in create_params.items()
            if not isinstance(self.model._meta.get_field(key), ManyToManyField)
        }
        m2m_params = {
            key: value for key, value in create_params.items()
            if isinstance(self.model._meta.get_field(key), ManyToManyField)
        }

        created_object = self.model(**singleton_params)
        created_object.save()
        for key, value in m2m_params.items():
            created_object.user_profiles.add(value)
            # If there is a certificate years valid field then create a certificate
            if 'certificate_years_valid' in self.create_form_params.keys():
                created_object.create_certificate(self.certificate_years)

        # Test that the item exists in the item list
        self.browser.get(self.live_server_url + self.page + self.list_page)
        rows = self.browser.find_elements_by_css_selector(".update_%s_queryset_body>table>tbody>tr" % self.base_name)
        self.assertEquals(
            self.expected_number_of_objects, len(rows) - 1,
                                             'must contain %s rows, however %s found' %
                                             (self.expected_number_of_objects, len(rows) - 1)
        )
        object_row = self.get_row_with_name(rows, self.object_name)
        actual_values = [element.text for element in object_row.find_elements_by_class_name('txtdata')]
        self.assert_lists(self.expected_values, actual_values, "List data")
        link = object_row.find_elements_by_css_selector('.txtdata>a')[0]
        link.click()
        self.assert_page((self.page + self.edit_page) % created_object.pk)

        # Test that the item can be searched
        self.browser.get(self.live_server_url + self.frontpage)
        search_field = self.browser.find_element_by_id('search_org_user_system')
        search_field.clear()
        search_field.send_keys(self.object_name[0:6])
        time.sleep(5)
        # self.browser.implicitly_wait(5)

        result_list = self.browser.find_elements_by_css_selector('#search_org_user_system_results>a')
        result_link = None
        sought_text = "%s: %s" % (self.model._meta.verbose_name.title(), self.object_name)
        for link in result_list:
            if link.text == sought_text:
                result_link = link
                break
        self.assertIsNotNone(result_link)
        result_link.click()
        self.assert_page((self.page + self.edit_page) % created_object.pk)

        # Edit the form
        self.fill_in_form('submit_save', **self.edit_form_params)
        self.assert_page(self.page + self.list_page)

        updated_params = dict(self.create_form_params.items() + self.edit_form_params.items())

        created_object = self.model.objects.search(self.object_name).first()
        self.compare_result(created_object, updated_params)



@tag('selenium')
@unittest.skipIf(not selenium, 'selenium not installed')
class IdentityProviderAccountTest(CrudTestMixin, BrowserTest):

    model = models.IdentityProviderAccount
    base_name = 'identityprovideraccount'
    create_button_id = 'create_identityprovider_account'
    page = '/organisation/'

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
        'organisation': u'Magenta leverer Grønlands datafordeler',
        'status': u'Aktiv',
        'user_profiles': u'DAFO Serviceudbyder'
    }

    edit_form_params = {
        'idp_type': u'Sekundær IdP (kan kun udstede angivne brugerprofiler)',
        'metadata_xml_file': resource_path + "/test_metadata.xml"
    }

    object_name = create_form_params['name']

    expected_titles = [
        u'Navn',
        u'Navn på kontaktperson',
        u'E-mailadresse på kontaktperson',
        u'IdP type',
        u'IdP Entity ID',
        u'Status'
    ]

    expected_values = [
        object_name,
        create_form_params['contact_name'],
        create_form_params['contact_email'],
        create_form_params['idp_type'],
        u'https://accounts.google.com/o/saml2?idpid=foobar',
        create_form_params['status']
    ]

    expected_number_of_objects = 1

@tag('selenium')
@unittest.skipIf(not selenium, 'selenium not installed')
class PasswordUserTest(CrudTestMixin, BrowserTest):

    model = models.PasswordUser
    base_name = 'passworduser'
    create_button_id = 'create_password_user'
    page = '/user/'

    files = []

    create_form_params = {
        'givenname': u'Peter',
        'lastname': u'Rasmussen',
        'email': u'pera@magenta.dk',
        'organisation': u'Magenta ApS',
        'status': u'Aktiv',
        'user_profiles': u'DAFO Serviceudbyder'
    }

    edit_form_params = {
        'email': u'pera@magenta2.dk',
        'organisation': u'Magenta 2 ApS'
    }

    object_name = create_form_params['givenname'] + " " + create_form_params['lastname']

    expected_titles = [
        u'Bruger',
        u'Email',
        u'Arbejdssted',
        u'Status'
    ]

    expected_values = [
        object_name,
        create_form_params['email'],
        create_form_params['organisation'],
        create_form_params['status']
    ]

    expected_number_of_objects = 3


@tag('selenium')
@unittest.skipIf(not selenium, 'selenium not installed')
class CertificateUserTest(CrudTestMixin, BrowserTest):

    model = models.CertificateUser
    base_name = 'certificateuser'
    create_button_id = 'create_certificate_user'
    page = '/system/'

    files = []

    create_form_params = {
        'name': u'Magenta ApS',
        'identification_mode': u'Identificerer brugere via \'på-vegne-af\'',
        'contact_name': u'Peter Rasmussen',
        'contact_email': u'pera@magenta.dk',
        'certificate_years_valid': u'3 år',
        'organisation': u'Magenta leverer Grønlands Datafordeler',
        'comment': u'I følge aftale.',
        'status': u'Aktiv',
        'user_profiles': u'DAFO Serviceudbyder'
    }

    edit_form_params = {
    }

    edit_form_action = 'delete_invalid_certificates'

    object_name = create_form_params['name']

    expected_titles = [
        u'Navn',
        u'Næste udløbsdato',
        u'Identifikationsmetode',
        u'Navn på kontaktperson',
        u'E-mailadresse på kontaktperson',
        u'Status'
    ]

    d = datetime.datetime.now()
    certificate_years = 3
    d = d + datetime.timedelta(days=(certificate_years*365))

    expected_values = [
        object_name,
        d,
        create_form_params['identification_mode'],
        create_form_params['contact_name'],
        create_form_params['contact_email'],
        create_form_params['status']
    ]

    expected_number_of_objects = 1
