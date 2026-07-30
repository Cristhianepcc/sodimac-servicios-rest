document.addEventListener("DOMContentLoaded", () => {
  let page = 1;
  const size = 10;
  const tbody = document.querySelector("#reclamos");
  const detalle = document.querySelector("#detalle");
  const label = document.querySelector("#page-label");

  document.querySelector("#prev").addEventListener("click", () => {
    if (page > 1) {
      page -= 1;
      load();
    }
  });
  document.querySelector("#next").addEventListener("click", () => {
    page += 1;
    load();
  });

  load();

  async function load() {
    const data = await apiJson(`/api/reclamos?page=${page}&size=${size}`);
    label.textContent = `${data.page} / ${Math.max(1, Math.ceil(data.total / data.size))}`;
    renderRows(tbody, data.items, showDetalle);
  }

  async function showDetalle(id) {
    const reclamo = await apiJson(`/api/reclamos/${id}`);
    const form = `
      <form id="form-garantia" class="mt-4">
        <h3 class="h6">Validacion de garantia</h3>
        <div class="form-check mb-3">
          <input class="form-check-input" type="checkbox" id="cumpleGarantia" ${reclamo.cumpleGarantia ? "checked" : ""}>
          <label class="form-check-label" for="cumpleGarantia">Cumple Garantia</label>
        </div>
        <label class="form-label" for="motivoValidacion">Motivo Validacion</label>
        <textarea class="form-control" id="motivoValidacion" rows="3" required>${text(reclamo.motivoValidacion) === "-" ? "" : escapeHtml(reclamo.motivoValidacion)}</textarea>
        <button class="btn btn-primary mt-3" type="submit">Guardar</button>
      </form>
    `;
    detalle.innerHTML = detailHtml(reclamo, form);
    detalle.classList.remove("d-none");
    document.querySelector("#form-garantia").addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await apiJson(`/api/reclamos/${id}/garantia`, {
          method: "PATCH",
          body: JSON.stringify({
            cumpleGarantia: document.querySelector("#cumpleGarantia").checked,
            motivoValidacion: document.querySelector("#motivoValidacion").value
          })
        });
        showAlert("Validacion guardada correctamente.");
        await showDetalle(id);
        await load();
      } catch (error) {
        showAlert(error.message, "danger");
      }
    });
  }
});
