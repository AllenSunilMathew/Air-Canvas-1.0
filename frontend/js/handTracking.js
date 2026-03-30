/**
 * HandTracking.js - MediaPipe Hand Tracking Module
 * Uses MediaPipe Hands for real-time hand detection and landmark tracking
 */

class HandTracking {
  constructor(video, canvas) {
    this.video = video;
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.hands = null;
    this.isRunning = false;
    this.onResultsCallback = null;
    this.lastProcessingTime = 0;
    this.frameSkip = 3;  // Throttled to ~15 FPS (60/3=20, conservative for perf)

    this.frameCount = 0;
    this.animationId = null;
  }

  /**
   * Initialize MediaPipe Hands
   */
  async initialize() {
    console.log('Loading MediaPipe scripts...');
    
    // Load MediaPipe scripts
    await this.loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js');
    await this.loadScript('https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js');
    
    console.log('Scripts loaded, initializing Hands...');
    console.log('Hands available:', typeof Hands !== 'undefined');
    console.log('Camera available:', typeof Camera !== 'undefined');
    
    // Check if Hands is available
    if (typeof Hands === 'undefined') {
      throw new Error('MediaPipe Hands not loaded');
    }
    
    this.hands = new Hands({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
      }
    });

    this.hands.setOptions({
      maxNumHands: 1,
      modelComplexity: 1,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5,
      staticImageMode: false
    });

    this.hands.onResults((results) => this.onResults(results));

    console.log('HandTracking initialized successfully');
  }

  /**
   * Load a script dynamically
   */
  loadScript(src) {
    return new Promise((resolve, reject) => {
      // Check if already loaded
      if (document.querySelector(`script[src="${src}"]`)) {
        resolve();
        return;
      }

      const script = document.createElement('script');
      script.src = src;
      script.onload = () => {
        console.log('Loaded:', src);
        resolve();
      };
      script.onerror = (e) => {
        console.error('Failed to load:', src, e);
        reject(new Error('Failed to load ' + src));
      };
      document.head.appendChild(script);
    });
  }

  /**
   * Start the camera and hand tracking
   */
  async start() {
    if (this.isRunning) {
      console.log('Already running');
      return;
    }

    try {
      console.log('Requesting camera access...');
      
      // Request camera
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        }
      });

      console.log('Camera access granted');
      
      this.video.srcObject = stream;
      
      // Wait for video to load
      await new Promise((resolve) => {
        this.video.onloadedmetadata = () => {
          console.log('Video metadata loaded');
          this.video.play();
          resolve();
        };
      });

      // Wait a bit for video to be ready
      await new Promise(resolve => setTimeout(resolve, 500));

      // Start processing frames
      this.isRunning = true;
      this.processFrame();
      
      console.log('HandTracking started');
      
    } catch (error) {
      console.error('Error starting hand tracking:', error);
      this.isRunning = false;
      throw error;
    }
  }

  /**
   * Process video frames
   */
  async processFrame() {
    if (!this.isRunning) return;

    const now = performance.now();
    if (now - this.lastRAF < 1000/15) {  // Strict 15 FPS cap
      this.animationId = requestAnimationFrame(() => this.processFrame());
      return;
    }
    this.lastRAF = now;

    try {
      this.frameCount++;
      
      // Frame skipping for better performance
      if (this.frameCount % this.frameSkip === 0) {
        if (this.hands && this.video.readyState === 4) {
          await this.hands.send({ image: this.video });
        }
      }
      
      // Continue processing
      this.animationId = requestAnimationFrame(() => this.processFrame());
      
    } catch (error) {
      console.error('Error processing frame:', error);
      this.animationId = requestAnimationFrame(() => this.processFrame());
    }
  }


  /**
   * Stop hand tracking and camera
   */
  stop() {
    this.isRunning = false;
    
    if (this.animationId) {
      cancelAnimationFrame(this.animationId);
      this.animationId = null;
    }
    
    if (this.video.srcObject) {
      const tracks = this.video.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      this.video.srcObject = null;
    }
    
    console.log('HandTracking stopped');
  }

  /**
   * Handle MediaPipe results
   */
  onResults(results) {
    const currentTime = performance.now();
    this.lastProcessingTime = currentTime;

    // Clear canvas and draw video frame
    this.ctx.save();
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
    this.ctx.drawImage(results.image, 0, 0, this.canvas.width, this.canvas.height);
    this.ctx.restore();

    if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
      if (this.onResultsCallback) {
        this.onResultsCallback(results.multiHandLandmarks);
      }
    }
  }

  /**
   * Set callback for hand results
   */
  onResults(callback) {
    this.onResultsCallback = callback;
  }

  /**
   * Get processing performance info
   */
  getPerformanceInfo() {
    return {
      fps: 1000 / this.lastProcessingTime,
      lastProcessingTime: this.lastProcessingTime
    };
  }

  /**
   * Set frame skip for performance adjustment
   */
  setFrameSkip(skip) {
    this.frameSkip = Math.max(1, skip);
  }

  /**
   * Check if tracking is running
   */
  getIsRunning() {
    return this.isRunning;
  }
}

// Export for use in other modules
window.HandTracking = HandTracking;

