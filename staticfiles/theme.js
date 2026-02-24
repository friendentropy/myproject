// theme.js - simple theme toggle (stores preference in localStorage)
(function(){
  const body = document.body;
  const toggleBtn = document.getElementById('theme-toggle-btn');

  // initialize
  const saved = localStorage.getItem('site-theme');
  if(saved === 'dark'){
    body.classList.add('dark');
  }

  function setDark(){
    body.classList.add('dark');
    localStorage.setItem('site-theme','dark');
  }
  function setLight(){
    body.classList.remove('dark');
    localStorage.setItem('site-theme','light');
  }

  if(toggleBtn){
    toggleBtn.addEventListener('click', ()=>{
      if(body.classList.contains('dark')) setLight(); else setDark();
    });
  }
})();
