document.addEventListener("DOMContentLoaded", () => {
  const path = window.location.pathname;
  if (path.includes("/proveedores")) initProveedores();
  else if (path.includes("/ordenes-compra")) initOrdenesCompra();
  else if (path.includes("/recepciones")) initRecepciones();
  else if (path.includes("/distribucion")) initDistribucion();
  else if (path.includes("/almacen")) initAlmacen();
  else if (path.includes("/auditorias")) initAuditorias();
});

function initProveedores() {
  const tbody = document.querySelector("#proveedores");
  const detalle = document.querySelector("#detalle");

  load();

  document.querySelector("#btn-nuevo").addEventListener("click", () => {
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Registrar Proveedor</h2>
      <form id="form-proveedor" class="form-card">
        <div class="row g-3">
          <div class="col-md-6"><label class="form-label">Nombre</label><input class="form-control" id="nombre" required></div>
          <div class="col-md-6"><label class="form-label">RUC</label><input class="form-control" id="ruc" required></div>
        </div>
        <button class="btn btn-primary mt-3" type="submit">Registrar</button>
      </form>`;
    detalle.classList.remove("d-none");
    document.querySelector("#form-proveedor").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await apiJson("/api/proveedores", { method: "POST", body: JSON.stringify({ nombre: document.querySelector("#nombre").value, ruc: document.querySelector("#ruc").value }) });
        showAlert("Proveedor registrado.");
        detalle.classList.add("d-none");
        load();
      } catch (err) { showAlert(err.message, "danger"); }
    });
  });

  async function load() {
    const items = await apiJson("/api/proveedores");
    tbody.innerHTML = items.map(p => `
      <tr>
        <td>${escapeHtml(p.id)}</td>
        <td>${escapeHtml(p.nombre)}</td>
        <td>${escapeHtml(p.ruc)}</td>
        <td>${p.puntaje}</td>
        <td><span class="badge text-bg-light">${escapeHtml(p.estado)}</span></td>
        <td><button class="btn btn-outline-primary btn-sm" data-id="${p.id}">Ver</button></td>
      </tr>`).join("") || `<tr><td colspan="6" class="text-center text-secondary">No hay proveedores.</td></tr>`;
    tbody.querySelectorAll("button[data-id]").forEach(b => b.addEventListener("click", () => showDetalle(b.dataset.id)));
  }

  async function showDetalle(id) {
    const p = await apiJson(`/api/proveedores/${id}`);
    const evaluarForm = ["REGISTRADO", "EVALUADO", "RECHAZADO"].includes(p.estado) ? `
      <form id="form-evaluar" class="mt-3">
        <div class="row g-3 align-items-end">
          <div class="col-md-3"><label class="form-label">Puntaje</label><input class="form-control" type="number" id="puntaje" min="0" max="100" value="${p.puntaje || ""}" required></div>
          <div class="col-md-3"><button class="btn btn-outline-primary btn-sm" type="submit">Guardar Puntaje</button></div>
        </div>
      </form>` : "";
    const accionForm = p.estado === "EVALUADO" ? `
      <div class="mt-3">
        <button class="btn btn-success btn-sm" id="btn-aprobar">Aprobar</button>
        <button class="btn btn-danger btn-sm" id="btn-rechazar">Rechazar</button>
      </div>` : p.estado === "RECHAZADO" ? `
      <div class="mt-3">
        <button class="btn btn-success btn-sm" id="btn-aprobar">Aprobar</button>
      </div>` : "";
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Detalle del Proveedor</h2>
      <div class="detail-grid">
        <div class="detail-item"><span>ID</span>${escapeHtml(p.id)}</div>
        <div class="detail-item"><span>Nombre</span>${escapeHtml(p.nombre)}</div>
        <div class="detail-item"><span>RUC</span>${escapeHtml(p.ruc)}</div>
        <div class="detail-item"><span>Puntaje</span>${p.puntaje}</div>
        <div class="detail-item"><span>Estado</span>${escapeHtml(p.estado)}</div>
      </div>
      ${evaluarForm}${accionForm}`;
    detalle.classList.remove("d-none");
    if (document.querySelector("#form-evaluar")) {
      document.querySelector("#form-evaluar").addEventListener("submit", async (e) => {
        e.preventDefault();
        try {
          await apiJson(`/api/proveedores/${id}/evaluar`, { method: "POST", body: JSON.stringify({ puntaje: parseInt(document.querySelector("#puntaje").value) }) });
          showAlert("Proveedor evaluado.");
          load(); showDetalle(id);
        } catch (err) { showAlert(err.message, "danger"); }
      });
    }
    if (document.querySelector("#btn-aprobar")) {
      document.querySelector("#btn-aprobar").addEventListener("click", async () => {
        try {
          await apiJson(`/api/proveedores/${id}/aprobar`, { method: "PUT" });
          showAlert("Proveedor aprobado.");
          load(); showDetalle(id);
        } catch (err) { showAlert(err.message, "danger"); }
      });
    }
    if (document.querySelector("#btn-rechazar")) {
      document.querySelector("#btn-rechazar").addEventListener("click", async () => {
        try {
          await apiJson(`/api/proveedores/${id}/rechazar`, { method: "PUT" });
          showAlert("Proveedor rechazado.");
          load(); showDetalle(id);
        } catch (err) { showAlert(err.message, "danger"); }
      });
    }
  }
}

function initOrdenesCompra() {
  const tbody = document.querySelector("#ordenes");
  const detalle = document.querySelector("#detalle");

  load();

  document.querySelector("#btn-nueva").addEventListener("click", () => {
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Generar Orden de Compra</h2>
      <form id="form-oc" class="form-card">
        <div class="row g-3">
          <div class="col-md-6"><label class="form-label">Proveedor ID</label><input class="form-control" id="proveedorId" required></div>
          <div class="col-md-3"><label class="form-label">SKU</label><input class="form-control" id="sku" required></div>
          <div class="col-md-3"><label class="form-label">Cantidad</label><input class="form-control" type="number" id="cantidad" min="1" required></div>
          <div class="col-md-3"><label class="form-label">Precio Unitario</label><input class="form-control" type="number" id="precio" min="0.01" step="0.01" required></div>
        </div>
        <button class="btn btn-primary mt-3" type="submit">Generar</button>
      </form>`;
    detalle.classList.remove("d-none");
    document.querySelector("#form-oc").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await apiJson("/api/ordenes-compra", { method: "POST", body: JSON.stringify({
          proveedorId: document.querySelector("#proveedorId").value,
          lineas: [{ sku: document.querySelector("#sku").value, cantidad: parseInt(document.querySelector("#cantidad").value), precioUnitario: parseFloat(document.querySelector("#precio").value) }]
        }) });
        showAlert("Orden generada.");
        detalle.classList.add("d-none");
        load();
      } catch (err) { showAlert(err.message, "danger"); }
    });
  });

  async function load() {
    const items = await apiJson("/api/ordenes-compra");
    tbody.innerHTML = items.map(o => `
      <tr>
        <td>${escapeHtml(o.id)}</td>
        <td>${escapeHtml(o.proveedorId)}</td>
        <td>${escapeHtml(o.fechaEmision)}</td>
        <td><span class="badge text-bg-light">${escapeHtml(o.estado)}</span></td>
        <td>S/ ${o.total.toFixed(2)}</td>
        <td><button class="btn btn-outline-primary btn-sm" data-id="${o.id}">Ver</button></td>
      </tr>`).join("") || `<tr><td colspan="6" class="text-center text-secondary">No hay ordenes.</td></tr>`;
    tbody.querySelectorAll("button[data-id]").forEach(b => b.addEventListener("click", () => showDetalle(b.dataset.id)));
  }

  async function showDetalle(id) {
    const o = await apiJson(`/api/ordenes-compra/${id}`);
    let accionForm = "";
    if (o.estado === "PENDIENTE_AUTORIZACION") accionForm = `<button class="btn btn-success btn-sm" id="btn-autorizar">Autorizar</button> `;
    if (o.estado === "AUTORIZADA") accionForm += `<button class="btn btn-primary btn-sm" id="btn-enviar">Enviar</button> `;
    if (!["ENVIADA", "CANCELADA"].includes(o.estado)) accionForm += `<button class="btn btn-danger btn-sm" id="btn-cancelar">Cancelar</button>`;
    const lineas = o.lineas.map(l => `<tr><td>${escapeHtml(l.sku)}</td><td>${l.cantidad}</td><td>S/ ${l.precioUnitario.toFixed(2)}</td><td>S/ ${l.subtotal.toFixed(2)}</td></tr>`).join("");
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Detalle Orden ${escapeHtml(o.id)}</h2>
      <div class="detail-grid mb-3">
        <div class="detail-item"><span>Proveedor</span>${escapeHtml(o.proveedorId)}</div>
        <div class="detail-item"><span>Estado</span>${escapeHtml(o.estado)}</div>
        <div class="detail-item"><span>Total</span>S/ ${o.total.toFixed(2)}</div>
      </div>
      <table class="table table-sm"><thead><tr><th>SKU</th><th>Cant.</th><th>Precio</th><th>Subtotal</th></tr></thead><tbody>${lineas}</tbody></table>
      <div class="mt-3">${accionForm}</div>`;
    detalle.classList.remove("d-none");
    if (document.querySelector("#btn-autorizar")) document.querySelector("#btn-autorizar").addEventListener("click", async () => { await apiJson(`/api/ordenes-compra/${id}/autorizar`, { method: "PUT" }); showAlert("Orden autorizada."); load(); showDetalle(id); });
    if (document.querySelector("#btn-enviar")) document.querySelector("#btn-enviar").addEventListener("click", async () => { await apiJson(`/api/ordenes-compra/${id}/enviar`, { method: "POST" }); showAlert("Orden enviada."); load(); showDetalle(id); });
    if (document.querySelector("#btn-cancelar")) document.querySelector("#btn-cancelar").addEventListener("click", async () => { await apiJson(`/api/ordenes-compra/${id}`, { method: "DELETE" }); showAlert("Orden cancelada."); load(); showDetalle(id); });
  }
}

function initRecepciones() {
  const tbody = document.querySelector("#recepciones");
  const tbodyOC = document.querySelector("#ordenes-disponibles");
  const detalle = document.querySelector("#detalle");

  loadOrdenes();
  load();

  document.querySelector("#btn-nueva").addEventListener("click", () => {
    loadOrdenes();
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Registrar Recepcion</h2>
      <form id="form-rec" class="form-card">
        <div class="row g-3">
          <div class="col-md-4"><label class="form-label">Orden Compra ID</label><select class="form-select" id="ordenCompraId" required><option value="">Seleccionar orden...</option></select></div>
          <div class="col-md-3"><label class="form-label">SKU</label><input class="form-control" id="sku" required></div>
          <div class="col-md-3"><label class="form-label">Cantidad Recibida</label><input class="form-control" type="number" id="cantidad" min="1" required></div>
        </div>
        <button class="btn btn-primary mt-3" type="submit">Registrar</button>
      </form>`;
    detalle.classList.remove("d-none");
    apiJson("/api/ordenes-compra").then(ordenes => {
      const select = document.querySelector("#ordenCompraId");
      ordenes.filter(o => o.estado === "ENVIADA").forEach(o => {
        const opt = document.createElement("option");
        opt.value = o.id;
        opt.textContent = `${o.id} - ${o.proveedorId} - S/ ${o.total.toFixed(2)}`;
        select.appendChild(opt);
      });
    });
    document.querySelector("#form-rec").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await apiJson("/api/recepciones", { method: "POST", body: JSON.stringify({
          ordenCompraId: document.querySelector("#ordenCompraId").value,
          items: [{ sku: document.querySelector("#sku").value, cantidadRecibida: parseInt(document.querySelector("#cantidad").value) }]
        }) });
        showAlert("Recepcion registrada.");
        detalle.classList.add("d-none");
        load();
      } catch (err) { showAlert(err.message, "danger"); }
    });
  });

  async function loadOrdenes() {
    const ordenes = await apiJson("/api/ordenes-compra");
    const enviadas = ordenes.filter(o => o.estado === "ENVIADA");
    tbodyOC.innerHTML = enviadas.map(o => `
      <tr>
        <td>${escapeHtml(o.id)}</td>
        <td>${escapeHtml(o.proveedorId)}</td>
        <td><span class="badge text-bg-light">${escapeHtml(o.estado)}</span></td>
        <td>S/ ${o.total.toFixed(2)}</td>
        <td><button class="btn btn-outline-primary btn-sm btn-recepcionar" data-id="${o.id}">Recepcionar</button></td>
      </tr>`).join("") || `<tr><td colspan="5" class="text-center text-secondary">No hay ordenes enviadas para recepcionar.</td></tr>`;
    tbodyOC.querySelectorAll(".btn-recepcionar").forEach(b => b.addEventListener("click", () => {
      document.querySelector("#btn-nueva").click();
      setTimeout(() => { document.querySelector("#ordenCompraId").value = b.dataset.id; }, 200);
    }));
  }

  async function load() {
    const items = await apiJson("/api/recepciones");
    tbody.innerHTML = items.map(r => `
      <tr>
        <td>${escapeHtml(r.id)}</td>
        <td>${escapeHtml(r.ordenCompraId)}</td>
        <td>${escapeHtml(r.fechaLlegada)}</td>
        <td><span class="badge text-bg-light">${escapeHtml(r.estado)}</span></td>
        <td><button class="btn btn-outline-primary btn-sm" data-id="${r.id}">Ver</button></td>
      </tr>`).join("") || `<tr><td colspan="5" class="text-center text-secondary">No hay recepciones.</td></tr>`;
    tbody.querySelectorAll("button[data-id]").forEach(b => b.addEventListener("click", () => showDetalle(b.dataset.id)));
  }

  async function showDetalle(id) {
    const r = await apiJson(`/api/recepciones/${id}`);
    const items = r.items.map(i => `<tr><td>${escapeHtml(i.sku)}</td><td>${i.cantidadRecibida}</td></tr>`).join("");
    let accionForm = "";
    if (r.estado === "PENDIENTE") accionForm = `<button class="btn btn-success btn-sm" id="btn-confirmar">Confirmar</button> <button class="btn btn-outline-primary btn-sm" id="btn-inspeccionar">Inspeccionar</button>`;
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Detalle Recepcion ${escapeHtml(r.id)}</h2>
      <div class="detail-grid mb-3">
        <div class="detail-item"><span>Orden Compra</span>${escapeHtml(r.ordenCompraId)}</div>
        <div class="detail-item"><span>Estado</span>${escapeHtml(r.estado)}</div>
        <div class="detail-item"><span>Fecha</span>${escapeHtml(r.fechaLlegada)}</div>
      </div>
      <table class="table table-sm"><thead><tr><th>SKU</th><th>Cant. Recibida</th></tr></thead><tbody>${items}</tbody></table>
      <div class="mt-3">${accionForm}</div>`;
    detalle.classList.remove("d-none");
    if (document.querySelector("#btn-confirmar")) document.querySelector("#btn-confirmar").addEventListener("click", async () => { await apiJson(`/api/recepciones/${id}/confirmar`, { method: "PUT" }); showAlert("Recepcion confirmada."); load(); showDetalle(id); });
    if (document.querySelector("#btn-inspeccionar")) document.querySelector("#btn-inspeccionar").addEventListener("click", async () => { await apiJson("/api/inspecciones", { method: "POST", body: JSON.stringify({ recepcionId: id }) }); showAlert("Inspeccion creada."); load(); });
  }
}

function initDistribucion() {
  const tbody = document.querySelector("#pedidos");
  const detalle = document.querySelector("#detalle");

  load();

  document.querySelector("#btn-nuevo").addEventListener("click", () => {
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Generar Pedido</h2>
      <form id="form-pedido" class="form-card">
        <div class="row g-3">
          <div class="col-md-4"><label class="form-label">Tienda Destino</label><input class="form-control" id="tiendaDestino" required></div>
          <div class="col-md-3"><label class="form-label">SKU</label><input class="form-control" id="sku" required></div>
          <div class="col-md-3"><label class="form-label">Cantidad</label><input class="form-control" type="number" id="cantidad" min="1" required></div>
        </div>
        <button class="btn btn-primary mt-3" type="submit">Generar</button>
      </form>`;
    detalle.classList.remove("d-none");
    document.querySelector("#form-pedido").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await apiJson("/api/distribucion/pedidos", { method: "POST", body: JSON.stringify({
          tiendaDestino: document.querySelector("#tiendaDestino").value,
          items: [{ sku: document.querySelector("#sku").value, cantidad: parseInt(document.querySelector("#cantidad").value) }]
        }) });
        showAlert("Pedido generado.");
        detalle.classList.add("d-none");
        load();
      } catch (err) { showAlert(err.message, "danger"); }
    });
  });

  async function load() {
    const items = await apiJson("/api/distribucion/pedidos");
    tbody.innerHTML = items.map(p => `
      <tr>
        <td>${escapeHtml(p.id)}</td>
        <td>${escapeHtml(p.tiendaDestino)}</td>
        <td>${escapeHtml(p.fechaSolicitud)}</td>
        <td><span class="badge text-bg-light">${escapeHtml(p.estado)}</span></td>
        <td><button class="btn btn-outline-primary btn-sm" data-id="${p.id}">Ver</button></td>
      </tr>`).join("") || `<tr><td colspan="5" class="text-center text-secondary">No hay pedidos.</td></tr>`;
    tbody.querySelectorAll("button[data-id]").forEach(b => b.addEventListener("click", () => showDetalle(b.dataset.id)));
  }

  async function showDetalle(id) {
    const p = await apiJson(`/api/distribucion/pedidos/${id}`);
    const items = p.items.map(i => `<tr><td>${escapeHtml(i.sku)}</td><td>${i.cantidad}</td></tr>`).join("");
    let accionForm = "";
    if (p.estado === "SOLICITADO") accionForm = `<button class="btn btn-primary btn-sm" id="btn-picking">Iniciar Picking</button> `;
    if (p.estado === "EN_PICKING") accionForm = `<button class="btn btn-primary btn-sm" id="btn-packing">Completar Packing</button> `;
    if (p.estado === "EN_PACKING") accionForm = `<button class="btn btn-success btn-sm" id="btn-despachar">Despachar</button>`;
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Detalle Pedido ${escapeHtml(p.id)}</h2>
      <div class="detail-grid mb-3">
        <div class="detail-item"><span>Tienda</span>${escapeHtml(p.tiendaDestino)}</div>
        <div class="detail-item"><span>Estado</span>${escapeHtml(p.estado)}</div>
      </div>
      <table class="table table-sm"><thead><tr><th>SKU</th><th>Cantidad</th></tr></thead><tbody>${items}</tbody></table>
      <div class="mt-3">${accionForm}</div>`;
    detalle.classList.remove("d-none");
    if (document.querySelector("#btn-picking")) document.querySelector("#btn-picking").addEventListener("click", async () => { await apiJson("/api/distribucion/picking", { method: "POST", body: JSON.stringify({ pedidoId: id }) }); showAlert("Picking iniciado."); load(); showDetalle(id); });
    if (document.querySelector("#btn-packing")) document.querySelector("#btn-packing").addEventListener("click", async () => { await apiJson("/api/distribucion/packing", { method: "POST", body: JSON.stringify({ pedidoId: id }) }); showAlert("Packing completado."); load(); showDetalle(id); });
    if (document.querySelector("#btn-despachar")) {
      const transportista = prompt("Transportista:");
      if (transportista) {
        document.querySelector("#btn-despachar").addEventListener("click", async () => { await apiJson("/api/distribucion/despachos", { method: "POST", body: JSON.stringify({ pedidoId: id, transportista }) }); showAlert("Despacho programado."); load(); showDetalle(id); });
      }
    }
  }
}

function initAlmacen() {
  const tbodyUbic = document.querySelector("#ubicaciones");
  const tbodyMerc = document.querySelector("#mercaderia");
  const detalle = document.querySelector("#detalle");

  loadUbicaciones();
  loadMercaderia();

  document.querySelector("#btn-ubicaciones").addEventListener("click", () => {
    document.querySelector("#vista-ubicaciones").classList.remove("d-none");
    document.querySelector("#vista-mercaderia").classList.add("d-none");
  });
  document.querySelector("#btn-mercaderia").addEventListener("click", () => {
    document.querySelector("#vista-ubicaciones").classList.add("d-none");
    document.querySelector("#vista-mercaderia").classList.remove("d-none");
  });

  document.querySelector("#btn-nueva-ubicacion").addEventListener("click", () => {
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Registrar Ubicacion</h2>
      <form id="form-ubic" class="form-card">
        <div class="row g-3">
          <div class="col-md-3"><label class="form-label">Codigo</label><input class="form-control" id="codigo" required></div>
          <div class="col-md-3"><label class="form-label">Pasillo</label><input class="form-control" id="pasillo" required></div>
          <div class="col-md-3"><label class="form-label">Estante</label><input class="form-control" id="estante" required></div>
          <div class="col-md-3"><label class="form-label">Nivel</label><input class="form-control" id="nivel" required></div>
        </div>
        <button class="btn btn-primary mt-3" type="submit">Registrar</button>
      </form>`;
    detalle.classList.remove("d-none");
    document.querySelector("#form-ubic").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await apiJson("/api/almacenes/ubicaciones", { method: "POST", body: JSON.stringify({
          codigo: document.querySelector("#codigo").value, pasillo: document.querySelector("#pasillo").value,
          estante: document.querySelector("#estante").value, nivel: document.querySelector("#nivel").value
        }) });
        showAlert("Ubicacion registrada.");
        detalle.classList.add("d-none");
        loadUbicaciones();
      } catch (err) { showAlert(err.message, "danger"); }
    });
  });

  document.querySelector("#btn-nueva-mercaderia").addEventListener("click", () => {
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Ubicar Mercaderia</h2>
      <form id="form-merc" class="form-card">
        <div class="row g-3">
          <div class="col-md-4"><label class="form-label">SKU</label><input class="form-control" id="sku" required></div>
          <div class="col-md-4"><label class="form-label">Ubicacion Codigo</label><input class="form-control" id="ubicacionCodigo" required></div>
          <div class="col-md-4"><label class="form-label">Cantidad</label><input class="form-control" type="number" id="cantidad" min="1" required></div>
        </div>
        <button class="btn btn-primary mt-3" type="submit">Ubicar</button>
      </form>`;
    detalle.classList.remove("d-none");
    document.querySelector("#form-merc").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await apiJson("/api/almacenes/mercaderia", { method: "POST", body: JSON.stringify({
          sku: document.querySelector("#sku").value, ubicacionCodigo: document.querySelector("#ubicacionCodigo").value,
          cantidad: parseInt(document.querySelector("#cantidad").value)
        }) });
        showAlert("Mercaderia ubicada.");
        detalle.classList.add("d-none");
        loadMercaderia();
      } catch (err) { showAlert(err.message, "danger"); }
    });
  });

  document.querySelector("#btn-buscar-sku").addEventListener("click", async () => {
    const sku = document.querySelector("#buscar-sku").value.trim();
    if (!sku) return;
    const items = await apiJson(`/api/almacenes/mercaderia/${sku}`);
    renderMercaderia(items);
  });

  async function loadUbicaciones() {
    const items = await apiJson("/api/almacenes/ubicaciones");
    tbodyUbic.innerHTML = items.map(u => `
      <tr><td>${escapeHtml(u.codigo)}</td><td>${escapeHtml(u.pasillo)}</td><td>${escapeHtml(u.estante)}</td><td>${escapeHtml(u.nivel)}</td></tr>
    `).join("") || `<tr><td colspan="4" class="text-center text-secondary">No hay ubicaciones.</td></tr>`;
  }

  async function loadMercaderia() {
    const items = await apiJson("/api/almacenes/mercaderia");
    renderMercaderia(items);
  }

  function renderMercaderia(items) {
    tbodyMerc.innerHTML = items.map(m => `
      <tr><td>${escapeHtml(m.id)}</td><td>${escapeHtml(m.sku)}</td><td>${escapeHtml(m.ubicacionCodigo)}</td><td>${m.cantidad}</td><td>${escapeHtml(m.fechaUbicacion)}</td></tr>
    `).join("") || `<tr><td colspan="5" class="text-center text-secondary">No hay mercaderia.</td></tr>`;
  }
}

function initAuditorias() {
  const tbodyAud = document.querySelector("#auditorias");
  const tbodyMov = document.querySelector("#movimientos");
  const detalle = document.querySelector("#detalle");

  loadAuditorias();
  loadMovimientos();

  document.querySelector("#btn-ver-auditorias").addEventListener("click", () => {
    document.querySelector("#vista-auditorias").classList.remove("d-none");
    document.querySelector("#vista-movimientos").classList.add("d-none");
  });
  document.querySelector("#btn-ver-movimientos").addEventListener("click", () => {
    document.querySelector("#vista-auditorias").classList.add("d-none");
    document.querySelector("#vista-movimientos").classList.remove("d-none");
  });

  document.querySelector("#btn-nueva-auditoria").addEventListener("click", () => {
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Crear Auditoria</h2>
      <form id="form-aud" class="form-card">
        <div class="row g-3">
          <div class="col-md-6"><label class="form-label">SKU</label><input class="form-control" id="sku" required></div>
          <div class="col-md-6"><label class="form-label">Tipo</label><select class="form-select" id="tipo"><option value="FISICA">Fisica</option><option value="CONTABLE">Contable</option></select></div>
        </div>
        <button class="btn btn-primary mt-3" type="submit">Crear</button>
      </form>`;
    detalle.classList.remove("d-none");
    document.querySelector("#form-aud").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await apiJson("/api/auditorias", { method: "POST", body: JSON.stringify({ sku: document.querySelector("#sku").value, tipo: document.querySelector("#tipo").value }) });
        showAlert("Auditoria creada.");
        detalle.classList.add("d-none");
        loadAuditorias();
      } catch (err) { showAlert(err.message, "danger"); }
    });
  });

  document.querySelector("#btn-nuevo-movimiento").addEventListener("click", () => {
    detalle.innerHTML = `
      <h2 class="h5 mb-3">Registrar Movimiento</h2>
      <form id="form-mov" class="form-card">
        <div class="row g-3">
          <div class="col-md-3"><label class="form-label">SKU</label><input class="form-control" id="sku" required></div>
          <div class="col-md-3"><label class="form-label">Tipo</label><select class="form-select" id="tipo"><option value="ENTRADA">Entrada</option><option value="SALIDA">Salida</option><option value="AJUSTE">Ajuste</option></select></div>
          <div class="col-md-2"><label class="form-label">Cantidad</label><input class="form-control" type="number" id="cantidad" min="1" required></div>
          <div class="col-md-4"><label class="form-label">Motivo</label><input class="form-control" id="motivo" required></div>
        </div>
        <button class="btn btn-primary mt-3" type="submit">Registrar</button>
      </form>`;
    detalle.classList.remove("d-none");
    document.querySelector("#form-mov").addEventListener("submit", async (e) => {
      e.preventDefault();
      try {
        await apiJson("/api/auditorias/movimientos", { method: "POST", body: JSON.stringify({
          sku: document.querySelector("#sku").value, tipo: document.querySelector("#tipo").value,
          cantidad: parseInt(document.querySelector("#cantidad").value), motivo: document.querySelector("#motivo").value
        }) });
        showAlert("Movimiento registrado.");
        detalle.classList.add("d-none");
        loadMovimientos();
      } catch (err) { showAlert(err.message, "danger"); }
    });
  });

  async function loadAuditorias() {
    const items = await apiJson("/api/auditorias");
    tbodyAud.innerHTML = items.map(a => `
      <tr>
        <td>${escapeHtml(a.id)}</td>
        <td>${escapeHtml(a.sku)}</td>
        <td>${escapeHtml(a.tipo)}</td>
        <td>${escapeHtml(a.fecha)}</td>
        <td><span class="badge text-bg-light">${escapeHtml(a.estado)}</span></td>
        <td>${a.estado === "PENDIENTE" ? `<button class="btn btn-success btn-sm" data-id="${a.id}">Completar</button>` : ""}</td>
      </tr>`).join("") || `<tr><td colspan="6" class="text-center text-secondary">No hay auditorias.</td></tr>`;
    tbodyAud.querySelectorAll("button[data-id]").forEach(b => b.addEventListener("click", async () => {
      const obs = prompt("Observaciones:") || "";
      await apiJson(`/api/auditorias/${b.dataset.id}/completar`, { method: "PUT", body: JSON.stringify({ observaciones: obs }) });
      showAlert("Auditoria completada.");
      loadAuditorias();
    }));
  }

  async function loadMovimientos() {
    const items = await apiJson("/api/auditorias/movimientos");
    tbodyMov.innerHTML = items.map(m => `
      <tr><td>${escapeHtml(m.id)}</td><td>${escapeHtml(m.sku)}</td><td>${escapeHtml(m.tipo)}</td><td>${m.cantidad}</td><td>${escapeHtml(m.motivo)}</td><td>${escapeHtml(m.fecha)}</td></tr>
    `).join("") || `<tr><td colspan="6" class="text-center text-secondary">No hay movimientos.</td></tr>`;
  }
}
