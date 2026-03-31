/**
 * DrawingCanvas.js - High-Performance Drawing Canvas Module
 * Uses PixiJS for smooth real-time drawing
 */

class DrawingCanvas {
  constructor(containerId, width = 700, height = 500) {
    this.containerId = containerId;
    this.width = width;
    this.height = height;
    this.app = null;
    this.graphics = null;
    this.currentColor = '#000000'; // Solid black for sketch lines
    this.brushSize = 6; // Slightly thicker to reduce pixelation appearance
    this.isEraser = false;
    this.previousPoint = null;
    this.isDrawing = false;
    
    // Sparkling properties
    this.sparkleEnabled = false; // Disabled for solid non-pixelated black lines
    this.sparkleTime = 0;
    this.sparkleIntensity = 0.8;
    

    
    // Smoothing
    this.smoothFactor = 0.5;
    this.lastPoints = [];
    this.maxPoints = 3;
  }

  /**
   * Initialize PixiJS canvas
   */
  async initialize() {
    // Load PixiJS dynamically
    await this.loadPixiJS();
    
    // Create PixiJS Application
    this.app = new PIXI.Application({
      width: this.width,
      height: this.height,
      backgroundColor: 0xFFFFFF,
      resolution: window.devicePixelRatio || 1,
      autoDensity: true,
      antialias: true
    });
    
    // Add canvas to container
    const container = document.getElementById(this.containerId);
    if (container) {
      container.appendChild(this.app.view);
    }
    
    // Create graphics layer for drawing
    this.graphics = new PIXI.Graphics();
    this.app.stage.addChild(this.graphics);
    
    // Create eraser graphics (using blend mode)
    this.eraserGraphics = new PIXI.Graphics();
    this.eraserGraphics.blendMode = PIXI.BLEND_MODES.ERASE;
    this.app.stage.addChild(this.eraserGraphics);
    
    // Sparkle animation ticker
    this.app.ticker.add((delta) => {
      this.sparkleTime += 0.1 * delta;
    });
    
    console.log('DrawingCanvas initialized with PixiJS');
    return this.app;
  }


  /**
   * Load PixiJS library dynamically
   */
  loadPixiJS() {
    return new Promise((resolve, reject) => {
      if (typeof PIXI !== 'undefined') {
        resolve();
        return;
      }
      
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/pixi.js@7.x/dist/pixi.min.js';
      script.onload = () => resolve();
      script.onerror = () => reject(new Error('Failed to load PixiJS'));
      document.head.appendChild(script);
    });
  }

  /**
   * Start drawing from a point
   */
  startDrawing(x, y) {
    this.isDrawing = true;
    this.previousPoint = { x, y };
    this.lastPoints = [{ x, y }];
  }

  /**
   * Continue drawing to a point
   */
  continueDrawing(x, y) {
    if (!this.isDrawing || !this.previousPoint) return;
    
    // Add point to history for smoothing
    this.lastPoints.push({ x, y });
    if (this.lastPoints.length > this.maxPoints) {
      this.lastPoints.shift();
    }
    
    // Get smoothed point
    const smoothedPoint = this.getSmoothedPoint(x, y);
    
    // Draw line
    this.drawLine(
      this.previousPoint.x,
      this.previousPoint.y,
      smoothedPoint.x,
      smoothedPoint.y
    );
    
    this.previousPoint = smoothedPoint;
  }

  /**
   * Stop drawing
   */
  stopDrawing() {
    this.isDrawing = false;
    this.previousPoint = null;
    this.lastPoints = [];
  }

  /**
   * Get smoothed point using moving average
   */
  getSmoothedPoint(x, y) {
    if (this.lastPoints.length < 2) {
      return { x, y };
    }
    
    let sumX = 0;
    let sumY = 0;
    
    this.lastPoints.forEach(point => {
      sumX += point.x;
      sumY += point.y;
    });
    
    return {
      x: sumX / this.lastPoints.length,
      y: sumY / this.lastPoints.length
    };
  }

  /**
   * Draw a line between two points
   */
  drawLine(x1, y1, x2, y2) {
    const targetGraphics = this.isEraser ? this.eraserGraphics : this.graphics;
    
    targetGraphics.lineStyle({
      width: this.brushSize,
      color: this.isEraser ? 0xFFFFFF : this.parseColor(this.currentColor),
      alpha: 1,
      cap: PIXI.LINE_CAP.ROUND,
      join: PIXI.LINE_JOIN.ROUND,
      native: false
    });
    
    targetGraphics.moveTo(x1, y1);
    targetGraphics.lineTo(x2, y2);
  }

  /**
   * Parse color string to hex
   */
  parseColor(color) {
    if (typeof color === 'number') return color;
    
    // Handle hex colors
    if (color.startsWith('#')) {
      return parseInt(color.slice(1), 16);
    }
    
    // Handle rgb colors
    const rgbMatch = color.match(/rgb\((\d+),\s*(\d+),\s*(\d+)\)/);
    if (rgbMatch) {
      return (parseInt(rgbMatch[1]) << 16) + 
             (parseInt(rgbMatch[2]) << 8) + 
             parseInt(rgbMatch[3]);
    }
    
    return 0x000000;
  }

