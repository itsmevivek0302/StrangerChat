let selected=null, conv=null, socket=null, me=null;
const userList=document.getElementById("users");
const usersById=new Map();
const messagesElement=document.getElementById("messages");
const chatError=document.getElementById("chatError");

(async()=>{
 if(!token()){location.href="login.html";return}
 try{
  me=await api("/api/users/me");
  document.getElementById("me").textContent="@"+me.username;
  await loadUsers();
  connectSocket();
 }catch(error){
  if(error.status===401){localStorage.removeItem("token");location.href="login.html";return}
  showError(error.message);
 }
})();

userList.addEventListener("click",event=>{
 const item=event.target.closest("[data-user-id]");
 if(item)selectUser(usersById.get(Number(item.dataset.userId)));
});

async function loadUsers(){
 try{
  const q=document.getElementById("search").value;
  const users=await api("/api/users/discover?q="+encodeURIComponent(q));
  usersById.clear();
  for(const user of users)usersById.set(user.id,user);
  userList.innerHTML=users.map(user=>`<div class="user" data-user-id="${user.id}"><b>${esc(user.username)}</b> ${user.is_online?'<span class="online">● online</span>':''}<div>${esc(user.bio||"")}</div></div>`).join("");
 }catch(error){
  userList.textContent=error.message;
 }
}

async function selectUser(user){
 if(!user)return;
 selected=user;
 conv=null;
 chatError.textContent="";
 document.getElementById("empty").hidden=true;
 document.getElementById("panel").hidden=false;
 document.getElementById("chatName").textContent="@"+user.username;
 document.getElementById("chatBio").textContent=user.bio||"";
 document.getElementById("typing").textContent="";
 messagesElement.replaceChildren();
 try{
  conv=await api("/api/chats/with/"+user.id,{method:"POST"});
  await loadMessages();
 }catch(error){
  showError(error.message);
 }
}

async function loadMessages(){
 await api("/api/chats/"+conv.id+"/read",{method:"POST"});
 const messages=await api("/api/chats/"+conv.id+"/messages");
 messagesElement.innerHTML=messages.map(render).join("");
 scrollBottom();
}

function render(message){
 const mine=message.sender_id===me.id;
 const receipt=mine?(message.is_read?"✓✓":"✓"):"";
 return `<div class="msg ${mine?'mine':''}" data-message-id="${message.id}">${esc(message.body)}<div class="meta">${new Date(message.created_at).toLocaleString()} <span class="receipt">${receipt}</span></div></div>`;
}

function appendMessage(message){
 if(messagesElement.querySelector(`[data-message-id="${message.id}"]`))return;
 messagesElement.insertAdjacentHTML("beforeend",render(message));
 scrollBottom();
}

document.getElementById("sendForm").addEventListener("submit",async event=>{
 event.preventDefault();
 if(!conv)return;
 const input=document.getElementById("message");
 if(!input.value.trim())return;
 chatError.textContent="";
 try{
  const sent=await api("/api/chats/"+conv.id+"/messages",{method:"POST",body:JSON.stringify({body:input.value})});
  input.value="";
  appendMessage(sent);
 }catch(error){
  showError(error.message);
 }
});

let typingTimer;
document.getElementById("message").addEventListener("input",()=>{
 if(!socket||!selected||socket.readyState!==WebSocket.OPEN)return;
 socket.send(JSON.stringify({type:"typing",to:selected.id,value:true}));
 clearTimeout(typingTimer);
 typingTimer=setTimeout(()=>{
  if(socket&&socket.readyState===WebSocket.OPEN)socket.send(JSON.stringify({type:"typing",to:selected.id,value:false}));
 },700);
});

function connectSocket(){
 const wsURL=API.replace(/^http/,"ws")+"/ws?token="+encodeURIComponent(token());
 socket=new WebSocket(wsURL);
 socket.onmessage=event=>{
  let data;
  try{data=JSON.parse(event.data)}catch(error){console.error("Invalid WebSocket message",error);return}
  if(data.type==="message"&&conv&&data.message.conversation_id===conv.id){
   appendMessage(data.message);
   if(data.message.sender_id!==me.id)api("/api/chats/"+conv.id+"/read",{method:"POST"}).catch(showError);
  }
  if(data.type==="read"&&conv&&data.conversation_id===conv.id){
   messagesElement.querySelectorAll(".msg.mine .receipt").forEach(receipt=>receipt.textContent="✓✓");
  }
  if(data.type==="typing"&&selected&&data.from===selected.id)document.getElementById("typing").textContent=data.typing?"typing…":"";
 };
 socket.onclose=event=>{
  if(event.code===1008){
   localStorage.removeItem("token");
   location.href="login.html";
   return;
  }
  if(token())setTimeout(connectSocket,2000);
 };
}

function scrollBottom(){messagesElement.scrollTop=messagesElement.scrollHeight}
function showError(message){chatError.textContent=message}
function esc(value){return String(value??"").replace(/[&<>"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[char]))}

async function blockUser(){
 if(!selected||!confirm("Block this user?"))return;
 try{
  await api("/api/users/"+selected.id+"/block",{method:"POST"});
  selected=null;
  location.reload();
 }catch(error){showError(error.message)}
}

async function reportUser(){
 if(!selected)return;
 const reason=prompt("Why are you reporting this user?");
 if(!reason)return;
 try{
  const result=await api("/api/reports/"+selected.id,{method:"POST",body:JSON.stringify({reason})});
  alert(result.message);
 }catch(error){showError(error.message)}
}
