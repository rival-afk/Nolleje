const loginTab = document.getElementById("loginTab");
const registerTab = document.getElementById("registerTab");
const login = document.getElementById("login");
const register = document.getElementById("register");

//регистрация
const registerName = document.getElementById("register-name");
const registerEmail = document.getElementById("register-email");
const registerPassword = document.getElementById("register-password");
const classesList = document.getElementById("class-select");
const classes = fetch("/api/classes")
.then(response => response.json())
.then(data => {
  data.forEach(item => {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = item.name + " " + item.class;
    classesList.appendChild(option);
  })
});
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
  
  fetch("/api/auth/login", {
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
    document.getElementById("error").textContent = error
  });
});

registerButton.addEventListener("click", function () {
  const name = registerName.value;
  const email = registerEmail.value;
  const password = registerPassword.value;
  let class_id_str = classesList.value;
  let class_id = null;

  if (!role) {
    document.getElementById("error").textContent = "Выберите роль";
    return;
  };

  if (!classId) {
    document.getElementById("error").textContent = "Выбери класс";
  };

  if (role = 'student') {
    class_id = Number(class_id_str);
  };

  console.log(class_id, typeof class_id);

  fetch("/api/auth/register", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name: name,
      email: email,
      password: password,
      role: role,
      class_id: class_id
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new OverconstrainedError("Ошибка в процессе регистрации")
    }
    return fetch("/api/auth/login", {
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
      };
      return response.json();
    })
    .then(data => {
      const token = data.access_token;
      localStorage.setItem("token", token);

      return fetch("/api/users/me", {
        headers: {
          "Authorization": "Bearer " + token
        }
      });
    })
    .then(response => {
      if (!response.ok) {
        throw new Error("Ошибка в процессе логина");
      };
      return response.json();
    })
    .then(user => {
      if (user.role == 'teacher') {
        window.location.href = "/choose_class.html";
      } else {
        window.location.href = "/dashboard.html";
      };
    })
    .catch(error => {
      document.getElementById("error").textContent = "Неверный логин или пароль"
    });
  });
});