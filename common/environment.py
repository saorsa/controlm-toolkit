import os
from abc import ABC
from enum import Enum


class CommonEnvironmentType(str, Enum):
    DEVELOPMENT = 'DEVELOPMENT'
    TEST = 'TEST'
    STAGING = 'STAGING'
    PRODUCTION = 'PRODUCTION'


class Environment (ABC):

    def __init__(self, name: str):
        self._name: str = name

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_development(self) -> bool:
        return self._name.lower() == CommonEnvironmentType.DEVELOPMENT.lower()

    @property
    def is_test(self) -> bool:
        return self._name.lower() == CommonEnvironmentType.TEST.lower()

    @property
    def is_staging(self) -> bool:
        return self._name.lower() == CommonEnvironmentType.STAGING.lower()

    @property
    def is_production(self) -> bool:
        return self._name.lower() == CommonEnvironmentType.PRODUCTION.lower()

    @property
    def is_common_environment(self) -> bool:
        return self._name.lower() in [
            CommonEnvironmentType.DEVELOPMENT.lower(),
            CommonEnvironmentType.TEST.lower(),
            CommonEnvironmentType.STAGING.lower(),
            CommonEnvironmentType.PRODUCTION.lower()
        ]

    def matches_common_type(self, env_type: CommonEnvironmentType) -> bool:
        return env_type and self.matches_environment_by_name(env_type.lower())

    def matches_environment_by_name(self, env_name: str) -> bool:
        return env_name and self._name.lower() == env_name.lower()

    def __str__(self) -> str:
        return f"Environment = {self.name}"

    def __eq__(self, other) -> bool:
        if isinstance(other, Environment):
            return self.matches_environment_by_name(other.name)
        return False


def get_environment(env_var_name: str = 'CONTROLM_ENVIRONMENT') -> Environment:
    env_name = os.environ.get(env_var_name, CommonEnvironmentType.DEVELOPMENT)
    return Environment(env_name)
