document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("#form-reclamo");
  const tbody = document.querySelector("#mis-reclamos");
  const detalle = document.querySelector("#detalle");

  if (form) {
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const payload = Object.fromEntries(new FormData(form).entries());
      try {
        const reclamo = await apiJson("/api/reclamos", {
          method: "POST",
          body: JSON.stringify(payload)
        });
        await apiJson("/web/reclamos-vinculados", {
          method: "POST",
          body: JSON.stringify({ reclamoId: reclamo.id })
        });
        form.reset();
        showAlert(`Reclamo ${reclamo.id} registrado correctamente.`);
      } catch (error) {
        showAlert(error.message, "danger");
      }
    });
  }

  if (tbody) {
    loadMisReclamos();
  }

  async function loadMisReclamos() {
    try {
      const data = await apiJson("/web/mis-reclamos");
      const reclamos = await Promise.all(data.items.map((id) => apiJson(`/api/reclamos/${id}`)));
      tbody.innerHTML = reclamos.map((item) => `
        <tr>
          <td>${escapeHtml(item.id)}</td>
          <td>${escapeHtml(item.producto)}</td>
          <td><span class="badge text-bg-light">${escapeHtml(item.estado)}</span></td>
          <td>${escapeHtml(item.fechaCierre)}</td>
          <td><button class="btn btn-outline-primary btn-sm" data-id="${item.id}" type="button">Ver detalle</button></td>
        </tr>
      `).join("") || `<tr><td colspan="5" class="text-center text-secondary">No tienes reclamos registrados.</td></tr>`;
      tbody.querySelectorAll("button[data-id]").forEach((button) => {
        button.addEventListener("click", () => showDetalle(button.dataset.id));
      });
    } catch (error) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-danger">${escapeHtml(error.message)}</td></tr>`;
    }
  }

  async function showDetalle(id) {
    const reclamo = await apiJson(`/api/reclamos/${id}`);
    detalle.innerHTML = detailHtml(reclamo);
    detalle.classList.remove("d-none");
  }
});
