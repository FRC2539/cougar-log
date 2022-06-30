# Cougar Log

**Cougar Log is a CLI for rapidly converting and visualizing .wpilog files!**

See the following page for a guide on creating these files inside of an FRC robotics project:

[https://docs.wpilib.org/en/stable/docs/software/telemetry/datalog.html](https://docs.wpilib.org/en/stable/docs/software/telemetry/datalog.html)

## Quickstart

### Installation

Run the following to install `cougar-log` using pip:

```
pip install cougar-log
```

### Basic Usage Examples

_See the documentation below this section for more specific capabilities of this CLI._

In this example, we have a file in our current directory called `my_data_log.wpilog`.

#### Converting to CSV

```
cougar-log convert -i my_data_log.wpilog
```

_or, to convert any file in the given folder:_

```
cougar-log convert -i .
```

#### Displaying as a Table

```
cougar-log table -i my_data_log.wpilog
```

#### Graphing Data

```
cougar-log graph -i my_data_log.wpilog
```

#### Filtering

Any of these commands can be used with a filter flag (`-f/--filter`) in order to select only the entries that have that name.

Use the table option to see the names of all of the log entries.

```
cougar-log graph -i my_data_log.wpilog -f /temps/drive
```

## Documentation

Click the link below to visit the documentation:

[frc2539.github.io/cougar-log](https://frc2539.github.io/cougar-log)