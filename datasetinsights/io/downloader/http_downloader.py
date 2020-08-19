import logging
import os
import zipfile

from datasetinsights.io.download import (
    download_file,
    get_checksum_from_file,
    validate_checksum,
)
from datasetinsights.io.downloader.base import DatasetDownloader
from datasetinsights.io.exceptions import ChecksumError

logger = logging.getLogger(__name__)


class HTTPDownloader(DatasetDownloader, protocol="http://"):
    """ This class is used to download data from any HTTP or HTTPS public url
        and perform function such as downloading the dataset and checksum
        validation.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def download(self, source_uri, output, checksum_file=None, **kwargs):
        """ This method is used to download the dataset from HTTP or HTTPS url.

        Args:
            source_uri (str): This is the downloader-uri that indicates where
                              the dataset should be downloaded from.

            output (str): This is the path to the directory where the download
                          will store the dataset.

            checksum_file (str): This is path of the txt file that contains
                                 checksum of the dataset to be downloaded. It
                                 can be HTTP or HTTPS url or local path.

        Raises:
            ChecksumError: This will raise this error if checksum doesn't
                           matches

        """

        dataset_path = os.path.join(output, "dataset.zip")
        download_file(source_uri, dataset_path)

        if checksum_file:
            logger.debug("Reading checksum from checksum file.")
            checksum = get_checksum_from_file(checksum_file)
            try:
                logger.debug("Validating checksum!!")
                validate_checksum(dataset_path, checksum)
            except ChecksumError as e:
                logger.info("Checksum mismatch. Deleting the downloaded file.")
                os.remove(dataset_path)
                raise e

        self.unzip_file(dataset_path, output)

    @staticmethod
    def unzip_file(filepath, destination):
        """Unzips a zip file to the destination and delete the zip file.

        Args:
            filepath (str): File path of the zip file.
            destination (str): Path where to unzip contents of zipped file.
        """
        with zipfile.ZipFile(filepath) as file:
            logger.info(f"Unzipping file: {filepath} to {destination}")
            file.extractall(destination)
