/**
 * HandVisualizer.js - Hand Visualization Module
 * Visualizes hand landmarks and gestures on canvas
 */

class HandVisualizer {
  constructor(canvas, ctx) {
    this.canvas = canvas;
    this.ctx = ctx;
    this.showLandmarks = true;
    this.showConnections = true;
    this.showFingertips = true;
    this.landmarkColor = '#6c8cff';
    this.connectionColor = '#8fd3f4';
    this.fingertipColor = '#ff6b6b';
    this.landmarkRadius = 4;
    this.connectionWidth = 2;
    
    // Animation
    this.pulseEffect = false;
    this.pulseRadius = 0;
    this.maxPulseRadius = 20;
  }

  /**
   * Draw hand landmarks and connections
   * @param {Array} landmarks - MediaPipe hand landmarks
   */
  draw(landmarks) {
    if (!landmarks || landmarks.length < 21) return;

    this.ctx.save();
    
    // Apply pulse effect if active
    if (this.pulseEffect) {
      this.drawPulse(landmarks[8]);
    }

    // Draw connections (skeleton)
    if (this.showConnections) {
      this.drawConnections(landmarks);
    }

    // Draw landmarks
    if (this.showLandmarks) {
      this.drawLandmarks(landmarks);
    }

    // Draw fingertips
    if (this.showFingertips) {
      this.drawFingertips(landmarks);
    }

    // Draw index finger tip with highlight (drawing point)
    this.drawDrawingPoint(landmarks[8]);

    this.ctx.restore();
  }

  /**
   * Draw skeleton connections
   */
  drawConnections(landmarks) {
    const connections = [
      // Palm
      [0, 1], [1, 2], [2, 3], [3, 7],
      [0, 5], [5, 6], [6, 7],
      [0, 9], [9, 10], [10, 11],
      [0, 13], [13, 14], [14, 15],
      [0, 17], [17, 18], [18, 19],
      // Thumb
      [1, 4],
      // Index
      [5, 8],
      // Middle
      [9, 12],
      // Ring
      [13, 16],
      // Pinky
      [17, 20]
    ];

    this.ctx.strokeStyle = this.connectionColor;
    this.ctx.lineWidth = this.connectionWidth;
    this.ctx.lineCap = 'round';

    connections.forEach(([start, end]) => {
      const startPoint = landmarks[start];
      const endPoint = landmarks[end];
      
      this.ctx.beginPath();
      this.ctx.moveTo(
        startPoint.x * this.canvas.width,
        startPoint.y * this.canvas.height
      );
      this.ctx.lineTo(
        endPoint.x * this.canvas.width,
        endPoint.y * this.canvas.height
      );
      this.ctx.stroke();
    });
  }

  /**
   * Draw landmark points
   */
  drawLandmarks(landmarks) {
    landmarks.forEach((landmark, index) => {
      const x = landmark.x * this.canvas.width;
      const y = landmark.y * this.canvas.height;
      
      this.ctx.beginPath();
      this.ctx.arc(x, y, this.landmarkRadius, 0, Math.PI * 2);
      this.ctx.fillStyle = this.landmarkColor;
      this.ctx.fill();
      
      // Add slight glow
      this.ctx.beginPath();
      this.ctx.arc(x, y, this.landmarkRadius + 2, 0, Math.PI * 2);
      this.ctx.fillStyle = 'rgba(108, 140, 255, 0.3)';
      this.ctx.fill();
    });
  }

  /**
   * Draw fingertip highlights
   */
  drawFingertips(landmarks) {
    const fingertips = [4, 8, 12, 16, 20]; // Thumb, Index, Middle, Ring, Pinky
    
    fingertips.forEach(index => {
      const landmark = landmarks[index];
      const x = landmark.x * this.canvas.width;
      const y = landmark.y * this.canvas.height;
      
      this.ctx.beginPath();
      this.ctx.arc(x, y, this.landmarkRadius + 2, 0, Math.PI * 2);
      this.ctx.fillStyle = this.fingertipColor;
      this.ctx.fill();
    });
  }

  /**
   * Draw the main drawing point (index finger tip)
   */
  drawDrawingPoint(landmark) {
    const x = landmark.x * this.canvas.width;
    const y = landmark.y * this.canvas.height;
    
    // Outer glow
    const gradient = this.ctx.createRadialGradient(x, y, 0, x, y, 30);
    gradient.addColorStop(0, 'rgba(108, 140, 255, 0.4)');
    gradient.addColorStop(1, 'rgba(108, 140, 255, 0)');
    
    this.ctx.beginPath();
    this.ctx.arc(x, y, 30, 0, Math.PI * 2);
    this.ctx.fillStyle = gradient;
    this.ctx.fill();
    
    // Inner circle
    this.ctx.beginPath();
    this.ctx.arc(x, y, 8, 0, Math.PI * 2);
    this.ctx.fillStyle = this.landmarkColor;
    this.ctx.fill();
    this.ctx.strokeStyle = 'white';
    this.ctx.lineWidth = 2;
    this.ctx.stroke();
  }

  /**
   * Draw pulse effect
   */
  drawPulse(landmark) {
    const x = landmark.x * this.canvas.width;
    const y = landmark.y * this.canvas.height;
    
    this.pulseRadius += 1;
    if (this.pulseRadius > this.maxPulseRadius) {
      this.pulseRadius = 0;
    }

    const alpha = 1 - (this.pulseRadius / this.maxPulseRadius);
    
    this.ctx.beginPath();
    this.ctx.arc(x, y, 10 + this.pulseRadius, 0, Math.PI * 2);
    this.ctx.strokeStyle = `rgba(108, 140, 255, ${alpha})`;
    this.ctx.lineWidth = 2;
    this.ctx.stroke();
  }

  /**
   * Enable/disable features
   */
  setOptions(options) {
    if (options.showLandmarks !== undefined) this.showLandmarks = options.showLandmarks;
    if (options.showConnections !== undefined) this.showConnections = options.showConnections;
    if (options.showFingertips !== undefined) this.showFingertips = options.showFingertips;
    if (options.landmarkColor !== undefined) this.landmarkColor = options.landmarkColor;
    if (options.connectionColor !== undefined) this.connectionColor = options.connectionColor;
    if (options.pulseEffect !== undefined) this.pulseEffect = options.pulseEffect;
  }

  /**
   * Clear the visualizer
   */
  clear() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
  }

  /**
   * Draw gesture indicator
   */
  drawGestureIndicator(gesture, x, y) {
    this.ctx.save();
    this.ctx.font = '16px Segoe UI';
    this.ctx.fillStyle = '#333';
    this.ctx.textAlign = 'center';
    
    let text = '';
    let color = '#666';
    
    switch(gesture) {
      case 'drawing':
        text = '✏️ Drawing';
        color = '#4CAF50';
        break;
      case 'ready':
        text = '👌 Ready';
        color = '#FF9800';
        break;
      case 'idle':
        text = '✋ Idle';
        color = '#666';
        break;
      default:
        text = '';
    }
    
    if (text) {
      this.ctx.fillStyle = color;
      this.ctx.fillText(text, x, y);
    }
    
    this.ctx.restore();
  }
}

// Export for use in other modules
window.HandVisualizer = HandVisualizer;

