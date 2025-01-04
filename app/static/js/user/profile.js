document.addEventListener("DOMContentLoaded", () => {
    const operationsTableBody = document.querySelector("#operations-table tbody");
    const eventFilter = document.querySelector("#event-filter");

    async function fetchOperations(filter = "all") {
        try {
            // Construimos la URL con el filtro
            const url = filter === "all" ? "/user/operations/latest" : `/user/operations/latest?filter=${filter}`;
            
            const response = await fetch(url);
            if (!response.ok) {
                console.error("Error al obtener las operaciones.");
                return;
            }

            const operations = await response.json();
            operationsTableBody.innerHTML = "";

            // Rellenamos la tabla con las últimas 10 operaciones
            operations.slice(0, 10).forEach(operation => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${operation.event_name}</td>
                    <td>${operation.description}</td>
                    <td>${operation.created_at}</td>
                `;
                operationsTableBody.appendChild(row);
            });
        } catch (error) {
            console.error("Error al actualizar las operaciones:", error);
        }
    }

    // Manejador de cambios en el filtro
    eventFilter.addEventListener("change", (event) => {
        const selectedFilter = event.target.value;
        fetchOperations(selectedFilter); // Llamada al servidor con el filtro seleccionado
    });

    // Cargar operaciones iniciales con el filtro predeterminado ("all")
    fetchOperations();

    // Actualizar las operaciones cada 10 segundos
    setInterval(() => {
        const selectedFilter = eventFilter.value;
        fetchOperations(selectedFilter); // Mantener el filtro actual
    }, 10000);
});
