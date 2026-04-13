async function init() {
  const user = await checkAuth();
  return user;
};

init();


