let user = null;
async function init() {
  user = await checkAuth();
  return user;
};

init().then(() => {

const userName = document.getElementById("user-name");
userName.textContent = user["name"];

const userRole = document.getElementById("user-role");
userRole.textContent = user["role"];

let userIcon = user["name"].split(" ");
if (userIcon.length == 1) {
  userIcon = userIcon[0].charAt(0).toUpperCase();
} else {
  userIcon = userIcon[0].charAt(0).toUpperCase() + userIcon[1].charAt(1).toUpperCase();
}

if (user.role == "student") {
  getHomeworks();
} else if (user.role == "teacher") {
  document.body.innerHTML = "<h1>Вы учитель</h1>";
} else if (user.role == "admin") {
  document.body.innerHTML = "<h1>Вы админ</h1>";
} else {
  throw new Error("Неизвестная роль")
}
});

const homework = document.getElementById("homework");

async function getHomeworks() {
  const token = localStorage.getItem("access_token");
  const response = await fetch("/api/students/me/homeworks", {
    method: "GET",
    headers: {
      "Authorization": "Bearer " + token
    }
  });

  if (!response.ok) {
    throw new Error("Ошибка запроса к API");
  };

  const data = await response.json();

  if (data.length == 0) {
    homework.textContent = "Нет домашних заданий!";
  } else if (data.length != 0) {
    data.forEach(hw => {
      const item = document.createElement("div");
      const title = document.createElement("p");
      const desc = document.createElement("p");
      const subjName = document.createElement("h2");
      const date = document.createElement("p");

      title.textContent = hw.title;
      desc.textContent = hw.description;
      subjName.textContent = hw.subject_name;
      
      const d = new Date(hw.due_date);
      date.textContent = d.getDate() + "." + (d.getMonth() + 1) + "." + d.getFullYear();
      
      item.appendChild(title);
      item.appendChild(desc);
      item.appendChild(subjName);
      item.appendChild(date);
      homework.appendChild(item);
    });
  };
};

