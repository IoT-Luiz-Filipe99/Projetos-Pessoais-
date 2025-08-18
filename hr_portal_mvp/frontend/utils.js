// Basic helpers for API + auth
const API = location.origin.replace(/\/$/, ""); // same origin
function getToken(){ return localStorage.getItem("token") || ""; }
async function api(path, opts={}){
  const headers = opts.headers || {};
  if(!headers["Content-Type"] && !(opts.body instanceof FormData)){
    headers["Content-Type"] = "application/json";
  }
  const token = getToken();
  if(token){ headers["Authorization"] = "Bearer " + token; }
  const res = await fetch(API + path, { ...opts, headers });
  if(!res.ok){
    const txt = await res.text();
    throw new Error(txt || "Erro de rede");
  }
  try{ return await res.json(); }catch{ return {}; }
}
function requireAuth(){
  const t = getToken();
  if(!t){ location.href = "./login.html"; }
}
async function loadMe(){
  try{
    const me = await api("/me");
    return me;
  }catch(e){
    localStorage.removeItem("token");
    location.href = "./login.html";
  }
}
