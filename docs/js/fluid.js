class FluidSimulation {
    constructor(canvas) {
        this.canvas = canvas;
        this.ctx = canvas.getContext('2d');
        this.particles = [];
        this.mouse = { x: null, y: null, radius: 100 };
        
        this.resize();
        window.addEventListener('resize', () => this.resize());
        canvas.addEventListener('mousemove', (e) => this.onMouseMove(e));
        
        this.initParticles();
        this.animate();
    }
    
    resize() {
        this.width = this.canvas.width = this.canvas.offsetWidth;
        this.height = this.canvas.height = this.canvas.offsetHeight;
        this.initParticles();
    }
    
    initParticles() {
        this.particles = [];
        const particleCount = Math.floor((this.width * this.height) / 10000);
        
        for (let i = 0; i < particleCount; i++) {
            const size = Math.random() * 2 + 1;
            this.particles.push({
                x: Math.random() * this.width,
                y: Math.random() * this.height,
                size: size,
                baseX: Math.random() * this.width,
                baseY: Math.random() * this.height,
                density: (Math.random() * 30) + 1,
                color: `hsla(${Math.random() * 60 + 200}, 90%, 70%, ${Math.random() * 0.6 + 0.3})`
            });
        }
    }
    
    onMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        this.mouse.x = e.clientX - rect.left;
        this.mouse.y = e.clientY - rect.top;
    }
    
    connect() {
        let opacity = 1;
        for (let a = 0; a < this.particles.length; a++) {
            for (let b = a; b < this.particles.length; b++) {
                const dx = this.particles[a].x - this.particles[b].x;
                const dy = this.particles[a].y - this.particles[b].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 100) {
                    opacity = 1 - (distance / 100);
                    this.ctx.strokeStyle = `rgba(255, 255, 255, ${opacity * 0.3})`;
                    this.ctx.lineWidth = 1;
                    this.ctx.beginPath();
                    this.ctx.moveTo(this.particles[a].x, this.particles[a].y);
                    this.ctx.lineTo(this.particles[b].x, this.particles[b].y);
                    this.ctx.stroke();
                }
            }
        }
    }
    
    updateParticles() {
        for (let i = 0; i < this.particles.length; i++) {
            const p = this.particles[i];
            
            // Move particle back to original position
            let dx = p.baseX - p.x;
            let dy = p.baseY - p.y;
            
            // Apply mouse influence
            if (this.mouse.x && this.mouse.y) {
                const mouseDx = this.mouse.x - p.x;
                const mouseDy = this.mouse.y - p.y;
                const mouseDist = Math.sqrt(mouseDx * mouseDx + mouseDy * mouseDy);
                const maxDist = 200;
                
                if (mouseDist < maxDist) {
                    const force = (1 - mouseDist / maxDist) * 2;
                    const angle = Math.atan2(mouseDy, mouseDx);
                    dx -= Math.cos(angle) * force * 20;
                    dy -= Math.sin(angle) * force * 20;
                }
            }
            
            // Apply movement with easing
            p.x += dx * 0.1;
            p.y += dy * 0.1;
            
            // Draw particle
            this.ctx.fillStyle = p.color;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.closePath();
            this.ctx.fill();
        }
    }
    
    animate() {
        this.ctx.clearRect(0, 0, this.width, this.height);
        this.ctx.fillStyle = 'rgba(13, 17, 23, 0.1)';
        this.ctx.fillRect(0, 0, this.width, this.height);
        
        this.connect();
        this.updateParticles();
        
        requestAnimationFrame(() => this.animate());
    }
}

// Store the fluid simulation instance
let fluidSimulation = null;

// Initialize when DOM is loaded
function initFluid() {
    const canvas = document.getElementById('fluid-canvas');
    if (canvas) {
        // Remove any existing instance
        if (fluidSimulation) {
            fluidSimulation = null;
        }
        
        // Set canvas dimensions
        const header = canvas.parentElement;
        canvas.width = header.offsetWidth;
        canvas.height = header.offsetHeight;
        
        // Create new simulation
        fluidSimulation = new FluidSimulation(canvas);
    }
}

// Handle window resize
function handleResize() {
    if (fluidSimulation) {
        const canvas = document.getElementById('fluid-canvas');
        if (canvas) {
            const header = canvas.parentElement;
            canvas.width = header.offsetWidth;
            canvas.height = header.offsetHeight;
        }
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Initialize fluid effect
    initFluid();
    
    // Handle window resize
    window.addEventListener('resize', handleResize);
    
    // Reinitialize fluid after page transition
    document.addEventListener('pageTransitionEnd', initFluid);
});

// Handle page navigation
document.addEventListener('click', (e) => {
    const link = e.target.closest('a');
    if (link && link.getAttribute('href') && !link.getAttribute('href').startsWith('#')) {
        // Allow default navigation
        return true;
    }
});
