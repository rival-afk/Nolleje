const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");
const login = document.getElementById("login");
const register = document.getElementById("register");

//регистрация
const registerName = document.getElementById("register-name");
const registerEmail = document.getElementById("register-email");
const registerPassword = document.getElementById("register-password");
let role = null;
let classId = null;

//логин
const loginEmail = document.getElementById("login-email");
const loginPassword = document.getElementById("login-password");

//кнопки отправки формы (ну регистрация и логин)
const loginButton = document.getElementById("login-button");
const registerButton = document.getElementById("register-button");

//кнопки ролей
const roleStudentButton = document.getElementById("student") 
const roleTeacherButton = document.getElementById("teacher")
const roleAdminButton = document.getElementById("admin")

roleAdminButton.addEventListener("click", function () {
  role = 'admin';
});

roleStudentButton.addEventListener("click", function () {
  role = 'student';
});

roleTeacherButton.addEventListener("click", function () {
  role = 'teacher'
});

loginTab.addEventListener("click", function () {
  login.style.display = "block";
  register.style.display = "none";
});

registerTab.addEventListener("click", function () {
  login.style.display = "none";
  register.style.display = "block";
});

loginButton.addEventListener("click", function () {
  const email = loginEmail.value;
  const password = loginPassword.value;
  
  fetch("http://localhost:8000/auth/login", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      email: email,
      password: password
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error("Ошибка в процессе логина");
    }
    return response.json();
  })
  .then(data => {
    localStorage.setItem("access_token", data.access_token);
    window.location.href = "/dashboard.html";
  })
  .catch(error => {
    document.getElementById("error").textContent = "Неверный логин или пароль"
  });
});

registerButton.addEventListener("click", function () {
  const name = registerName.value;
  const email = registerEmail.value;
  const password = registerPassword.value;

  if (!role) {
    document.getElementById("error").textContent = "Выберите роль";
    return;
  };

  if (!classId) {
    document.getElementById("error").textContent = "Выбери класс";
  };

  fetch("http://localhost:8000/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name: name,
      email: email,
      password: password,
      role: role
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new OverconstrainedError("Ошибка в процессе регистрации")
    }
    return fetch("http://localhost:8000/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email: email,
        password: password
      })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Ошибка в процессе логина");
      }
      return response.json();
    })
    .then(data => {
      localStorage.setItem("access_token", data.access_token);
      window.location.href = "/dashboard.html";
    })
    .catch(error => {
      document.getElementById("error").textContent = "Неверный логин или пароль"
    });
  });
});