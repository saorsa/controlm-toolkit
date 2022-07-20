import unittest
from parameterized import parameterized
from common import Environment, CommonEnvironmentType
from common.utils import generate_random_string


class EnvironmentTestCase(unittest.TestCase):

    def test_random_name(self):
        env_name = generate_random_string(50)
        e1 = Environment(env_name)

        self.assertIsNotNone(e1)
        self.assertIsNotNone(e1.name)
        self.assertEqual(e1.name, env_name)
        self.assertFalse(e1.is_common_environment)

        for ct in CommonEnvironmentType.__members__.values():
            self.assertFalse(e1.matches_common_type(ct))

    @parameterized.expand([
        'development',
        'Development',
        'DEVELOPMENT',
        'dEVelOPmEnT'
    ])
    def test_name_for_development(self, name):
        e = Environment(name)
        self.assertTrue(e.is_development)
        self.assertFalse(e.is_test)
        self.assertFalse(e.is_staging)
        self.assertFalse(e.is_production)
        self.assertTrue(e.is_common_environment)
        self.assertTrue(e.matches_common_type(CommonEnvironmentType.DEVELOPMENT))
        self.assertTrue(e.matches_environment_by_name(name))

    @parameterized.expand([
        'test',
        'TEST',
        'Test',
        'tEST'
    ])
    def test_name_for_test(self, name):
        e = Environment(name)
        self.assertFalse(e.is_development)
        self.assertTrue(e.is_test)
        self.assertFalse(e.is_staging)
        self.assertFalse(e.is_production)
        self.assertTrue(e.is_common_environment)
        self.assertTrue(e.matches_common_type(CommonEnvironmentType.TEST))
        self.assertTrue(e.matches_environment_by_name(name))

    @parameterized.expand([
        'staging',
        'Staging',
        'STAGING',
        'sTaGINg'
    ])
    def test_name_for_staging(self, name):
        e = Environment(name)
        self.assertFalse(e.is_development)
        self.assertFalse(e.is_test)
        self.assertTrue(e.is_staging)
        self.assertFalse(e.is_production)
        self.assertTrue(e.is_common_environment)
        self.assertTrue(e.matches_common_type(CommonEnvironmentType.STAGING))
        self.assertTrue(e.matches_environment_by_name(name))

    @parameterized.expand([
        'production',
        'Production',
        'PRODUCTION',
        'prodUCTion'
    ])
    def test_name_for_production(self, name):
        e = Environment(name)
        self.assertFalse(e.is_development)
        self.assertFalse(e.is_test)
        self.assertFalse(e.is_staging)
        self.assertTrue(e.is_production)
        self.assertTrue(e.is_common_environment)
        self.assertTrue(e.matches_common_type(CommonEnvironmentType.PRODUCTION))
        self.assertTrue(e.matches_environment_by_name(name))

    @parameterized.expand([
        ('production', 'Production'),
        ('production', 'proDUCTion'),
        ('staging', 'STAGING'),
    ])
    def test_comparison_to_environment(self, env1_name: str, env2_name: str):
        e1 = Environment(env1_name)
        e2 = Environment(env2_name)
        self.assertEqual(e1, e2)
        self.assertTrue(e1.matches_environment_by_name(e2.name))


if __name__ == '__main__':
    unittest.main()
