// Hockey Rink Diagram Drawing System
class RinkDiagram {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.options = {
            width: 400,
            height: 200,
            ...options
        };
        
        this.setupCanvas();
        this.drawRink();
    }
    
    setupCanvas() {
        this.canvas.width = this.options.width;
        this.canvas.height = this.options.height;
        this.ctx.strokeStyle = '#000';
        this.ctx.fillStyle = '#000';
        this.ctx.lineWidth = 2;
    }
    
    drawRink() {
        // Main rink outline
        this.ctx.strokeRect(0, 0, this.options.width, this.options.height);
        
        // Center line
        this.ctx.beginPath();
        this.ctx.moveTo(this.options.width / 2, 0);
        this.ctx.lineTo(this.options.width / 2, this.options.height);
        this.ctx.stroke();
        
        // Blue lines
        this.ctx.beginPath();
        this.ctx.moveTo(this.options.width / 3, 0);
        this.ctx.lineTo(this.options.width / 3, this.options.height);
        this.ctx.stroke();
        
        this.ctx.beginPath();
        this.ctx.moveTo((this.options.width / 3) * 2, 0);
        this.ctx.lineTo((this.options.width / 3) * 2, this.options.height);
        this.ctx.stroke();
        
        // Center face-off circle
        this.ctx.beginPath();
        this.ctx.arc(this.options.width / 2, this.options.height / 2, 15, 0, 2 * Math.PI);
        this.ctx.stroke();
        
        // Face-off dots
        this.drawFaceoffDot(this.options.width / 6, this.options.height / 4);
        this.drawFaceoffDot(this.options.width / 6, (this.options.height / 4) * 3);
        this.drawFaceoffDot((this.options.width / 6) * 5, this.options.height / 4);
        this.drawFaceoffDot((this.options.width / 6) * 5, (this.options.height / 4) * 3);
        
        // Goal creases
        this.drawGoalCrease(0, this.options.height / 2);
        this.drawGoalCrease(this.options.width, this.options.height / 2);
    }
    
    drawFaceoffDot(x, y) {
        this.ctx.beginPath();
        this.ctx.arc(x, y, 3, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    drawGoalCrease(x, y) {
        const creaseWidth = 20;
        const creaseHeight = 15;
        
        if (x === 0) {
            // Left goal
            this.ctx.beginPath();
            this.ctx.arc(x + creaseHeight, y, creaseHeight, Math.PI / 2, -Math.PI / 2);
            this.ctx.lineTo(x + creaseHeight + creaseWidth, y - creaseHeight);
            this.ctx.lineTo(x + creaseHeight + creaseWidth, y + creaseHeight);
            this.ctx.closePath();
        } else {
            // Right goal
            this.ctx.beginPath();
            this.ctx.arc(x - creaseHeight, y, creaseHeight, -Math.PI / 2, Math.PI / 2);
            this.ctx.lineTo(x - creaseHeight - creaseWidth, y - creaseHeight);
            this.ctx.lineTo(x - creaseHeight - creaseWidth, y + creaseHeight);
            this.ctx.closePath();
        }
        this.ctx.stroke();
    }
    
    drawPlayer(x, y, options = {}) {
        const defaultOptions = {
            color: '#007bff',
            size: 12,
            label: '',
            number: ''
        };
        
        const opts = { ...defaultOptions, ...options };
        
        // Player circle
        this.ctx.fillStyle = opts.color;
        this.ctx.beginPath();
        this.ctx.arc(x, y, opts.size, 0, 2 * Math.PI);
        this.ctx.fill();
        
        // Player label
        if (opts.label) {
            this.ctx.fillStyle = '#fff';
            this.ctx.font = '10px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(opts.label, x, y + 3);
        }
        
        // Player number
        if (opts.number) {
            this.ctx.fillStyle = '#fff';
            this.ctx.font = '8px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(opts.number, x, y + 15);
        }
    }
    
    drawPuck(x, y) {
        this.ctx.fillStyle = '#000';
        this.ctx.beginPath();
        this.ctx.arc(x, y, 4, 0, 2 * Math.PI);
        this.ctx.fill();
    }
    
    drawCone(x, y) {
        this.ctx.fillStyle = '#ffc107';
        this.ctx.beginPath();
        this.ctx.moveTo(x, y - 8);
        this.ctx.lineTo(x - 6, y + 8);
        this.ctx.lineTo(x + 6, y + 8);
        this.ctx.closePath();
        this.ctx.fill();
        this.ctx.stroke();
    }
    
    drawArrow(startX, startY, endX, endY, options = {}) {
        const defaultOptions = {
            color: '#dc3545',
            width: 2,
            arrowSize: 8
        };
        
        const opts = { ...defaultOptions, ...options };
        
        this.ctx.strokeStyle = opts.color;
        this.ctx.lineWidth = opts.width;
        
        // Draw line
        this.ctx.beginPath();
        this.ctx.moveTo(startX, startY);
        this.ctx.lineTo(endX, endY);
        this.ctx.stroke();
        
        // Draw arrowhead
        const angle = Math.atan2(endY - startY, endX - startX);
        const arrowLength = opts.arrowSize;
        
        this.ctx.beginPath();
        this.ctx.moveTo(endX, endY);
        this.ctx.lineTo(
            endX - arrowLength * Math.cos(angle - Math.PI / 6),
            endY - arrowLength * Math.sin(angle - Math.PI / 6)
        );
        this.ctx.moveTo(endX, endY);
        this.ctx.lineTo(
            endX - arrowLength * Math.cos(angle + Math.PI / 6),
            endY - arrowLength * Math.sin(angle + Math.PI / 6)
        );
        this.ctx.stroke();
    }
    
    drawMovementPath(points, options = {}) {
        const defaultOptions = {
            color: '#28a745',
            width: 2,
            style: 'solid' // solid, dashed, dotted
        };
        
        const opts = { ...defaultOptions, ...options };
        
        this.ctx.strokeStyle = opts.color;
        this.ctx.lineWidth = opts.width;
        
        if (opts.style === 'dashed') {
            this.ctx.setLineDash([5, 5]);
        } else if (opts.style === 'dotted') {
            this.ctx.setLineDash([2, 2]);
        } else {
            this.ctx.setLineDash([]);
        }
        
        this.ctx.beginPath();
        this.ctx.moveTo(points[0].x, points[0].y);
        
        for (let i = 1; i < points.length; i++) {
            this.ctx.lineTo(points[i].x, points[i].y);
        }
        
        this.ctx.stroke();
        this.ctx.setLineDash([]); // Reset line dash
    }
    
    clear() {
        this.ctx.clearRect(0, 0, this.options.width, this.options.height);
        this.drawRink();
    }
}

// Predefined drill patterns
const DrillPatterns = {
    warmUp: (rink) => {
        // Players in corners with movement to center
        rink.drawPlayer(50, 50, { color: '#007bff', label: 'P1' });
        rink.drawPlayer(350, 50, { color: '#007bff', label: 'P2' });
        rink.drawPlayer(50, 150, { color: '#007bff', label: 'P3' });
        rink.drawPlayer(350, 150, { color: '#007bff', label: 'P4' });
        
        // Movement arrows to center
        rink.drawArrow(50, 50, 200, 100, { color: '#28a745' });
        rink.drawArrow(350, 50, 200, 100, { color: '#28a745' });
        rink.drawArrow(50, 150, 200, 100, { color: '#28a745' });
        rink.drawArrow(350, 150, 200, 100, { color: '#28a745' });
        
        // Center gathering area
        rink.drawPuck(200, 100);
        rink.drawPuck(210, 95);
        rink.drawPuck(190, 105);
    },
    
    skillStations: (rink) => {
        // Figure 8 pattern
        rink.drawPlayer(100, 100, { color: '#28a745', label: 'P1' });
        rink.drawPlayer(300, 100, { color: '#28a745', label: 'P2' });
        
        // Figure 8 movement paths
        rink.drawMovementPath([
            { x: 100, y: 100 },
            { x: 150, y: 80 },
            { x: 200, y: 100 },
            { x: 150, y: 120 },
            { x: 100, y: 100 }
        ], { style: 'dashed' });
        
        rink.drawMovementPath([
            { x: 300, y: 100 },
            { x: 250, y: 80 },
            { x: 200, y: 100 },
            { x: 250, y: 120 },
            { x: 300, y: 100 }
        ], { style: 'dashed' });
        
        // Pucks for stickhandling
        rink.drawPuck(150, 80);
        rink.drawPuck(150, 120);
        rink.drawPuck(250, 80);
        rink.drawPuck(250, 120);
    },
    
    shootout: (rink) => {
        // Two lines at blue line
        rink.drawPlayer(133, 80, { color: '#dc3545', label: 'P1' });
        rink.drawPlayer(133, 120, { color: '#dc3545', label: 'P2' });
        rink.drawPlayer(267, 80, { color: '#dc3545', label: 'P3' });
        rink.drawPlayer(267, 120, { color: '#dc3545', label: 'P4' });
        
        // Goals
        rink.drawGoalCrease(0, 100);
        rink.drawGoalCrease(400, 100);
        
        // Movement arrows
        rink.drawArrow(133, 80, 50, 100, { color: '#dc3545' });
        rink.drawArrow(133, 120, 50, 100, { color: '#dc3545' });
        rink.drawArrow(267, 80, 350, 100, { color: '#dc3545' });
        rink.drawArrow(267, 120, 350, 100, { color: '#dc3545' });
        
        // Puck
        rink.drawPuck(133, 80);
    },
    
    scrimmage: (rink) => {
        // 3v3 setup in each end
        // Top end
        rink.drawPlayer(100, 60, { color: '#007bff', label: 'B1' });
        rink.drawPlayer(150, 60, { color: '#007bff', label: 'B2' });
        rink.drawPlayer(200, 60, { color: '#007bff', label: 'B3' });
        
        rink.drawPlayer(100, 40, { color: '#dc3545', label: 'R1' });
        rink.drawPlayer(150, 40, { color: '#dc3545', label: 'R2' });
        rink.drawPlayer(200, 40, { color: '#dc3545', label: 'R3' });
        
        // Bottom end
        rink.drawPlayer(100, 140, { color: '#007bff', label: 'B4' });
        rink.drawPlayer(150, 140, { color: '#007bff', label: 'B5' });
        rink.drawPlayer(200, 140, { color: '#007bff', label: 'B6' });
        
        rink.drawPlayer(100, 160, { color: '#dc3545', label: 'R4' });
        rink.drawPlayer(150, 160, { color: '#dc3545', label: 'R5' });
        rink.drawPlayer(200, 160, { color: '#dc3545', label: 'R6' });
        
        // Goals
        rink.drawGoalCrease(0, 100);
        rink.drawGoalCrease(400, 100);
        
        // Cones for boundaries
        rink.drawCone(80, 50);
        rink.drawCone(320, 50);
        rink.drawCone(80, 150);
        rink.drawCone(320, 150);
        
        // Pucks
        rink.drawPuck(150, 50);
        rink.drawPuck(150, 150);
    }
};

// Initialize rink diagrams when page loads
document.addEventListener('DOMContentLoaded', function() {
    const rinkElements = document.querySelectorAll('.rink-diagram');
    
    rinkElements.forEach((element, index) => {
        // Create canvas element
        const canvas = document.createElement('canvas');
        canvas.id = `rink-canvas-${index}`;
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        element.appendChild(canvas);
        
        // Initialize rink diagram
        const rink = new RinkDiagram(`rink-canvas-${index}`);
        
        // Draw appropriate pattern based on section
        const section = element.closest('.activity-section');
        if (section) {
            const header = section.querySelector('.activity-header');
            if (header) {
                const headerText = header.textContent.toLowerCase();
                if (headerText.includes('warm')) {
                    DrillPatterns.warmUp(rink);
                } else if (headerText.includes('skill')) {
                    DrillPatterns.skillStations(rink);
                } else if (headerText.includes('cool')) {
                    DrillPatterns.warmUp(rink); // Similar pattern for cool down
                }
            }
        }
    });
});
