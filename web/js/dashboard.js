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
    homework.textContent = "Нет домашних заданий!"
  };

  homework.textContent = JSON.stringify(data, null, 2);
};

getHomeworks();