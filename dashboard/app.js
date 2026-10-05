const statusElement =
    document.getElementById(
        "status"
    );

const prefixElement =
    document.getElementById(
        "prefix"
    );

const positionElement =
    document.getElementById(
        "position"
    );

const guessElement =
    document.getElementById(
        "guess"
    );

const candidateContainer =
    document.getElementById(
        "candidate-container"
    );

const stepsContainer =
    document.getElementById(
        "steps-container"
    );

const startButton =
    document.getElementById(
        "start-button"
    );

const resultPanel =
    document.getElementById(
        "result-panel"
    );

const foundPin =
    document.getElementById(
        "found-pin"
    );


async function startAttack() {

    const response =
        await fetch(
            "/api/start",
            {
                method: "POST"
            }
        );

    if (response.ok) {

        startButton.disabled =
            true;
    }
}


async function resetAttack() {

    const response =
        await fetch(
            "/api/reset",
            {
                method: "POST"
            }
        );

    if (response.ok) {

        await updateDashboard();
    }
}


function renderCandidates(
    candidates
) {

    if (
        candidates.length === 0
    ) {

        candidateContainer.innerHTML =
            `
            <p class="empty">
                Waiting for measurements...
            </p>
            `;

        return;
    }


    const maximumTime =
        Math.max(
            ...candidates.map(
                candidate =>
                    candidate.milliseconds
            )
        );


    candidateContainer.innerHTML =
        "";


    candidates
        .slice()
        .sort(
            (
                first,
                second
            ) =>
                second.milliseconds
                - first.milliseconds
        )
        .forEach(
            candidate => {

                const percentage =
                    (
                        candidate.milliseconds
                        / maximumTime
                    ) * 100;


                const row =
                    document.createElement(
                        "div"
                    );


                row.className =
                    "candidate";


                row.innerHTML = `

                    <span class="digit">
                        ${candidate.digit}
                    </span>

                    <span class="guess">
                        ${candidate.guess}
                    </span>

                    <div
                        class="bar-background"
                    >
                        <div
                            class="bar"
                            style="
                                width:
                                ${percentage}%;
                            "
                        ></div>
                    </div>

                    <span class="timing">
                        ${candidate.milliseconds}
                        ms
                    </span>
                `;


                candidateContainer
                    .appendChild(
                        row
                    );
            }
        );
}


function renderSteps(
    steps
) {

    if (
        steps.length === 0
    ) {

        stepsContainer.innerHTML =
            `
            <p class="empty">
                No digits recovered yet.
            </p>
            `;

        return;
    }


    stepsContainer.innerHTML =
        "";


    steps.forEach(
        step => {

            const row =
                document.createElement(
                    "div"
                );


            row.className =
                "step";


            row.innerHTML = `

                <span>
                    Position
                    ${step.position}
                </span>

                <strong>
                    ${step.prefix}
                </strong>

            `;


            stepsContainer
                .appendChild(
                    row
                );
        }
    );
}


async function updateDashboard() {

    try {

        const response =
            await fetch(
                "/api/status"
            );


        const data =
            await response.json();


        statusElement.textContent =
            data.status.toUpperCase();


        prefixElement.textContent =
            data.prefix.length > 0
                ? data.prefix
                : "????";


        positionElement.textContent =
            data.current_position > 0
                ? data.current_position
                : "-";


        guessElement.textContent =
            data.current_guess || "----";


        startButton.disabled =
            data.running;


        renderCandidates(
            data.current_candidates
        );


        renderSteps(
            data.steps
        );


        if (
            data.completed
        ) {

            resultPanel.classList
                .remove(
                    "hidden"
                );


            foundPin.textContent =
                data.found_pin;

        }

        else {

            resultPanel.classList
                .add(
                    "hidden"
                );
        }

    }

    catch (error) {

        statusElement.textContent =
            "OFFLINE";
    }
}


updateDashboard();


setInterval(
    updateDashboard,
    500
);