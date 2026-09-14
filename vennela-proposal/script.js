/**
 * 💖 VENNELA & AKASH LOVE PROPOSAL SCRIPT
 * Interactive Cinematic Desktop-First Engine
 */

document.addEventListener('DOMContentLoaded', () => {

    // ==========================================
    // 1. STATE & CONFIGURATION INITIALIZATION
    // ==========================================
    const herName = CONFIG.HER_NAME || "Vennela";
    const yourName = CONFIG.YOUR_NAME || "Akash";
    let currentScene = 1;
    let noAttemptCount = 0;
    let isNoDodging = false;
    let s3Phase = 1;

    // Element References
    const cursorGlow = document.getElementById('cursorGlow');
    const bgCanvas = document.getElementById('bgCanvas');
    const ctx = bgCanvas ? bgCanvas.getContext('2d') : null;

    // Mouse Tracking
    let mouseX = window.innerWidth / 2;
    let mouseY = window.innerHeight / 2;

    window.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        if (cursorGlow) {
            cursorGlow.style.left = `${mouseX}px`;
            cursorGlow.style.top = `${mouseY}px`;
        }
    });

    // Handle Window Resize for Canvas & Dodge Bounds
    function resizeCanvas() {
        if (bgCanvas) {
            bgCanvas.width = window.innerWidth;
            bgCanvas.height = window.innerHeight;
        }
    }
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // ==========================================
    // 2. CANVAS AMBIENT PARTICLE ENGINE
    // ==========================================
    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * window.innerWidth;
            this.y = Math.random() * window.innerHeight;
            this.size = Math.random() * 2.5 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.4;
            this.speedY = -Math.random() * 0.6 - 0.2;
            this.alpha = Math.random() * 0.7 + 0.2;
            this.fadeSpeed = Math.random() * 0.008 + 0.002;
            this.isHeart = Math.random() < 0.12; // 12% floating hearts
            this.rotation = Math.random() * Math.PI * 2;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;
            this.alpha += this.fadeSpeed;

            if (this.alpha >= 0.95 || this.alpha <= 0.1) {
                this.fadeSpeed = -this.fadeSpeed;
            }

            if (this.y < -20 || this.x < -20 || this.x > window.innerWidth + 20) {
                this.reset();
                this.y = window.innerHeight + 10;
            }
        }

        draw() {
            if (!ctx) return;
            ctx.save();
            ctx.globalAlpha = this.alpha;
            
            if (this.isHeart) {
                ctx.translate(this.x, this.y);
                ctx.font = `${this.size * 5 + 8}px serif`;
                ctx.fillStyle = '#ff4d8d';
                ctx.textAlign = 'center';
                ctx.fillText('❤️', 0, 0);
            } else {
                ctx.fillStyle = '#ffb3d1';
                ctx.shadowBlur = 10;
                ctx.shadowColor = '#ff0055';
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
            ctx.restore();
        }
    }

    const particles = Array.from({ length: 60 }, () => new Particle());

    function animateParticles() {
        if (ctx) {
            ctx.clearRect(0, 0, window.innerWidth, window.innerHeight);
            particles.forEach(p => {
                p.update();
                p.draw();
            });
        }
        requestAnimationFrame(animateParticles);
    }
    animateParticles();

    // Burst particles function for scene transitions or YES celebration
    function createBurst(x, y, count = 40) {
        if (!ctx) return;
        for (let i = 0; i < count; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = Math.random() * 6 + 2;
            const p = new Particle();
            p.x = x;
            p.y = y;
            p.speedX = Math.cos(angle) * speed;
            p.speedY = Math.sin(angle) * speed;
            p.isHeart = Math.random() < 0.35;
            particles.push(p);
            // remove extra particles after fadeout
            setTimeout(() => {
                const idx = particles.indexOf(p);
                if (idx > -1) particles.splice(idx, 1);
            }, 2500);
        }
    }

    // ==========================================
    // 3. SCENE NAVIGATION CONTROLLER
    // ==========================================
    function goToScene(targetScene) {
        const currentEl = document.getElementById(`scene-${currentScene}`);
        const nextEl = document.getElementById(`scene-${targetScene}`);

        if (currentEl) {
            currentEl.classList.remove('active');
            currentEl.classList.add('hidden');
        }

        setTimeout(() => {
            if (nextEl) {
                nextEl.classList.remove('hidden');
                nextEl.classList.add('active');
            }
            currentScene = targetScene;
            triggerSceneAnimations(targetScene);
        }, 500);
    }

    // Trigger line reveals & typing per scene
    function triggerSceneAnimations(sceneNum) {
        if (sceneNum === 1) initScene1();
        else if (sceneNum === 2) initScene2();
        else if (sceneNum === 3) initScene3();
        else if (sceneNum === 4) initScene4();
        else if (sceneNum === 5) initScene5();
        else if (sceneNum === 6) initScene6();
        else if (sceneNum === 8) initScene8();
        else if (sceneNum === 9) initScene9();
        else if (sceneNum === 10) initScene10();
    }

    // Delay helper
    const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

    // Typewriter Effect Function
    async function typeWriter(element, text, speed = 50) {
        element.textContent = '';
        for (let i = 0; i < text.length; i++) {
            element.textContent += text.charAt(i);
            await delay(speed);
        }
    }

    // ==========================================
    // SCENE 1 — HEY VENNEELA
    // ==========================================
    async function initScene1() {
        const line1 = document.getElementById('s1-line1');
        const line2 = document.getElementById('s1-line2');
        const line3 = document.getElementById('s1-line3');
        const btn = document.getElementById('s1-btn');

        await delay(600);
        await typeWriter(line1, `Hey ${herName}… 👀❤️`, 60);
        
        await delay(500);
        line2.textContent = "I have something important to tell you…";
        line2.classList.add('show');

        await delay(1200);
        line3.textContent = "But I don't know how to say it.";
        line3.classList.add('show');

        await delay(1000);
        btn.classList.add('visible');
    }

    document.getElementById('s1-btn').addEventListener('click', () => {
        createBurst(window.innerWidth / 2, window.innerHeight / 2, 25);
        goToScene(2);
    });

    // ==========================================
    // SCENE 2 — THE SUSPENSE
    // ==========================================
    async function initScene2() {
        const lines = document.querySelectorAll('#scene-2 .reveal-line');
        const btn = document.getElementById('s2-btn');

        for (let i = 0; i < lines.length; i++) {
            await delay(1100);
            lines[i].classList.add('show');
        }

        await delay(800);
        btn.classList.add('visible');
    }

    document.getElementById('s2-btn').addEventListener('click', () => {
        createBurst(window.innerWidth / 2, window.innerHeight / 2, 25);
        goToScene(3);
    });

    // ==========================================
    // SCENE 3 — THE FEELING
    // ==========================================
    async function initScene3() {
        s3Phase = 1;
        const phase1 = document.getElementById('feeling-phase-1');
        const phase2 = document.getElementById('feeling-phase-2');
        const btn = document.getElementById('s3-btn');
        const btnText = document.getElementById('s3-btn-text');

        phase1.className = 'feeling-phase active-phase';
        phase2.className = 'feeling-phase hidden-phase';
        btn.classList.remove('visible');

        const lines = phase1.querySelectorAll('.card-line');
        for (let i = 0; i < lines.length; i++) {
            await delay(900);
            lines[i].classList.add('show');
        }

        await delay(800);
        btnText.textContent = "Continue ✨";
        btn.classList.add('visible');
    }

    document.getElementById('s3-btn').addEventListener('click', async () => {
        const btn = document.getElementById('s3-btn');
        const btnText = document.getElementById('s3-btn-text');
        const phase1 = document.getElementById('feeling-phase-1');
        const phase2 = document.getElementById('feeling-phase-2');

        if (s3Phase === 1) {
            s3Phase = 2;
            btn.classList.remove('visible');
            
            // Fade Phase 1
            phase1.classList.remove('active-phase');
            phase1.classList.add('hidden-phase');

            await delay(600);
            phase2.classList.remove('hidden-phase');
            phase2.classList.add('active-phase');

            const fadeIntro = phase2.querySelector('.fade-intro');
            const dramatic = phase2.querySelector('.card-dramatic-reveal');
            const fadeSub = phase2.querySelector('.fade-sub');

            await delay(400);
            fadeIntro.classList.add('show');

            await delay(1200);
            dramatic.classList.add('show');
            createBurst(window.innerWidth / 2, window.innerHeight / 2, 30);

            await delay(1000);
            fadeSub.classList.add('show');

            await delay(800);
            btnText.textContent = "There's more… 🥹";
            btn.classList.add('visible');
        } else {
            goToScene(4);
        }
    });

    // ==========================================
    // SCENE 4 — THE HEARTBEAT
    // ==========================================
    async function initScene4() {
        const lines = document.querySelectorAll('#scene-4 .heartbeat-line');
        const btn = document.getElementById('s4-btn');

        for (let i = 0; i < lines.length; i++) {
            await delay(1000);
            lines[i].classList.add('show');
        }

        await delay(800);
        btn.classList.add('visible');
    }

    document.getElementById('s4-btn').addEventListener('click', () => {
        const beatingHeart = document.getElementById('beatingHeart');
        beatingHeart.classList.add('expanding');
        createBurst(window.innerWidth / 2, window.innerHeight / 2, 50);

        setTimeout(() => {
            goToScene(5);
            setTimeout(() => beatingHeart.classList.remove('expanding'), 1000);
        }, 800);
    });

    // ==========================================
    // SCENE 5 — THE LOVE CONFESSION
    // ==========================================
    async function initScene5() {
        const nameEl = document.querySelector('.confession-name');
        const titleEl = document.querySelector('.confession-bold-title');
        const lines = document.querySelectorAll('#scene-5 .confession-sub');
        const bgHeart = document.querySelector('.confession-bg-heart');
        const btn = document.getElementById('s5-btn');

        await delay(600);
        nameEl.classList.add('show');

        await delay(900);
        titleEl.classList.add('show');
        bgHeart.classList.add('brighten');
        createBurst(window.innerWidth / 2, window.innerHeight / 2, 35);

        for (let i = 0; i < lines.length; i++) {
            await delay(1200);
            lines[i].classList.add('show');
        }

        await delay(1000);
        btn.classList.add('visible');
    }

    document.getElementById('s5-btn').addEventListener('click', () => {
        createBurst(window.innerWidth / 2, window.innerHeight / 2, 25);
        goToScene(6);
    });

    // ==========================================
    // SCENE 6 & 7 — THE PROPOSAL & RUNAWAY NO BUTTON
    // ==========================================
    async function initScene6() {
        noAttemptCount = 0;
        isNoDodging = false;
        
        const lines = document.querySelectorAll('#scene-6 .prop-line');
        const qBox = document.querySelector('.question-reveal-box');
        const yesBtn = document.getElementById('yesBtn');
        const noBtn = document.getElementById('noBtn');
        const toast = document.getElementById('noToast');

        // Reset positions
        noBtn.style.transform = 'none';
        noBtn.style.position = 'relative';
        noBtn.style.left = '0px';
        noBtn.style.top = '0px';
        noBtn.querySelector('span').textContent = 'NO 🙈';
        yesBtn.style.transform = 'none';
        yesBtn.querySelector('span').textContent = 'YES ❤️';
        toast.classList.add('hidden');

        for (let i = 0; i < lines.length; i++) {
            await delay(1000);
            lines[i].classList.add('show');
        }

        await delay(1200);
        qBox.classList.add('show');
        createBurst(window.innerWidth / 2, window.innerHeight / 2, 40);

        // Enable Dodge Proximity Detection
        setupNoButtonDodge();
    }

    // RUNAWAY NO BUTTON MOUSE PROXIMITY DODGE ENGINE
    function setupNoButtonDodge() {
        const noBtn = document.getElementById('noBtn');
        const yesBtn = document.getElementById('yesBtn');
        const toast = document.getElementById('noToast');
        const container = document.getElementById('proposalActionArea');

        if (!noBtn || !container) return;

        function dodgeNoButton(e) {
            if (currentScene !== 6) return;

            const rect = noBtn.getBoundingClientRect();
            const btnCenterX = rect.left + rect.width / 2;
            const btnCenterY = rect.top + rect.height / 2;

            const clientX = e.clientX || (e.touches && e.touches[0] ? e.touches[0].clientX : mouseX);
            const clientY = e.clientY || (e.touches && e.touches[0] ? e.touches[0].clientY : mouseY);

            const dist = Math.hypot(clientX - btnCenterX, clientY - btnCenterY);
            const threshold = 125; // 125px detection range

            if (dist < threshold && !isNoDodging) {
                isNoDodging = true;
                noAttemptCount++;

                // Container bounds for safe movement
                const containerRect = container.getBoundingClientRect();
                const yesRect = yesBtn.getBoundingClientRect();

                const padding = 20;
                const maxX = containerRect.width - rect.width - padding;
                const maxY = containerRect.height - rect.height - padding;

                let randomX, randomY, distanceToYes;
                let attempts = 0;

                // Pick random safe position avoiding YES button overlay
                do {
                    randomX = Math.random() * (maxX - padding) + padding - containerRect.width / 2 + rect.width / 2;
                    randomY = (Math.random() - 0.5) * 80;

                    // Calculate proposed distance to YES button
                    const targetAbsoluteX = containerRect.left + containerRect.width / 2 + randomX;
                    const targetAbsoluteY = containerRect.top + containerRect.height / 2 + randomY;
                    distanceToYes = Math.hypot(targetAbsoluteX - (yesRect.left + yesRect.width / 2), targetAbsoluteY - (yesRect.top + yesRect.height / 2));
                    attempts++;
                } while (distanceToYes < 120 && attempts < 20);

                const randomAngle = (Math.random() - 0.5) * 24; // -12deg to +12deg rotation

                // Apply spring physics transform
                noBtn.style.position = 'relative';
                noBtn.style.transition = 'transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1)';
                noBtn.style.transform = `translate(${randomX}px, ${randomY}px) rotate(${randomAngle}deg)`;

                // Update reaction message toast
                const reactions = CONFIG.NO_REACTIONS || [
                    "Are you sure? 🥺",
                    "Vennela… really? 😭❤️",
                    "Think again… ❤️",
                    "Pleaseee 🥹"
                ];

                const messageIdx = Math.min(noAttemptCount - 1, reactions.length - 1);
                toast.textContent = reactions[messageIdx];
                toast.classList.remove('hidden');
                toast.classList.add('show');

                // Special handling for Attempt 8+
                if (noAttemptCount >= 8) {
                    noBtn.style.transform += ' scale(0.8)';
                    noBtn.querySelector('span').textContent = 'no 🥺';
                    yesBtn.style.transform = 'scale(1.15)';
                    yesBtn.querySelector('span').textContent = 'YES ❤️ (Maybe this one? ❤️)';
                }

                setTimeout(() => {
                    isNoDodging = false;
                }, 400);
            }
        }

        window.removeEventListener('mousemove', dodgeNoButton);
        window.addEventListener('mousemove', dodgeNoButton);
        noBtn.addEventListener('touchstart', dodgeNoButton, { passive: true });
        noBtn.addEventListener('click', (e) => {
            e.preventDefault();
            dodgeNoButton({ clientX: mouseX, clientY: mouseY });
        });
    }

    // YES BUTTON CLICK HANDLER — CELEBRATION TRIGGER
    document.getElementById('yesBtn').addEventListener('click', () => {
        // Disable NO button & dodging
        isNoDodging = true;
        document.body.classList.add('shake');
        setTimeout(() => document.body.classList.remove('shake'), 600);

        // Confetti Heart Explosion
        if (typeof confetti === 'function') {
            confetti({
                particleCount: 120,
                spread: 90,
                origin: { y: 0.6 },
                colors: ['#ff0055', '#ff4d8d', '#ffffff', '#ffe0b2'],
                shapes: ['heart', 'circle']
            });

            setTimeout(() => {
                confetti({
                    particleCount: 80,
                    angle: 60,
                    spread: 55,
                    origin: { x: 0 },
                    colors: ['#ff0055', '#ff4d8d', '#ffffff']
                });
                confetti({
                    particleCount: 80,
                    angle: 120,
                    spread: 55,
                    origin: { x: 1 },
                    colors: ['#ff0055', '#ff4d8d', '#ffffff']
                });
            }, 300);
        }

        createBurst(window.innerWidth / 2, window.innerHeight / 2, 80);

        setTimeout(() => {
            goToScene(8);
        }, 500);
    });

    // ==========================================
    // SCENE 8 — YES CELEBRATION
    // ==========================================
    async function initScene8() {
        const lines = document.querySelectorAll('#scene-8 .celeb-line');
        const btn = document.getElementById('s8-btn');

        createBurst(window.innerWidth / 2, window.innerHeight / 3, 50);

        for (let i = 0; i < lines.length; i++) {
            await delay(900);
            lines[i].style.opacity = '1';
        }
    }

    document.getElementById('s8-btn').addEventListener('click', () => {
        createBurst(window.innerWidth / 2, window.innerHeight / 2, 30);
        goToScene(9);
    });

    // ==========================================
    // SCENE 9 — FROM AKASH (ROMANTIC LETTER)
    // ==========================================
    function initScene9() {
        const letterBody = document.getElementById('letterBody');
        const messageText = CONFIG.PERSONAL_MESSAGE || `Vennela,

I don't know how to explain everything I feel, but I know one thing for sure — I love you.

You are incredibly special to me, and I want to be there for the beautiful moments, the difficult moments, the laughter, and everything in between.

I don't know exactly what the future holds, but I know I want you to be a part of it. ❤️

Thank you for giving my heart a chance.`;

        letterBody.textContent = messageText;
    }

    document.getElementById('s9-btn').addEventListener('click', () => {
        createBurst(window.innerWidth / 2, window.innerHeight / 2, 30);
        goToScene(10);
    });

    // ==========================================
    // SCENE 10 — FINAL SCREEN
    // ==========================================
    function initScene10() {
        // Continuous gentle particle floating
        setInterval(() => {
            if (currentScene === 10) {
                createBurst(Math.random() * window.innerWidth, window.innerHeight, 2);
            }
        }, 600);
    }

    // Start Scene 1 on load
    initScene1();

});
