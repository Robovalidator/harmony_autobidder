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


class EpochStats(object):
    FirstEpoch = 186
    FirstBlock = int("0x338000", 16)
    EpochSize = int("0x4000", 16)
    SecondsPerBlock = 8.0


class TimeUnit(object):
    Second = 1
    Minute = 60
    Hour = 60 * Minute
    Day = 24 * Hour
