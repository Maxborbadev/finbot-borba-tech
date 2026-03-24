function toggleSenha() {

  const campo = document.getElementById("senha");

  if (!campo) return;

  if (campo.type === "password") {
    campo.type = "text";
  } else {
    campo.type = "password";
  }

}