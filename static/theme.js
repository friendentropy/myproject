// --------------------
// THEME TOGGLE
// --------------------
(function(){
  const body = document.body;
  const toggleBtn = document.getElementById('theme-toggle-btn');

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
      if(body.classList.contains('dark')) setLight();
      else setDark();
    });
  }
})();



// ------------------------------------------------
// SIDEBAR + HAMBURGER ANIMATION + MINI CART
// ------------------------------------------------
document.addEventListener("DOMContentLoaded", function () {

  const sidebar = document.getElementById("sidebar");
  const overlay = document.getElementById("sidebar-overlay");
  const toggleBtn = document.getElementById("sidebar-toggle");
  const closeBtn = document.getElementById("close-sidebar");

  const miniCartBtn = document.getElementById("miniCartBtn");
  const miniCartDropdown = document.getElementById("miniCartDropdown");

  // ---- SIDEBAR OPEN/CLOSE ----
  function openSidebar() {
    sidebar.classList.add("open");
    overlay.classList.add("visible");
    toggleBtn.classList.add("open");   // << USES YOUR CSS ANIMATION
  }

  function closeSidebar() {
    sidebar.classList.remove("open");
    overlay.classList.remove("visible");
    toggleBtn.classList.remove("open");   // << REVERSE ANIMATION
  }

  // Toggle with same button
  if (toggleBtn) {
    toggleBtn.addEventListener("click", () => {
      if (sidebar.classList.contains("open")) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }

  if (closeBtn) closeBtn.addEventListener("click", closeSidebar);
  if (overlay) overlay.addEventListener("click", closeSidebar);


  // ---- MINI CART ----
  if (miniCartBtn && miniCartDropdown) {
    miniCartBtn.addEventListener("click", (e) => {
      e.preventDefault();
      miniCartDropdown.style.display =
        miniCartDropdown.style.display === "block" ? "none" : "block";
    });

    document.addEventListener("click", (e) => {
      if (!miniCartBtn.contains(e.target) && !miniCartDropdown.contains(e.target)) {
        miniCartDropdown.style.display = "none";
      }
    });
  }


  // ---- AUTO RESET WHEN RESIZING ----
  window.addEventListener("resize", () => {
    if (window.innerWidth > 992) {
      overlay.classList.remove("visible");
      sidebar.classList.remove("open");
      toggleBtn.classList.remove("open");
    }
  });
});
