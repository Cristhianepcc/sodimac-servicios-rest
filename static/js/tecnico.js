document.addEventListener("DOMContentLoaded", () => {
  const isSoluciones = Boolean(document.querySelector("#soluciones"));
  const tbody = document.querySelector(isSoluciones ? "#soluciones" : "#evaluaciones");
  const detalle = document.querySelector("#detalle");
  const label = document.querySelector("#page-label");
  let page = 1;
  const size = 10;

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
    const endpoint = isSoluciones ? "/api/soluciones" : "/api/evaluaciones";
    const data = await apiJson(`${endpoint}?page=${page}&size=${size}`);
    label.textContent = `${data.page} / ${Math.max(1, Math.ceil(data.total / data.size))}`;
    renderRows(tbody, data.items, showDetalle);
  }

  async function showDetalle(id) {
    const reclamo = await apiJson(`/api/reclamos/${id}`);
    detalle.innerHTML = detailHtml(reclamo, isSoluciones ? solucionForm(reclamo) : evaluacionForm(reclamo));
    detalle.classList.remove("d-none");
    if (isSoluciones) bindSolucion(id);
    else bindEvaluacion(id);
  }

  function evaluacionForm(reclamo) {
    const evaluacionCompleta = Boolean((reclamo.diagnostico || "").trim());
    const disabled = evaluacionCompleta ? "disabled" : "";
    const badge = evaluacionCompleta ? `<span class="badge text-bg-success">Evaluacion completada</span>` : "";
    const button = evaluacionCompleta ? "" : `<button class="btn btn-primary mt-3" type="submit">Guardar</button>`;
    return `
      <form id="form-evaluacion" class="mt-4">
        <div class="stage-header mb-3">
          <h3 class="h6 mb-0">Evaluacion tecnica</h3>
          ${badge}
        </div>
        <label class="form-label" for="diagnostico">Diagnostico</label>
        <textarea class="form-control mb-3" id="diagnostico" rows="3" required ${disabled}>${text(reclamo.diagnostico) === "-" ? "" : escapeHtml(reclamo.diagnostico)}</textarea>
        <div class="form-check">
          <input class="form-check-input" type="checkbox" id="procede" ${reclamo.procedeEvaluacion ? "checked" : ""} ${disabled}>
          <label class="form-check-label" for="procede">Procede</label>
        </div>
        ${button}
      </form>
    `;
  }

  function solucionForm(reclamo) {
    const casoResuelto = Boolean((reclamo.tipoSolucion || "").trim());
    const disabled = casoResuelto ? "disabled" : "";
    const badge = casoResuelto ? `<span class="badge text-bg-success">Caso resuelto</span>` : "";
    const button = casoResuelto ? "" : `<button class="btn btn-primary mt-3" type="submit">Guardar</button>`;
    return `
      <form id="form-solucion" class="mt-4">
        <div class="stage-header mb-3">
          <h3 class="h6 mb-0">Resolucion del caso</h3>
          ${badge}
        </div>
        <label class="form-label" for="tipoSolucion">Tipo Solucion</label>
        <select class="form-select mb-3" id="tipoSolucion" required ${disabled}>
          ${["REEMBOLSO", "CAMBIO", "REPARACION"].map((tipo) => `<option value="${tipo}" ${reclamo.tipoSolucion === tipo ? "selected" : ""}>${tipo}</option>`).join("")}
        </select>
        <label class="form-label" for="mensajeCliente">Mensaje Cliente</label>
        <textarea class="form-control" id="mensajeCliente" rows="4" required ${disabled}>${text(reclamo.mensajeCliente) === "-" ? "" : escapeHtml(reclamo.mensajeCliente)}</textarea>
        ${button}
      </form>
    `;
  }

  function bindEvaluacion(id) {
    const form = document.querySelector("#form-evaluacion");
    if (!form || !form.querySelector("button[type='submit']")) return;
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await apiJson(`/api/reclamos/${id}/evaluacion`, {
          method: "PATCH",
          body: JSON.stringify({
            diagnostico: document.querySelector("#diagnostico").value,
            procede: document.querySelector("#procede").checked
          })
        });
        showAlert("Evaluacion guardada correctamente.");
        await showDetalle(id);
        await load();
      } catch (error) {
        showAlert(error.message, "danger");
      }
    });
  }

  function bindSolucion(id) {
    const form = document.querySelector("#form-solucion");
    if (!form || !form.querySelector("button[type='submit']")) return;
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      try {
        await apiJson(`/api/reclamos/${id}/solucion`, {
          method: "PATCH",
          body: JSON.stringify({ tipoSolucion: document.querySelector("#tipoSolucion").value })
        });
        await apiJson(`/api/reclamos/${id}/notificacion`, {
          method: "POST",
          body: JSON.stringify({ mensajeCliente: document.querySelector("#mensajeCliente").value })
        });
        showAlert("Solucion registrada y notificacion enviada.");
        await showDetalle(id);
        await load();
      } catch (error) {
        showAlert(error.message, "danger");
      }
    });
  }
});
