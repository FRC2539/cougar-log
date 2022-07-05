from fabric import Connection
from pathlib import Path, PurePosixPath


class RobotSSHInterface:
    """Robot SSH Interface enables remote communcation with the robot for downloading files."""

    def __init__(
        self, host: str, user: str, password: str, port: int, remove_files: bool
    ):
        self.remove_files = remove_files

        connect_kwargs = {} if password is None else {"password": password}

        # Create an ssh connection to the robot
        self.connection = Connection(
            host=host, user=user, port=port, connect_kwargs=connect_kwargs
        )

        # Connect to the robot's file system
        self.sftp = self.connection.sftp()

    def download_from_directory(
        self, source_directory: str, target_directory: str, remove: bool
    ):
        try:
            directory_contents = self.sftp.listdir(source_directory)
        except:
            return (
                "Invalid directory provided. Try a format like: '.' or './my_folder'."
            )

        log_files = filter(
            lambda file_name: file_name.endswith(".wpilog"), directory_contents
        )

        for file_name in log_files:
            remote_file_path = PurePosixPath(
                source_directory,
                file_name,
            )

            local_path = Path(target_directory, file_name)

            # Make sure a file exists at the given path
            try:
                local_path.parent.mkdir(parents=True, exist_ok=True)
                local_path.touch(exist_ok=True)
            except:
                return "Could not save file locally in the target location. Try running the shell with administrator privileges."

            self.sftp.get(str(remote_file_path), str(local_path))

            if remove:
                self.sftp.remove(str(remote_file_path))

        return None

    def close_interface(self):
        self.connection.close()
