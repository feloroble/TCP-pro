document.addEventListener("DOMContentLoaded", () => {
    const operationsTableBody = document.querySelector("#operations-table tbody");

    async function fetchOperations() {
        try {
            const response = await fetch("/user/operations/latest");
            if (!response.ok) {
                console.error("Error al obtener las operaciones.");
                return;
            }

            const operations = await response.json();
            operationsTableBody.innerHTML = "";

            operations.forEach(operation => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${operation.event_type}</td>
                    <td>${operation.description}</td>
                    <td>${operation.created_at}</td>
                `;
                operationsTableBody.appendChild(row);
            });
        } catch (error) {
            console.error("Error al actualizar las operaciones:", error);
        }
    }

    // Actualizar las operaciones cada 10 segundos
    fetchOperations();
    setInterval(fetchOperations, 10000);
});
