document.addEventListener("DOMContentLoaded", () => {

  // =====================================================
  // MENU MOBILE
  // =====================================================

  const sidebar = document.querySelector(".sidebar")
  const toggle = document.querySelector(".menu-toggle")
  const overlay = document.querySelector(".overlay")
  const links = document.querySelectorAll(".sidebar a")

  function openMenu() {

    sidebar.classList.add("open")

    if (overlay) overlay.classList.add("show")

    document.body.style.overflow = "hidden"

  }

  function closeMenu() {

    sidebar.classList.remove("open")

    if (overlay) overlay.classList.remove("show")

    document.body.style.overflow = ""

  }

  if (toggle) toggle.addEventListener("click", openMenu)

  if (overlay) overlay.addEventListener("click", closeMenu)

  links.forEach(link => {
    link.addEventListener("click", closeMenu)
  })

  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeMenu()
  })

  window.addEventListener("resize", () => {
    if (window.innerWidth > 900) closeMenu()
  })


  // =====================================================
  // BUSCA DE USUÁRIOS
  // =====================================================

  const searchInput = document.querySelector("#buscarUsuario")

  if (searchInput) {

    searchInput.addEventListener("input", () => {

      const termo = searchInput.value.toLowerCase()

      const usuarios = document.querySelectorAll(".user-item")

      usuarios.forEach(user => {

        const nome = user.dataset.nome || ""
        const whatsapp = user.dataset.whatsapp || ""

        if (
          nome.includes(termo) ||
          whatsapp.includes(termo)
        ) {

          user.style.display = "flex"

        } else {

          user.style.display = "none"

        }

      })

    })

  }


  // =====================================================
  // TABS (CARTÕES / GASTOS / RENDAS)
  // =====================================================

  const tabs = document.querySelectorAll(".tab")

  tabs.forEach(btn => {

    btn.addEventListener("click", () => {

      document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"))
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"))

      btn.classList.add("active")

      const alvo = document.getElementById(btn.dataset.tab)

      if (alvo) alvo.classList.add("active")

    })

  })

})

// =====================================================
// ABRIR ABA PELA URL
// =====================================================

const params = new URLSearchParams(window.location.search)
const tab = params.get("tab")

if (tab) {

document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"))
document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"))

const botao = document.querySelector(`.tab[data-tab="${tab}"]`)
const conteudo = document.getElementById(tab)

if (botao && conteudo) {

botao.classList.add("active")
conteudo.classList.add("active")

}

}