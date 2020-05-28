from builtins import object
from enum import Enum


class BootedStatus(Enum):
    Inactive = 'manually turned inactive or insufficient uptime'


class EposStatus(Enum):
    EligibleElected = 'eligible to be elected next epoch'


class OneUnit(object):
    Wei = 1.0 / 1.0e+18


class Uptime(object):
    RequiredThreshold = 2.0 / 3.0
