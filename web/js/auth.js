async function checkAuth() {
  try {
    const token = localStorage.getItem("access_token");

    if (!token) {
      window.location.href = "/login";
      return;
    };

    const response = await fetch("/api/users/me", {
      method: "GET",
      headers: {
        "Authorization": "Bearer " + token
      }
    });

    if (response.status == 401) {
      window.location.href = "/login";
      return;
    };

    if (!response.ok) {
      throw new Error("Ошибка запроса");
    }

    const user = await response.json();
    return user;
  } catch (e) {
    throw new Error(e)
  }
}