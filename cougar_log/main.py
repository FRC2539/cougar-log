from pathlib import Path
import click_spinner

import typer

from cougar_log.log_helpers import (
    HEADER_LIST,
    exclude_from_dataframe,
    filter_dataframe,
    plot_dataframe,
    read_log_to_dataframe,
)
from cougar_log.ssh_download import RobotSSHInterface

app = typer.Typer()


def exit_with_error(error):
    typer.echo(f"Error: {error}")
    raise typer.Exit(code=1)


@app.command()
def convert(
    input_path: Path = typer.Option(
        None,
        "--input",
        "-i",
        prompt="Enter the path to the file/directory to convert",
        help="The file/directory provided to convert.",
    ),
    output_path: Path = typer.Option(
        None,
        "--output",
        "-o",
        help="The name of the resulting file.",
    ),
    name_filter: str = typer.Option(
        None,
        "--filter",
        "-f",
        help="Filter by a specific name in the logs.",
    ),
    include_system_time: bool = typer.Option(
        False,
        "--include-system-time",
        "-t",
        help="Whether or not to include system time in the output.",
    ),
):
    """
    This command will convert a given wpilog file or directory of files into csv files.

    Optionally use filter to select only log entries containing a given name.
    """
    # Convert all files in the given directory, or convert just a single given file.
    if input_path.is_dir():
        for file in input_path.iterdir():
            # Convert all valid files within the given folder
            if file.is_dir() or not file.is_file() or file.suffix != ".wpilog":
                continue
            else:
                convert_file(file, None, name_filter, include_system_time)
    else:
        convert_file(input_path, output_path, name_filter, include_system_time)


def convert_file(
    input_path: Path, output_path: Path, name_filter: str, include_system_time: bool
):
    [log_dataframe, error] = read_log_to_dataframe(input_path=input_path)

    if error is not None:
        exit_with_error(error)

    if name_filter is not None:
        log_dataframe = filter_dataframe(log_dataframe, name_filter=name_filter)

    if not include_system_time:
        log_dataframe = exclude_from_dataframe(
            log_dataframe, name_to_exclude="systemTime"
        )

    if output_path is None:
        output_path = input_path.stem + ".csv"

    log_dataframe.to_csv(output_path, index=False)

    typer.echo(f"Successfully converted and exported the log to '{output_path}'")


@app.command()
def table(
    input_path: Path = typer.Option(
        None,
        "--input",
        "-i",
        prompt="Enter the path to the file to tabulate",
        help="The file provided to tabulate.",
    ),
    name_filter: str = typer.Option(
        None,
        "--filter",
        "-f",
        help="Filter by a specific name in the logs.",
    ),
    include_system_time: bool = typer.Option(
        False,
        "--include-system-time",
        "-t",
        help="Whether or not to include system time in the output.",
    ),
):
    """
    This command will display the contents of a wpilog file in a table.

    Optionally use filter to select only logs containing a given name.
    """
    [log_dataframe, error] = read_log_to_dataframe(input_path=input_path)

    if error is not None:
        exit_with_error(error)

    if name_filter is not None:
        log_dataframe = filter_dataframe(log_dataframe, name_filter=name_filter)

    if not include_system_time:
        log_dataframe = exclude_from_dataframe(
            log_dataframe, name_to_exclude="systemTime"
        )

    from tabulate import tabulate

    typer.echo(tabulate(log_dataframe.set_index(HEADER_LIST[0]), headers=HEADER_LIST))


@app.command()
def graph(
    input_path: Path = typer.Option(
        None,
        "--input",
        "-i",
        prompt="Enter the path to the file to graph",
        help="The file provided to graph.",
    ),
    name_filter: str = typer.Option(
        None,
        "--filter",
        "-f",
        help="Filter by a specific name in the logs.",
    ),
):
    """
    This command will display the contents of a wpilog file in a graph.

    Optionally use filter to select only logs containing a given name.
    """
    [log_dataframe, error] = read_log_to_dataframe(input_path=input_path)

    if error is not None:
        exit_with_error(error)

    if name_filter is not None:
        log_dataframe = filter_dataframe(log_dataframe, name_filter=name_filter)

    typer.echo("Creating a graph from the given log.")

    plot_dataframe(log_dataframe)


@app.command()
def download(
    directory: str = typer.Option(
        ".",
        "--directory",
        "-d",
        help="The directory to download files from.",
    ),
    save_directory: str = typer.Option(
        "./logs",
        "--save-directory",
        "-s",
        help="The directory to save downloaded files in.",
    ),
    remove: bool = typer.Option(
        True,
        help="Whether or not to delete log files from the robot after downloading them.",
    ),
    host: str = typer.Option(
        None,
        "--host",
        "-h",
        prompt="Enter the host to connect to (ip/hostname)",
        help="The host to download files from.",
    ),
    user: str = typer.Option(
        "lvuser",
        "--user",
        "-u",
        help="The user to authenticate as.",
    ),
    password: str = typer.Option(
        "",
        help="The password used for connecting to the robot. By default FRC robots have no password.",
    ),
    port: int = typer.Option(
        22,
        "--port",
        "-p",
        help="The port to use for the ssh connection.",
    ),
):
    """
    This command will connect to a robot and download log files from the robot.
    """

    typer.echo("Connecting to the robot ... ", nl=False)

    with click_spinner.spinner():
        interface = RobotSSHInterface(host, user, password, port, remove_files=remove)

    typer.echo("Connected!")

    typer.echo("Downloading log files ... ", nl=False)

    with click_spinner.spinner():
        error = interface.download_from_directory(
            source_directory=directory, target_directory=save_directory, remove=remove
        )

    if error is not None:
        exit_with_error(error)

    typer.echo("Download complete!")

    interface.close_interface()
