from dataclasses import dataclass
from logging import getLogger

import clamd
from fastapi import UploadFile

from app.core.settings import settings

logger = getLogger("uvicorn")


@dataclass
class ScanResults:
    success: bool
    message: str


SCAN_FAILED = "Het is niet gelukt om het bestand te controleren"


def scan_file_for_malware(file: UploadFile):
    # Malicious file examples: https://github.com/fire1ce/eicar-standard-antivirus-test-files
    if settings.DISABLE_SECURITY_CHECK == "1":
        return ScanResults(success=True, message="De malware scan is uitgeschakeld.")

    try:
        cd = clamd.ClamdNetworkSocket()
        cd.__init__(host=settings.CLAMAV_HOST, port=settings.CLAMAV_PORT, timeout=30)
        file.file.seek(0)  # just in case another function didnt move the pointer
        response = cd.instream(file.file)
        file.file.seek(0)
        if response is None:
            return ScanResults(
                success=False,
                message=SCAN_FAILED,
            )

    except TimeoutError as err:
        logger.exception(err)
        return ScanResults(
            success=False,
            message="Het duurde te lang om het bestand te scannen",
        )

    except clamd.ConnectionError as err:
        logger.exception(err)
        return ScanResults(
            success=False,
            message=SCAN_FAILED,
        )

    except clamd.ResponseError as err:
        logger.exception(err)
        return ScanResults(
            success=False,
            message=SCAN_FAILED,
        )

    except Exception as err:
        logger.exception(err)
        return ScanResults(
            success=False,
            message="Onbekende foutmelding bij controleren van het bestand",
        )

    logger.info(response["stream"])
    if response["stream"][0] == "OK":
        return ScanResults(success=True, message="Het bestand bevat geen schadelijke data")
    else:
        logger.warning(f"Malware gevonden {response['stream'][1]}")
        return ScanResults(success=False, message="Het bestand bevat mogelijk schadelijke data")
