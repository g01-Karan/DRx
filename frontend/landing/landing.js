document.addEventListener("DOMContentLoaded", () => {
  // 1. Mouse Glow Effect
  const cursorGlow = document.getElementById("cursorGlow");
  if (cursorGlow) {
    document.addEventListener("mousemove", (e) => {
      cursorGlow.style.left = `${e.clientX}px`;
      cursorGlow.style.top = `${e.clientY}px`;
    });
  }

  // 2. Navbar Scroll Effect
  const navbar = document.querySelector(".navbar");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  });

  // 3. 3D Card Tilt Effect on Mouse Movement
  const glassCards = document.querySelectorAll(".glass-card, .feature-card");
  glassCards.forEach((card) => {
    card.addEventListener("mousemove", (e) => {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      const centerX = rect.width / 2;
      const centerY = rect.height / 2;

      const rotateX = ((y - centerY) / centerY) * -10;
      const rotateY = ((x - centerX) / centerX) * 10;

      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
    });

    card.addEventListener("mouseleave", () => {
      card.style.transform = "perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
    });
  });

  // 4. GSAP & ScrollTrigger Animations
  if (typeof gsap !== "undefined") {
    // Register ScrollTrigger if available
    if (typeof ScrollTrigger !== "undefined") {
      gsap.registerPlugin(ScrollTrigger);
    }

    // Hero Section Animations
    const tl = gsap.timeline();
    tl.from(".navbar", { y: -50, opacity: 0, duration: 0.8, ease: "power3.out" })
      .from(".hero-badge", { y: 20, opacity: 0, duration: 0.5, ease: "power3.out" }, "-=0.4")
      .from(".hero-title", { y: 30, opacity: 0, duration: 0.7, ease: "power3.out" }, "-=0.3")
      .from(".hero-subtitle", { y: 20, opacity: 0, duration: 0.5, ease: "power3.out" }, "-=0.4")
      .from(".hero-description", { y: 20, opacity: 0, duration: 0.5, ease: "power3.out" }, "-=0.3")
      .from(".hero-buttons", { y: 20, opacity: 0, duration: 0.5, ease: "power3.out" }, "-=0.3")
      .from(".hero-showcase", { scale: 0.9, opacity: 0, duration: 0.8, ease: "back.out(1.7)" }, "-=0.6");

    // Feature Cards ScrollTrigger
    if (typeof ScrollTrigger !== "undefined") {
      gsap.from(".feature-card", {
        scrollTrigger: {
          trigger: ".features-section",
          start: "top 90%",
        },
        y: 30,
        opacity: 0,
        duration: 0.5,
        stagger: 0.1,
        ease: "power2.out",
        clearProps: "all"
      });

      gsap.from(".about-container", {
        scrollTrigger: {
          trigger: ".about-section",
          start: "top 90%",
        },
        y: 30,
        opacity: 0,
        duration: 0.6,
        ease: "power2.out",
        clearProps: "all"
      });

      gsap.from(".cta-container", {
        scrollTrigger: {
          trigger: ".cta-section",
          start: "top 90%",
        },
        scale: 0.96,
        opacity: 0,
        duration: 0.6,
        ease: "power2.out",
        clearProps: "all"
      });
    }
  }

  // 5. Animated Number Counters for Stats
  const counters = document.querySelectorAll(".counter");
  let speed = 200;

  const startCounters = () => {
    counters.forEach((counter) => {
      const target = +counter.getAttribute("data-target");
      let count = 0;
      const inc = target / speed;

      const updateCount = () => {
        count += inc;
        if (count < target) {
          counter.innerText = (target % 1 === 0) ? Math.ceil(count) : count.toFixed(1);
          setTimeout(updateCount, 15);
        } else {
          counter.innerText = target;
        }
      };

      updateCount();
    });
  };

  // Trigger counters when scrolled into view
  let animated = false;
  window.addEventListener("scroll", () => {
    const statsSection = document.getElementById("stats");
    if (statsSection && !animated) {
      const pos = statsSection.getBoundingClientRect().top;
      if (pos < window.innerHeight - 100) {
        startCounters();
        animated = true;
      }
    }
  });

  // Check if user is already logged in
  const localUser = localStorage.getItem("drx_user");
  if (localUser) {
    const navLoginBtn = document.getElementById("navLoginBtn");
    const navCtaBtn = document.getElementById("navCtaBtn");
    const heroGetStartedBtn = document.getElementById("heroGetStartedBtn");
    const ctaStartNowBtn = document.getElementById("ctaStartNowBtn");
    const footerLoginLink = document.getElementById("footerLoginLink");

    if (navLoginBtn) {
      navLoginBtn.textContent = "Dashboard";
      navLoginBtn.href = "/dashboard";
    }
    if (navCtaBtn) {
      navCtaBtn.innerHTML = 'Go to Dashboard <i class="fa-solid fa-arrow-right"></i>';
      navCtaBtn.href = "/dashboard";
    }
    if (heroGetStartedBtn) {
      heroGetStartedBtn.innerHTML = '<span>Go to Dashboard</span><i class="fa-solid fa-arrow-right"></i>';
      heroGetStartedBtn.href = "/dashboard";
    }
    if (ctaStartNowBtn) {
      ctaStartNowBtn.innerHTML = '<span>Open Dashboard</span><i class="fa-solid fa-arrow-right"></i>';
      ctaStartNowBtn.href = "/dashboard";
    }
    if (footerLoginLink) {
      footerLoginLink.textContent = "Dashboard";
      footerLoginLink.href = "/dashboard";
    }
  }
});
