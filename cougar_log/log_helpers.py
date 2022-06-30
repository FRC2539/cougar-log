from datetime import datetime
from pathlib import Path
from numpy import average

import typer
import pandas as pd
import matplotlib.pyplot as plt

from cougar_log.data_log_reader import DataLogReader

HEADER_LIST = ["Timestamp", "Name", "Value"]


def filter_dataframe(dataframe: pd.DataFrame, name_filter: str):
    return dataframe.loc[dataframe[HEADER_LIST[1]] == name_filter]


def exclude_from_dataframe(dataframe: pd.DataFrame, name_to_exclude: str):
    return dataframe.loc[dataframe[HEADER_LIST[1]] != name_to_exclude]


def read_log_to_dataframe(input_path: Path):
    if input_path is None:
        return [None, "No input file provided"]

    if input_path.is_file():
        # Verify the file format of the provided path
        if input_path.suffix != ".wpilog":
            return [None, "Invalid file format provided. Try providing a .wpilog file."]

        [output, error] = convert_data_log_to_list(input_path=input_path)

        if error is not None:
            return [None, error]

        # Convert the log data to a pandas dataframe
        log_dataframe = pd.DataFrame(output)

        log_dataframe.columns = HEADER_LIST

        return [log_dataframe, error]

    elif input_path.is_dir():
        return [None, "The given input file is a directory."]
    elif not input_path.exists():
        return [None, "The input file doesn't exist"]


def convert_data_log_to_list(input_path: str):
    import mmap

    output = []

    error = None

    error_message = "Invalid file, verify that the file is a wpilog or try downloading the log file again."

    with open(input_path, "r") as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        reader = DataLogReader(mm)

        entries = {}

        for record in reader:
            # Store all record starting data in the entries dictionary
            if record.isStart():
                try:
                    data = record.getStartData()
                    entries[data.entry] = data
                except TypeError as e:
                    error = error_message

            # Delete the finish entry of the current record
            elif record.isFinish():
                try:
                    entry = record.getFinishEntry()
                    if entry in entries:
                        del entries[entry]
                except TypeError as e:
                    error = error_message

            # Verify any available metadata
            elif record.isSetMetadata():
                try:
                    data = record.getSetMetadataData()
                except TypeError as e:
                    error = error_message

            # Verify that the type of the record is recognized
            elif record.isControl():
                error = error_message

            # Extract and store the information from the current record
            else:
                entry = entries.get(record.entry, None)

                if entry is None:
                    continue

                output.append(extract_value_from_entry(entry, record))

    return [output, error]


def extract_value_from_entry(entry, record):
    timestamp = record.timestamp / 1000000

    value = None

    # Handle the system time-type entries
    if entry.name == "systemTime" and entry.type == "int64":
        dt = datetime.fromtimestamp(record.getInteger() / 1000000)
        value = "{:%Y-%m-%d %H:%M:%S.%f}".format(dt)
    else:
        match entry.type:
            case "double":
                value = record.getDouble()
            case "int64":
                value = record.getInteger()
            case "string" | "json":
                value = record.getString()
            case "boolean":
                value = record.getBoolean()
            case "boolean[]":
                value = list(record.getBooleanArray())
            case "double[]":
                value = list(record.getDoubleArray())
            case "float[]":
                value = list(record.getFloatArray())
            case "int64[]":
                value = list(record.getIntegerArray())
            case "string[]":
                value = list(record.getStringArray())

    return [timestamp, entry.name, value]


def plot_dataframe(dataframe: pd.DataFrame):
    _, axes = plt.subplots(nrows=1, ncols=1, num="Cougar Log")

    axes.set_xlabel("Timestamp")
    axes.set_ylabel("Value")
    axes.set_title("WPILOG Graph")

    # Automatically filter out all system time entries
    dataframe = exclude_from_dataframe(dataframe, "systemTime")

    all_names = dataframe[HEADER_LIST[1]].unique()

    for name in all_names:
        filtered_dataframe = filter_dataframe(dataframe, name)

        # Include only timestamps and values
        filtered_dataframe = filtered_dataframe[[HEADER_LIST[0], HEADER_LIST[2]]]

        try:
            plt.plot(
                filtered_dataframe["Timestamp"].values,
                [average(x) for x in filtered_dataframe["Value"].values],
                label=name,
            )
        except:
            typer.echo(f"Skipping '{name}' as graphing of this type is not supported")

    plt.legend()
    plt.show()
