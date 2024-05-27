"""Constants for the Integration 101 Template integration."""

DOMAIN = "msp_integration_101_requests_example"

DEFAULT_SCAN_INTERVAL = 60
MIN_SCAN_INTERVAL = 10

BINARY_SENSORS = ["charge_enabled", "float_mode", "manual_charge", "logs"]

VOLTAGE_SENSORS = [
    "absorption_voltage",
    "force_chg_v",
    "min_discharge_v",
    "min_voltage_cell",
    "max_voltage_cell",
    "min_cell_voltage",
    "max_cell_voltage",
    "delta_cell_voltage",
    "average_cell_voltage",
    "cell_voltage_1",
    "cell_voltage_2",
    "cell_voltage_3",
    "cell_voltage_4",
]

CURRENT_SENSORS = ["charge_current", "discharge_current"]

BATTERY_SENSORS = ["battery_soh"]

TIME_SENSORS = ["uptime"]

OTHER_SENSORS = ["charge_status", "slaves_total"]
