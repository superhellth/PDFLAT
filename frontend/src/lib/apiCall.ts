const apiCall = async (url) => {
  console.log(url);
  const response = await fetch(url);
  const jsonData = await response.json();
  return jsonData;
};

const apiCallFrontend = async (route: String) => {
  const url = `http://localhost:1337/${route}`;
  return await apiCall(url);
};

const apiCallBackend = async (route: String) => {
  const url = `http://api/${route}`;
  return await apiCall(url);
};

export {apiCallFrontend, apiCallBackend}