const form=document.getElementById("form");
form.addEventListener("submit",async e=>{
 e.preventDefault(); const error=document.getElementById("error");
 error.textContent="";
 try{
  const usernameInput=document.getElementById("username");
  const emailInput=document.getElementById("email");
  const passwordInput=document.getElementById("password");
  let data;
  if(location.pathname.endsWith("register.html")){
   data=await api("/api/auth/register",{method:"POST",body:JSON.stringify({username:usernameInput.value,email:emailInput.value,password:passwordInput.value})});
  }else{
   data=await api("/api/auth/login",{method:"POST",body:JSON.stringify({email:emailInput.value,password:passwordInput.value})});
  }
  localStorage.setItem("token",data.access_token); localStorage.setItem("user",JSON.stringify(data.user)); location.href="chat.html";
 }catch(e){error.textContent=e.message}
});
