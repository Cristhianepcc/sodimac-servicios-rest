async function apiJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.error || data.mensaje || "No se pudo completar la operacion.");
  }
  return data;
}

function text(value) {
  return value === null || value === undefined || value === "" ? "-" : String(value);
}

function escapeHtml(value) {
  return text(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function boolText(value) {
  if (value === true) return "Si";
  if (value === false) return "No";
  return "-";
}

function showAlert(message, type = "success") {
  const el = document.querySelector("#alerta");
  if (!el) return;
  el.className = `alert alert-${type}`;
  el.textContent = message;
}

function detailHtml(reclamo, extra = "") {
  const fields = [
    ["ID", reclamo.id],
    ["Cliente", reclamo.cliente],
    ["DNI", reclamo.dni],
    ["Email", reclamo.email],
    ["Telefono", reclamo.telefono],
    ["Producto", reclamo.producto],
    ["Motivo", reclamo.motivo],
    ["Estado", reclamo.estado],
    ["Cumple Garantia", boolText(reclamo.cumpleGarantia)],
    ["Motivo Validacion", reclamo.motivoValidacion],
    ["Diagnostico", reclamo.diagnostico],
    ["Procede Evaluacion", boolText(reclamo.procedeEvaluacion)],
    ["Tipo Solucion", reclamo.tipoSolucion],
    ["Fecha cierre", reclamo.fechaCierre],
    ["Fecha notificacion", reclamo.fechaNotificacion]
  ];
  const response = reclamo.mensajeCliente
    ? `<div class="respuesta-cliente"><h2>Respuesta de Sodimac</h2><p class="mb-0">${escapeHtml(reclamo.mensajeCliente)}</p></div>`
    : "";
  return `
    <h2 class="h5 mb-3">Detalle del Reclamo</h2>
    <div class="detail-grid">
      ${fields.map(([label, value]) => `<div class="detail-item"><span>${label}</span>${escapeHtml(value)}</div>`).join("")}
    </div>
    ${response}
    ${extra}
  `;
}

function renderRows(tbody, items, onClick) {
  tbody.innerHTML = items.map((item) => `
    <tr data-id="${item.id}">
      <td>${escapeHtml(item.id)}</td>
      <td>${escapeHtml(item.cliente)}</td>
      <td>${escapeHtml(item.producto)}</td>
      <td><span class="badge text-bg-light">${escapeHtml(item.estado)}</span></td>
    </tr>
  `).join("");
  tbody.querySelectorAll("tr").forEach((row) => row.addEventListener("click", () => onClick(row.dataset.id)));
}
