import unittest
import selinux

from Atomic import util


class TestAtomicUtil(unittest.TestCase):
    def test_image_by_name(self):
        matches = util.image_by_name('rhel7:latest')
        self.assertEqual(len(matches), 1)
        self.assertTrue(matches[0]['Id'].startswith('65de4a13fc7c'))

    def test_image_by_name_glob(self):
        matches = util.image_by_name('rhel*')
        self.assertEqual(len(matches), 2)
        self.assertTrue(any([m['Id'].startswith('f5f0b338bbd6') for m in
                             matches]))

    def test_image_by_name_tag_glob(self):
        matches = util.image_by_name('fedora:*')
        self.assertTrue(len(matches) > 1)

    def test_image_by_name_no_match(self):
        matches = util.image_by_name('this is not a real image name')
        self.assertTrue(len(matches) == 0)

    def test_default_container_context(self):
        exp = ('system_u:object_r:svirt_sandbox_file_t:s0' if
               selinux.is_selinux_enabled() else '')
        self.assertEqual(exp, util.default_container_context())


if __name__ == '__main__':
    unittest.main()
