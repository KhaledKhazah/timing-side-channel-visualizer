import sys
import threading

from pathlib import Path

from flask import (
    Flask,
    jsonify,
    send_from_directory
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent
    .parent
)

ATTACK_DIR = (
    BASE_DIR / "attack"
)

DASHBOARD_DIR = (
    BASE_DIR / "dashboard"
)


sys.path.insert(
    0,
    str(ATTACK_DIR)
)

from timing_attack import recover_pin


app = Flask(__name__)


state_lock = threading.Lock()


attack_state = {
    "status": "idle",
    "running": False,
    "completed": False,

    "prefix": "",
    "found_pin": "",

    "current_position": 0,
    "current_guess": "",

    "current_candidates": [],
    "steps": [],

    "error": None
}


def reset_state():

    with state_lock:

        attack_state[
            "status"
        ] = "idle"

        attack_state[
            "running"
        ] = False

        attack_state[
            "completed"
        ] = False

        attack_state[
            "prefix"
        ] = ""

        attack_state[
            "found_pin"
        ] = ""

        attack_state[
            "current_position"
        ] = 0

        attack_state[
            "current_guess"
        ] = ""

        attack_state[
            "current_candidates"
        ] = []

        attack_state[
            "steps"
        ] = []

        attack_state[
            "error"
        ] = None


def progress_callback(event):

    with state_lock:

        event_type = event[
            "type"
        ]

        if event_type == "measurement":

            position = event[
                "position"
            ]

            if (
                attack_state[
                    "current_position"
                ]
                != position
            ):

                attack_state[
                    "current_candidates"
                ] = []

            attack_state[
                "current_position"
            ] = position

            attack_state[
                "current_guess"
            ] = event[
                "guess"
            ]

            attack_state[
                "current_candidates"
            ].append({
                "digit":
                    event["digit"],

                "guess":
                    event["guess"],

                "milliseconds":
                    event["milliseconds"]
            })

        elif event_type == "digit_found":

            step = event[
                "step"
            ]

            attack_state[
                "prefix"
            ] = step[
                "prefix"
            ]

            attack_state[
                "steps"
            ].append(
                step
            )

        elif event_type == "complete":

            attack_state[
                "found_pin"
            ] = event[
                "pin"
            ]

            attack_state[
                "status"
            ] = "completed"

            attack_state[
                "running"
            ] = False

            attack_state[
                "completed"
            ] = True


def attack_worker():

    try:

        recover_pin(
            progress_callback
        )

    except Exception as error:

        with state_lock:

            attack_state[
                "status"
            ] = "error"

            attack_state[
                "running"
            ] = False

            attack_state[
                "error"
            ] = str(error)


@app.route("/")
def dashboard():

    return send_from_directory(
        DASHBOARD_DIR,
        "index.html"
    )


@app.route(
    "/<path:filename>"
)
def dashboard_files(
    filename
):

    return send_from_directory(
        DASHBOARD_DIR,
        filename
    )


@app.route(
    "/api/status",
    methods=["GET"]
)
def get_status():

    with state_lock:

        return jsonify(
            attack_state.copy()
        )


@app.route(
    "/api/start",
    methods=["POST"]
)
def start_attack():

    with state_lock:

        if attack_state[
            "running"
        ]:

            return jsonify({
                "error":
                    "Attack already running"
            }), 409

    reset_state()

    with state_lock:

        attack_state[
            "status"
        ] = "running"

        attack_state[
            "running"
        ] = True

    thread = threading.Thread(
        target=attack_worker,
        daemon=True
    )

    thread.start()

    return jsonify({
        "message":
            "Attack started"
    })


@app.route(
    "/api/reset",
    methods=["POST"]
)
def reset_attack():

    with state_lock:

        if attack_state[
            "running"
        ]:

            return jsonify({
                "error":
                    "Cannot reset while running"
            }), 409

    reset_state()

    return jsonify({
        "message":
            "Attack reset"
    })


if __name__ == "__main__":

    print(
        "Timing Side-Channel Visualizer"
    )

    print(
        "Dashboard: "
        "http://127.0.0.1:8000"
    )

    app.run(
        host="127.0.0.1",
        port=8000,
        debug=False
    )