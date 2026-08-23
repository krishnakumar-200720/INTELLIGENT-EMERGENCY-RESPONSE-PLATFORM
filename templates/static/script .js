// --------------------------------------------------
// Submit Emergency
// --------------------------------------------------

document
    .getElementById("emergencyForm")
    .addEventListener("submit", async function(event) {

        event.preventDefault();

        const data = {

            name:
                document.getElementById("name").value,

            phone:
                document.getElementById("phone").value,

            emergency_type:
                document.getElementById(
                    "emergency_type"
                ).value,

            location:
                document.getElementById(
                    "location"
                ).value,

            description:
                document.getElementById(
                    "description"
                ).value
        };


        try {

            const response = await fetch(
                "/api/emergency",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify(data)
                }
            );


            const result =
                await response.json();


            const message =
                document.getElementById(
                    "responseMessage"
                );


            message.style.display = "block";


            if (result.success) {

                message.style.background =
                    "#dcfce7";

                message.style.color =
                    "#166534";

                message.innerHTML =
                    `
                    <strong>
                    🚨 Emergency Alert Received
                    </strong>
                    <br>
                    Emergency ID:
                    ${result.emergency_id}
                    <br>
                    Priority:
                    <strong>
                    ${result.priority}
                    </strong>
                    `;


                document
                    .getElementById(
                        "emergencyForm"
                    )
                    .reset();


                loadEmergencies();

                loadStatistics();

            } else {

                message.style.background =
                    "#fee2e2";

                message.style.color =
                    "#991b1b";

                message.innerText =
                    result.message;
            }


        } catch (error) {

            console.error(error);

            alert(
                "Unable to connect to server."
            );
        }

    });


// --------------------------------------------------
// Load Emergencies
// --------------------------------------------------

async function loadEmergencies() {

    try {

        const response =
            await fetch(
                "/api/emergencies"
            );

        const emergencies =
            await response.json();


        const table =
            document.getElementById(
                "emergencyTable"
            );


        table.innerHTML = "";


        emergencies.forEach(
            emergency => {

                let priorityClass =
                    emergency.priority.toLowerCase();


                const row =
                    document.createElement("tr");


                row.innerHTML = `

                    <td>
                        ${emergency.id}
                    </td>

                    <td>
                        ${emergency.name}
                    </td>

                    <td>
                        ${emergency.emergency_type}
                    </td>

                    <td>
                        ${emergency.location}
                    </td>

                    <td>
                        <span
                            class="priority-badge ${priorityClass}">
                            ${emergency.priority}
                        </span>
                    </td>

                    <td>
                        ${emergency.status}
                    </td>

                    <td>
                        ${emergency.created_at}
                    </td>

                    <td>

                        <button
                            class="status-button"
                            onclick="updateStatus(
                                ${emergency.id}
                            )">

                            Update

                        </button>

                    </td>
                `;


                table.appendChild(row);

            }
        );


    } catch (error) {

        console.error(
            "Error loading emergencies:",
            error
        );
    }
}


// --------------------------------------------------
// Update Status
// --------------------------------------------------

async function updateStatus(id) {

    const status =
        prompt(
            "Enter status:\n\n" +
            "Pending\n" +
            "Dispatched\n" +
            "In Progress\n" +
            "Resolved"
        );


    if (!status) {
        return;
    }


    try {

        const response =
            await fetch(
                `/api/emergency/${id}`,
                {
                    method: "PUT",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        status: status
                    })
                }
            );


        const result =
            await response.json();


        if (result.success) {

            alert(
                "Emergency status updated."
            );

            loadEmergencies();

            loadStatistics();

        } else {

            alert(
                result.message
            );
        }


    } catch (error) {

        console.error(error);

        alert(
            "Unable to update status."
        );
    }
}


// --------------------------------------------------
// Load Dashboard Statistics
// --------------------------------------------------

async function loadStatistics() {

    try {

        const response =
            await fetch(
                "/api/statistics"
            );


        const stats =
            await response.json();


        document.getElementById(
            "totalEmergencies"
        ).innerText = stats.total;


        document.getElementById(
            "pendingEmergencies"
        ).innerText = stats.pending;


        document.getElementById(
            "dispatchedEmergencies"
        ).innerText = stats.dispatched;


        document.getElementById(
            "criticalEmergencies"
        ).innerText = stats.critical;


    } catch (error) {

        console.error(
            "Statistics error:",
            error
        );
    }
}


// --------------------------------------------------
// Initial Loading
// --------------------------------------------------

window.addEventListener(
    "DOMContentLoaded",
    function() {

        loadEmergencies();

        loadStatistics();

    }
);
