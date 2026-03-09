/**
 * GestureDetector.js - Hand Gesture Detection Module
 * Detects various hand gestures for drawing control
 */

class GestureDetector {
  constructor(width = 700, height = 500) {
    this.canvasWidth = width;
    this.canvasHeight = height;
    this.previousLandmarks = null;
    this.gestureHistory = [];
    this.maxHistory = 5;
    
    // Gesture thresholds
    this.PINCH_THRESHOLD = 0.05;
    this.MOVE_THRESHOLD = 0.02;
    this.STABILIZE_FRAMES = 3;
    this.stabilizeCount = 0;
    
    // Current state
    this.isDrawing = false;
    this.currentPosition = null;
    this.previousPosition = null;
  }

  /**
   * Process hand landmarks and detect gestures
   * @param {Array} landmarks - MediaPipe hand landmarks
   * @returns {Object} Gesture state
   */
  detect(landmarks) {
    if (!landmarks || landmarks.length < 21) {
      return this.getDefaultState();
    }

    // Get key finger landmarks
    const indexTip = landmarks[8];
    const indexMCP = landmarks[5];
    const thumbTip = landmarks[4];
    const thumbIP = landmarks[3];
    const middleTip = landmarks[12];
    const ringTip = landmarks[16];
    const pinkyTip = landmarks[20];
    
    // Calculate distances
    const pinchDistance = this.calculateDistance(indexTip, thumbTip);
    const indexStraight = this.checkFingerStraight(landmarks, 8);
    const otherFingersClosed = this.areOtherFingersClosed(landmarks);
    
    // Detect gesture
    let gesture = 'idle';
    
    // Drawing gesture: Index finger extended, thumb close to index
    if (pinchDistance < this.PINCH_THRESHOLD && indexStraight && otherFingersClosed) {
      gesture = 'drawing';
      this.stabilizeCount++;
    } else if (pinchDistance < this.PINCH_THRESHOLD * 1.5) {
      gesture = 'ready';
      this.stabilizeCount = 0;
    } else {
      gesture = 'idle';
      this.stabilizeCount = 0;
    }
    
    // Stabilize gesture detection
    if (this.stabilizeCount >= this.STABILIZE_FRAMES) {
      this.isDrawing = true;
    } else {
      this.isDrawing = false;
    }
    
    // Calculate position
    const currentPosition = {
      x: indexTip.x * this.canvasWidth,
      y: indexTip.y * this.canvasHeight,
      z: indexTip.z
    };
    
    // Check for significant movement
    const movement = this.previousPosition ? 
      this.calculateDistance(currentPosition, this.previousPosition) : 0;
    
    // Update state
    const state = {
      gesture: gesture,
      isDrawing: this.isDrawing,
      position: currentPosition,
      previousPosition: this.previousPosition,
      movement: movement,
      landmarks: landmarks,
      // Additional gesture info
      pinchStrength: 1 - (pinchDistance / this.PINCH_THRESHOLD),
      fingerStates: {
        index: indexStraight,
        thumb: pinchDistance < this.PINCH_THRESHOLD,
        middle: !this.isFingerStraight(landmarks, 12),
        ring: !this.isFingerStraight(landmarks, 16),
        pinky: !this.isFingerStraight(landmarks, 20)
      }
    };
    
    // Update history
    this.gestureHistory.push(gesture);
    if (this.gestureHistory.length > this.maxHistory) {
      this.gestureHistory.shift();
    }
    
    // Update previous position
    this.previousPosition = currentPosition;
    this.previousLandmarks = landmarks;
    
    return state;
  }

  /**
   * Calculate distance between two points
   */
  calculateDistance(point1, point2) {
    return Math.sqrt(
      Math.pow(point1.x - point2.x, 2) +
      Math.pow(point1.y - point2.y, 2) +
      Math.pow(point1.z - point2.z, 2)
    );
  }

  /**
   * Check if finger is straight (extended)
   */
  checkFingerStraight(landmarks, tipIndex = 8) {
    const tip = landmarks[tipIndex];
    const mcp = landmarks[tipIndex - 3];
    const pip = landmarks[tipIndex - 2];
    
    // Check if finger is extended (tip is above pip which is above mcp)
    const extended = tip.y < pip.y && pip.y < mcp.y;
    return extended;
  }

  /**
   * Check if index finger is straight (extended) - alias for compatibility
   */
  isFingerStraight(landmarks, tipIndex = 8) {
    return this.checkFingerStraight(landmarks, tipIndex);
  }

  /**
   * Check if other fingers are closed (not extended)
   */
  areOtherFingersClosed(landmarks) {
    const middle = landmarks[12];
    const ring = landmarks[16];
    const pinky = landmarks[20];
    const indexTip = landmarks[8];
    
    // Other fingers should be below or at same level as index finger tip
    return middle.y > indexTip.y && ring.y > indexTip.y && pinky.y > indexTip.y;
  }

  /**
   * Get default gesture state
   */
  getDefaultState() {
    return {
      gesture: 'idle',
      isDrawing: false,
      position: null,
      previousPosition: null,
      movement: 0,
      landmarks: null,
      pinchStrength: 0,
      fingerStates: {
        index: false,
        thumb: false,
        middle: false,
        ring: false,
        pinky: false
      }
    };
  }

  /**
   * Reset gesture detector state
   */
  reset() {
    this.previousLandmarks = null;
    this.gestureHistory = [];
    this.isDrawing = false;
    this.currentPosition = null;
    this.previousPosition = null;
    this.stabilizeCount = 0;
  }

  /**
   * Get gesture history for smoothing
   */
  getGestureHistory() {
    return [...this.gestureHistory];
  }

  /**
   * Check if recent gestures are consistent
   */
  isGestureConsistent(gesture, minCount = 3) {
    const recent = this.gestureHistory.slice(-minCount);
    return recent.length >= minCount && recent.every(g => g === gesture);
  }

  /**
   * Get smoothed position using exponential moving average
   */
  getSmoothedPosition(currentPos, alpha = 0.3) {
    if (!this.smoothedPosition) {
      this.smoothedPosition = { ...currentPos };
      return this.smoothedPosition;
    }

    this.smoothedPosition.x = alpha * currentPos.x + (1 - alpha) * this.smoothedPosition.x;
    this.smoothedPosition.y = alpha * currentPos.y + (1 - alpha) * this.smoothedPosition.y;
    
    return this.smoothedPosition;
  }

  /**
   * Detect two-finger gestures for special actions
   */
  detectTwoFingerGesture(landmarks) {
    const indexTip = landmarks[8];
    const middleTip = landmarks[12];
    const distance = this.calculateDistance(indexTip, middleTip);
    
    // Two finger pinch for erase
    if (distance < 0.05) {
      return 'erase';
    }
    
    // Two finger spread for clear
    if (distance > 0.2) {
      return 'clear';
    }
    
    return null;
  }
}

// Export for use in other modules
window.GestureDetector = GestureDetector;

