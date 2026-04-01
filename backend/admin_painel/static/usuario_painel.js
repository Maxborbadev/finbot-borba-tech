/* ============================================================
FINBOT — JS USUÁRIO
============================================================ */

function gerarCores(qtd) {
  const cores = [];

  for (let i = 0; i < qtd; i++) {
    const hue = i * (360 / qtd);
    cores.push(`hsl(${hue},70%,55%)`);
  }

  return cores;
}

/* ============================================================
PLUGIN SOMBRA SUAVE (Chart.js)
============================================================ */

const softShadowPlugin = {
  id: "softShadow",
  beforeDatasetsDraw(chart) {
    const ctx = chart.ctx;
    ctx.save();
    ctx.shadowColor = "rgba(15,23,42,.18)";
    ctx.shadowBlur = 10;
    ctx.shadowOffsetY = 4;
  },
  afterDatasetsDraw(chart) {
    chart.ctx.restore();
  },
};

Chart.register(softShadowPlugin);

const centerTextPlugin = {
  id: "centerText",

  afterDraw(chart) {
    if (chart.config.type !== "doughnut") return;

    const { ctx } = chart;

    const meta = chart.getDatasetMeta(0);
    const x = meta.data[0].x;
    const y = meta.data[0].y;

    const data = chart.data.datasets[0].data;
    const total = data.reduce((a, b) => a + b, 0);

    ctx.save();

    const valor = total.toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    });

    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    /* valor */

    ctx.font = "bold 19px JetBrains Mono"; // ↓ diminui o tamanho
    ctx.fillStyle = "#f9fafb";

    /* borda do texto */

    ctx.lineWidth = 3;
    ctx.strokeStyle = "rgba(0,0,0,.6)";
    ctx.strokeText(valor, x, y - 6);

    ctx.fillText(valor, x, y - 6);

    /* subtítulo */

    ctx.font = "14px Inter";
    ctx.fillStyle = "#9ca3af";

    ctx.fillText("gastos", x, y + 16);

    ctx.restore();
  },
};

Chart.register(centerTextPlugin);

/* ============================================================
GRÁFICO DE LINHA
============================================================ */

function criarGraficoLinha() {
  fetch("/grafico/usuario")
    .then((res) => res.json())
    .then((dados) => {
      const canvas = document.getElementById("graficoLinha");
      if (!canvas) return;

      new Chart(canvas, {
        type: "line",

        data: {
          labels: dados.dias,

          datasets: [
            {
              label: "Gastos",
              data: dados.gastos,
              borderColor: "#ef4444",
              backgroundColor: "#ef449a2d",
              fill: true,
              tension: 0.3,
              borderWidth: 3,
              pointRadius: (ctx) => (ctx.raw > 0 ? 4 : 0),
              pointHoverRadius: 6,
            },

            {
              label: "Rendas",
              data: dados.rendas,
              borderColor: "#22c55e",
              backgroundColor: "#22c5aa3b",
              fill: true,
              tension: 0.6,
              borderWidth: 3,
              borderDash: [7, 8],
              pointRadius: (ctx) => (ctx.raw > 0 ? 4 : 0),
              pointHoverRadius: 6,
            },
          ],
        },

        options: {
          responsive: true,
          maintainAspectRatio: false,

          animation: {
            duration: 1200,
            easing: "easeOutQuart",
          },
        },
      });
    });
}

const linhaObserver = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) {
    criarGraficoLinha();
    linhaObserver.disconnect();
  }
});

const graficoLinha = document.getElementById("graficoLinha");

if (graficoLinha) {
  linhaObserver.observe(graficoLinha);
}

