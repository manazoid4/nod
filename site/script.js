(() => {
 const copy={
 talk:{title:"ASK. LISTEN. NOD.",desc:"Short answers without another app.",left:"PRESS → SPEAK",right:"CALL",user:"“What's the next task on my project?”",answer:"Your computer looks up the project and returns a concise answer.",tag:"Voice requires the paired PC hub"},
 capture:{title:"HOLD THAT THOUGHT.",desc:"Capture now. Organise later.",left:"PRESS → CAPTURE",right:"NOTE",user:"“Remember to sketch the enclosure after work.”",answer:"A voice note is saved for review and future task organisation.",tag:"Capture workflow still undergoing hardware validation"},
 approve:{title:"YOUR CALL.",desc:"Sensitive actions wait for you.",left:"Y APPROVE · N DENY",right:"AGENT",user:"“Agent requests permission to deploy.”",answer:"Device shows the action and waits for explicit approval. No response must never silently approve.",tag:"Full remote approval loop not yet verified"}
 };
 const modes=[...document.querySelectorAll('[data-mode]')];
 const change=(key)=>{const x=copy[key];if(!x)return;
  modes.forEach(b=>{const on=b.dataset.mode===key;b.classList.toggle('active',on);b.setAttribute('aria-selected',String(on));b.tabIndex=on?0:-1;});
  const put=(id,val)=>{const el=document.getElementById(id);if(el)el.textContent=val};
  put('screen-title',x.title);put('screen-copy',x.desc);put('screen-left',x.left);put('screen-right',x.right);put('scenario-user',x.user);put('scenario-answer',x.answer);put('scenario-tag',x.tag);
  const panel=document.getElementById('scenario-panel');if(panel)panel.setAttribute('aria-labelledby','tab-'+key);
 };
 modes.forEach((b,i)=>{b.addEventListener('click',()=>change(b.dataset.mode));b.addEventListener('keydown',ev=>{if(!['ArrowDown','ArrowUp','ArrowRight','ArrowLeft','Home','End'].includes(ev.key))return;ev.preventDefault();const k=ev.key==='Home'?0:ev.key==='End'?modes.length-1:(i+(ev.key==='ArrowDown'||ev.key==='ArrowRight'?1:-1)+modes.length)%modes.length;modes[k].focus();change(modes[k].dataset.mode)})});
 if(modes.length)change('talk');
})();