from pathlib import Path

import typer

from cougar_log.log_helpers import HEADER_LIST, filter_dataframe, read_log_to_dataframe

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
        prompt="Enter the path to the file to convert",
        help="The file provided to convert.",
    ),
    output_path: Path = typer.Option(
        "output.csv",
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
):
    """
    This command will convert a given wpilog file into a csv.

    Optionally use filter to select only logs containing a given name.
    """
    [log_dataframe, error] = read_log_to_dataframe(input_path=input_path)

    if error is not None:
        exit_with_error(error)

    if name_filter is not None:
        log_dataframe = filter_dataframe(log_dataframe, name_filter=name_filter)

    log_dataframe.to_csv(output_path, index=False)

    typer.echo("Successfully converted and exported the provided file!")


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

    from tabulate import tabulate

    typer.echo(tabulate(log_dataframe.set_index(HEADER_LIST[0]), headers=HEADER_LIST))


@app.command()
def visualize():
    typer.echo("Random")