/* ============================================================
GRÁFICO DONUT (CATEGORIAS)
============================================================ */
function criarGraficoPizza() {
  fetch("/grafico/pizza")
    .then((res) => res.json())
    .then((dados) => {
      const canvas = document.getElementById("graficoPizza");
      if (!canvas) return;

      new Chart(canvas, {
        type: "doughnut",

        data: {
          labels: dados.categorias,

          datasets: [
            {
              data: dados.valores,
              backgroundColor: gerarCores(dados.valores.length),
              borderWidth: 1.2,
              borderColor: "#ffffff",
            },
          ],
        },

        options: {
          responsive: true,
          maintainAspectRatio: false,

          animation: {
            animateRotate: true,
            animateScale: true,
            duration: 1400,
            easing: "easeOutQuart",
          },

          cutout: "60%",

          plugins: {
            legend: {
              position: "top",
              labels: {
                usePointStyle: true,
                pointStyle: "rectRounded",
                padding: 12,
                font: { size: 12 },
              },
            },

            tooltip: {
              callbacks: {
                label: function (context) {
                  let valor = context.raw;

                  return valor.toLocaleString("pt-BR", {
                    style: "currency",
                    currency: "BRL",
                  });
                },
              },
            },
          },
        },
      });
    });
}

const pizzaObserver = new IntersectionObserver((entries) => {
  if (entries[0].isIntersecting) {
    criarGraficoPizza();
    pizzaObserver.disconnect();
  }
});

const graficoPizza = document.getElementById("graficoPizza");

if (graficoPizza) {
  pizzaObserver.observe(graficoPizza);
}
/* ============================================================
DOM READY
============================================================ */

document.addEventListener("DOMContentLoaded", () => {
  /* ============================================================
TOGGLE GASTOS
============================================================ */

  const tituloGastos = document.querySelector(".toggle-gastos");
  const listaGastos = document.querySelector(".lista-gastos");

  if (tituloGastos && listaGastos) {
    tituloGastos.addEventListener("click", () => {
      listaGastos.classList.toggle("fechado");
      tituloGastos.classList.toggle("fechado");
    });
  }

  /* ============================================================
TOGGLE RENDAS
============================================================ */

  const tituloRendas = document.querySelector(".toggle-rendas");
  const listaRendas = document.querySelector(".lista-rendas");

  if (tituloRendas && listaRendas) {
    tituloRendas.addEventListener("click", () => {
      listaRendas.classList.toggle("fechado");
      tituloRendas.classList.toggle("fechado");
    });
  }

  /* ============================================================
AJAX FORM
============================================================ */

  document.querySelectorAll(".ajax-form").forEach((form) => {
    form.addEventListener("submit", async function (e) {
      e.preventDefault();

      const formData = new FormData(form);

      try {
        const response = await fetch(form.action, {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          form.classList.add("salvo");

          setTimeout(() => {
            form.classList.remove("salvo");
          }, 600);
        } else {
          alert("Erro ao salvar");
        }
      } catch {
        alert("Erro de conexão");
      }
    });
  });

  /* ============================================================
                          SLIDER CARTÃO
============================================================ */

  let slideAtual = 0;
  let startX = 0;
  let currentX = 0;
  let dragging = false;

  const slider = document.querySelector(".cartao-slider");

  if (!slider) return;

  const slides = slider.querySelector(".slides");
  const dots = slider.querySelectorAll(".dot");
  if (slider) {
    atualizarSlider();
    console.log("TOTAL SLIDES:", dots.length);

    function atualizarSlider(animar = true) {
      if (animar) {
        slides.style.transition = "transform 0.35s cubic-bezier(.22,.61,.36,1)";
      } else {
        slides.style.transition = "none";
      }

      slides.style.transform = `translateX(-${slideAtual * 100}%)`;

      dots.forEach((d) => d.classList.remove("ativo"));
      dots[slideAtual].classList.add("ativo");
    }

    slider.addEventListener("touchstart", (e) => {
      startX = e.touches[0].clientX;
      dragging = true;
      slides.style.transition = "none";
    });

    slider.addEventListener("touchmove", (e) => {
      if (!dragging) return;

      currentX = e.touches[0].clientX;

      const diff = currentX - startX;
      const percent = (diff / slides.offsetWidth) * 100;

      const offset = -slideAtual * 100 + percent;

      slides.style.transform = `translateX(${offset}%)`;
    });

    slider.addEventListener("touchend", () => {
      dragging = false;

      const diff = currentX - startX;

      if (Math.abs(diff) > 50) {
        if (diff < 0) {
          slideAtual++;
        } else {
          slideAtual--;
        }
      }

      if (slideAtual < 0) slideAtual = 0;
      const totalSlides = dots.length;

      if (slideAtual >= totalSlides) slideAtual = totalSlides - 1;

      atualizarSlider(true);
    });
  }
});
