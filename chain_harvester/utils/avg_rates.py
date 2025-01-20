from decimal import Decimal

from chain_harvester.constants import SECONDS_PER_YEAR


def calculate_average_rate(previous_index, previous_time, current_index, current_time):
    time_difference = current_time - previous_time
    seconds = Decimal(time_difference.total_seconds())
    period = SECONDS_PER_YEAR / seconds
    return (current_index / previous_index) ** period - Decimal("1")
