document.addEventListener("DOMContentLoaded", () => {

/* ============================================================
PAGINAÇÃO
============================================================ */

const cards = Array.from(document.querySelectorAll(".cartao-card"));
const porPagina = 7;
let paginaAtual = 1;

function renderPagina(){

const lista = document.getElementById("lista-gastos");

lista.innerHTML = "";

const inicio = (paginaAtual - 1) * porPagina;
const fim = inicio + porPagina;

cards.slice(inicio,fim).forEach(card=>{
lista.appendChild(card);
});

renderPaginacao();

}

function renderPaginacao(){

const totalPaginas = Math.ceil(cards.length / porPagina);
const pag = document.getElementById("paginacao");

pag.innerHTML = "";

if(totalPaginas <= 1) return;

for(let i=1;i<=totalPaginas;i++){

const btn = document.createElement("button");

btn.innerText = i;

if(i === paginaAtual) btn.classList.add("ativo");

btn.onclick = ()=>{
paginaAtual = i;
renderPagina();
};

pag.appendChild(btn);

}

}

renderPagina();


/* ============================================================
SALVAR SEM RECARREGAR
============================================================ */

document.querySelectorAll(".cartao-card").forEach(form=>{

form.addEventListener("submit", function(e){

e.preventDefault();

const formData = new FormData(form);

fetch(form.action,{
method:"POST",
body:formData
})
.then(r=>r.json())
.then(data=>{

if(data.sucesso){

form.classList.add("card-salvo");

setTimeout(()=>{
form.classList.remove("card-salvo");
},450);

mostrarToast("✔ Alteração salva","success");

}

});

});

});


/* ============================================================
TOAST
============================================================ */

function mostrarToast(msg,tipo="success"){

const toast = document.getElementById("toast");

toast.className = "toast " + tipo;

toast.innerText = msg;

toast.classList.add("show");

setTimeout(()=>{
toast.classList.remove("show");
},2000);

}


/* ============================================================
EXCLUIR CARTÃO
============================================================ */

let gastoParaExcluir = null;

const modal = document.getElementById("modalConfirm");
const btnCancelar = document.getElementById("cancelarExcluir");
const btnConfirmar = document.getElementById("confirmarExcluir");

document.querySelectorAll(".btn-excluir").forEach(btn=>{

btn.addEventListener("click",function(){

gastoParaExcluir = btn;

modal.classList.add("show");

});

});

btnCancelar.onclick = ()=>{
modal.classList.remove("show");
};

btnConfirmar.onclick = ()=>{

const id = gastoParaExcluir.dataset.id;

fetch("/gasto-cartao/apagar/" + id,{
method:"POST"
})
.then(r=>r.json())
.then(data=>{

if(data.sucesso){

const item = gastoParaExcluir.closest(".cartao-card");

item.classList.add("card-removendo");

setTimeout(()=>{
item.remove();
},350);

mostrarToast("🗑 Gasto excluído","error");

}

});

modal.classList.remove("show");

};


/* ============================================================
FECHAR MODAL CLICANDO FORA
============================================================ */

modal.onclick = (e)=>{

if(e.target === modal){
modal.classList.remove("show");
}

};

});
