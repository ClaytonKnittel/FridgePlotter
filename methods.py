from files import FridgeFile
from math import log10
from decimal import Decimal


# returns True if the string input is an
# integer, and False otherwise
def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        pass
    return False


# returns the order of magnitude of a value.
# i.e. order_of_magnitude(130) = .01
# and order_of_magnitude(.0014) = .001
def order_of_magnitude(val):
    if val == 0:
        return 1
    val = abs(val)
    scale = 1
    while abs(val) * scale < 1:
        scale *= 10
    while abs(val) * scale >= 10:
        scale /= 10
    return scale


def get_most_recent_record_date(date):
    dateret = date.__copy__()
    for x in range(0, 400):
        try:
            f = FridgeFile(date.tostring(), chamber=6)
            f.open()
            return date
        except IOError:
            try:
                date.subtract()
            except IndexError:
                print('No LOG files have appeared')
                return
            continue
    return dateret


chambers = ['1', '2', '5', '6', 'ovc_1', 'still', 'condense', 'ln2_trap', 'tank', 'ovc_2', 'flowmeter']


def convert(i):
    return chambers[i]


def round_sf(num, sig_figs=4):
    if num == 0:
        return 0
    if num < 0:
        return -round(-num, -int(log10(-num)) + sig_figs - 1)
    return round(num, -int(log10(num)) + sig_figs - 1)

def round_int(num):
    if num < 0:
        return -round_int(-num)
    i = int(num)
    if num - i < .5:
        return i
    return i + 1


def decimal_sf(num, sig_figs=4):
    return ('{:.' + str(sig_figs) + 'f}').format(num)


def scientific_sf(num, sig_figs=4):
    return ('%.' + str(sig_figs - 1) + 'E') % Decimal(num)


unit_prefixes = ('a', 'f', 'p', 'n', '\u03bc', 'm', '', 'k', 'M', 'G', 'T', 'P', 'E')
scientific = True
standard = False


def get_pref_method(units):
    if units == 'K':
        return temp_pref
    elif units == 'bar':
        return pres_pref
    elif units == 'mol/s':
        return flow_pref
    elif units == 'log bar':
        return log_pres_pref
    else:
        return def_pref


# dummy unit is usually middle value, used so every number is converted the same way
def get_unit_display(num, unit, unit_config_strategy=None, dummy_value=None):
    if unit_config_strategy is None:
        unit_config_strategy = get_pref_method(unit)

    if dummy_value is not None:
        factor, pref, s = unit_config_strategy(dummy_value)
    else:
        factor, pref, s = unit_config_strategy(num)

    num *= 1000 ** factor
    if s:
        return scientific_sf(num) + ' ' + pref + unit
    return decimal_sf(num) + ' ' + pref + unit


# dummy unit is usually middle value, used so every number is converted the same way
def get_unitless_display(num, unit, unit_config_strategy=None, dummy_value=None):
    if unit_config_strategy is None:
        unit_config_strategy = get_pref_method(unit)

    if dummy_value is not None:
        factor, pref, s = unit_config_strategy(dummy_value)
    else:
        factor, pref, s = unit_config_strategy(num)

    num *= 1000 ** factor
    if s:
        return scientific_sf(num)
    return decimal_sf(num)


# dummy unit is usually middle value, used so every number is converted the same way
def unit_display(dummy_value, unit, unit_config_strategy=None):
    if unit_config_strategy is None:
        unit_config_strategy = get_pref_method(unit)
    factor, pref, s = unit_config_strategy(dummy_value)
    return pref + unit


# figures out which prefix to given units (m (milli), k (kilo), M (mega), etc.)
# to use for a given input number, and then returns the factor of 1000 the number was
# scaled by and the prefix of the units to be used
def def_pref(num):
    if num == 0:
        return 0, '', standard
    factor = 0
    while abs(num) * (1000 ** -factor) < .1:
        factor -= 1
    while abs(num) * (1000 ** -factor) >= 100:
        factor += 1
    return -factor, unit_prefixes[factor + 6], standard


def temp_pref(num):
    if num < .1:
        return 1, 'm', standard
    return 0, '', standard


def pres_pref(num):
    return 1, 'm', scientific


def log_pres_pref(num):
    return 0, '', standard


def flow_pref(num):
    return 0, '', scientific