  /**
   * Get current color for drawing (sparkle if enabled)
   */
  getSparkleColor() {
    if (!this.sparkleEnabled) {
      return this.parseColor(this.currentColor);
    }
    this.updateSparkleColor();
    return this.parseColor(this.currentColor);
  }

  /**
   * Update sparkling color animation
   */
  updateSparkleColor() {
    const time = this.sparkleTime;
    const hue = (200 + Math.sin(time) * 20 + 360) % 360;
    const s = 0.7 + Math.sin(time * 1.3) * 0.25;
    const l = 0.8 + Math.sin(time * 0.7) * 0.12;
    // HSL to RGB conversion
    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs((hue / 60) % 2 - 1));
    const m = l - c/2;
    let r=0, g=0, b=0;
    if (hue < 60) {r = c; g = x; b = 0;}
    else if (hue < 120) {r = x; g = c; b = 0;}
    else if (hue < 180) {r = 0; g = c; b = x;}
    else if (hue < 240) {r = 0; g = x; b = c;}
    else if (hue < 300) {r = x; g = 0; b = c;}
    else {r = c; g = 0; b = x;}
    r = Math.round((r + m) * 255);
    g = Math.round((g + m) * 255);
    b = Math.round((b + m) * 255);
    this.currentColor = `#${r.toString(16).padStart(2,'0')}${g.toString(16).padStart(2,'0')}${b.toString(16).padStart(2,'0')}`;
  }

  /**
   * Set brush color
   */
  setColor(color) {
    this.currentColor = color;
  }

  /**
   * Set brush size
   */
  setBrushSize(size) {
    this.brushSize = size;
  }

  /**
   * Enable/disable eraser
   */
  setEraser(enabled) {
    this.isEraser = enabled;
  }

  /**
   * Clear the canvas
   */
  clear() {
    this.graphics.clear();
    this.eraserGraphics.clear();
  }

  /**
   * Get canvas as image data URL
   */
  async toDataURL() {
    // Create a temporary canvas to render
    const renderer = this.app.renderer;
    const texture = renderer.generateTexture(this.graphics);
    
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = this.width;
    tempCanvas.height = this.height;
    const tempCtx = tempCanvas.getContext('2d');
    
    // Fill white background
    tempCtx.fillStyle = 'white';
    tempCtx.fillRect(0, 0, this.width, this.height);
    
    // Draw the PixiJS graphics
    const pixiCanvas = renderer.extract.canvas(this.app.stage);
    tempCtx.drawImage(pixiCanvas, 0, 0);
    
    return tempCanvas.toDataURL('image/png');
  }

  /**
   * Get canvas as blob
   */
  async toBlob() {
    const dataURL = await this.toDataURL();
    
    return new Promise((resolve) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = this.width;
        canvas.height = this.height;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = 'white';
        ctx.fillRect(0, 0, this.width, this.height);
        ctx.drawImage(img, 0, 0);
        canvas.toBlob(resolve, 'image/png');
      };
      img.src = dataURL;
    });
  }

  /**
   * Resize canvas
   */
  resize(width, height) {
    this.width = width;
    this.height = height;
    
    if (this.app) {
      this.app.renderer.resize(width, height);
    }
  }

  /**
   * Destroy the canvas
   */
  destroy() {
    if (this.app) {
      this.app.destroy(true, { children: true, texture: true });
    }
  }

  /**
   * Add touch/mouse event listeners
   */
  addEventListeners(canvasElement) {
    const getPosition = (e) => {
      const rect = canvasElement.getBoundingClientRect();
      const scaleX = this.width / rect.width;
      const scaleY = this.height / rect.height;
      
      if (e.touches) {
        return {
          x: (e.touches[0].clientX - rect.left) * scaleX,
          y: (e.touches[0].clientY - rect.top) * scaleY
        };
      }
      
      return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
      };
    };

    // Mouse events
    canvasElement.addEventListener('mousedown', (e) => {
      const pos = getPosition(e);
      this.startDrawing(pos.x, pos.y);
    });

    canvasElement.addEventListener('mousemove', (e) => {
      const pos = getPosition(e);
      this.continueDrawing(pos.x, pos.y);
    });

    canvasElement.addEventListener('mouseup', () => {
      this.stopDrawing();
    });

    canvasElement.addEventListener('mouseleave', () => {
      this.stopDrawing();
    });

    // Touch events
    canvasElement.addEventListener('touchstart', (e) => {
      e.preventDefault();
      const pos = getPosition(e);
      this.startDrawing(pos.x, pos.y);
    }, { passive: false });

    canvasElement.addEventListener('touchmove', (e) => {
      e.preventDefault();
      const pos = getPosition(e);
      this.continueDrawing(pos.x, pos.y);
    }, { passive: false });

    canvasElement.addEventListener('touchend', () => {
      this.stopDrawing();
    });
  }
}

// Export for use in other modules
window.DrawingCanvas = DrawingCanvas;

