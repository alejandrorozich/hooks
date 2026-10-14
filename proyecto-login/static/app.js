// Frontend del login: habla con la API JSON de servidor.py.
// El token de sesión se guarda en sessionStorage (se borra al cerrar la pestaña).
const CLAVE_TOKEN = "token"

const $ = (selector) => document.querySelector(selector)
const mensaje = $("#mensaje")

const mostrarMensaje = (texto, tipo = "error") => {
  mensaje.textContent = texto
  mensaje.className = tipo
}

async function api(ruta, { metodo = "GET", datos } = {}) {
  const cabeceras = { "Content-Type": "application/json" }
  const token = sessionStorage.getItem(CLAVE_TOKEN)
  if (token) cabeceras.Authorization = `Bearer ${token}`

  const respuesta = await fetch(ruta, {
    method: metodo,
    headers: cabeceras,
    body: datos ? JSON.stringify(datos) : undefined,
  })
  const cuerpo = await respuesta.json().catch(() => ({}))
  if (!respuesta.ok) throw new Error(cuerpo.error ?? "Error inesperado del servidor")
  return cuerpo
}

function cambiarPestana(vista) {
  document.querySelectorAll(".pestana").forEach((b) => b.classList.toggle("activa", b.dataset.vista === vista))
  $("#form-login").hidden = vista !== "login"
  $("#form-registro").hidden = vista !== "registro"
  mostrarMensaje("")
}

function mostrarPerfil(usuario) {
  $("#perfil-nombre").textContent = usuario.nombre
  $("#perfil-email").textContent = usuario.email
  $("#vista-acceso").hidden = true
  $("#vista-perfil").hidden = false
}

function mostrarAcceso() {
  $("#vista-acceso").hidden = false
  $("#vista-perfil").hidden = true
}

// Deshabilita el botón mientras se envía, para evitar dobles envíos
async function enviar(form, accion) {
  const boton = form.querySelector("button[type=submit]")
  boton.disabled = true
  try {
    await accion(Object.fromEntries(new FormData(form)))
  } catch (error) {
    mostrarMensaje(error.message)
  } finally {
    boton.disabled = false
  }
}

$("#form-login").addEventListener("submit", (evento) => {
  evento.preventDefault()
  enviar(evento.target, async (datos) => {
    const { token, usuario } = await api("/api/login", { metodo: "POST", datos })
    sessionStorage.setItem(CLAVE_TOKEN, token)
    evento.target.reset()
    mostrarPerfil(usuario)
    mostrarMensaje("Sesión iniciada", "exito")
  })
})

$("#form-registro").addEventListener("submit", (evento) => {
  evento.preventDefault()
  enviar(evento.target, async (datos) => {
    await api("/api/registro", { metodo: "POST", datos })
    evento.target.reset()
    cambiarPestana("login")
    $("#form-login [name=email]").value = datos.email
    mostrarMensaje("Cuenta creada. Ahora inicia sesión.", "exito")
  })
})

$("#btn-logout").addEventListener("click", async () => {
  await api("/api/logout", { metodo: "POST" }).catch(() => {})
  sessionStorage.removeItem(CLAVE_TOKEN)
  mostrarAcceso()
  mostrarMensaje("Sesión cerrada", "exito")
})

document.querySelectorAll(".pestana").forEach((b) => b.addEventListener("click", () => cambiarPestana(b.dataset.vista)))

// Al cargar: si hay un token guardado, se valida contra el servidor
;(async () => {
  if (!sessionStorage.getItem(CLAVE_TOKEN)) return
  try {
    const { usuario } = await api("/api/perfil")
    mostrarPerfil(usuario)
  } catch {
    sessionStorage.removeItem(CLAVE_TOKEN)
  }
})()
