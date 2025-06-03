import * as tf from "@tensorflow/tfjs";

// This utility file contains functions for detecting numbers in images

// Function to preprocess image tensor for model inference
export const preprocessImage = (imageTensor) => {
  // Use tf.tidy to automatically clean up intermediate tensors
  return tf.tidy(() => {
    // Convert to grayscale if the image is RGB
    let processedTensor = imageTensor;

    if (imageTensor.shape[2] === 3) {
      // RGB to grayscale conversion: 0.299 * R + 0.587 * G + 0.114 * B
      const redChannel = tf.slice(imageTensor, [0, 0, 0], [-1, -1, 1]);
      const greenChannel = tf.slice(imageTensor, [0, 0, 1], [-1, -1, 1]);
      const blueChannel = tf.slice(imageTensor, [0, 0, 2], [-1, -1, 1]);

      processedTensor = tf.add(
        tf.add(
          tf.mul(redChannel, tf.scalar(0.299)),
          tf.mul(greenChannel, tf.scalar(0.587))
        ),
        tf.mul(blueChannel, tf.scalar(0.114))
      );
    }

    // Normalize pixel values to the range [0, 1]
    return tf.div(processedTensor, tf.scalar(255.0));
  });
};

// In a real implementation, this would use a trained model to detect numbers
// For now, we'll create a simulation that mimics the detection of numbers
export const detectNumbers = async (imageTensor) => {
  // For demonstration purposes, we'll use a simulated detection
  // In a real app, you would:
  // 1. Use a trained model or OCR library to detect numbers
  // 2. Return the actual detected numbers with bounding boxes

  return simulateNumberDetection();
};

// Function to simulate number detection
// Returns array of objects with number, confidence and bounding box
const simulateNumberDetection = () => {
  // Number of detections (1-5)
  const count = Math.floor(Math.random() * 5) + 1;
  const detections = [];

  for (let i = 0; i < count; i++) {
    // Generate random number between 1-500
    const number = Math.floor(Math.random() * 500) + 1;

    // Generate random bounding box (normalized coordinates)
    // Format: [x, y, width, height] where x,y is top-left corner
    const x = Math.random() * 0.7; // Keep within reasonable screen bounds
    const y = Math.random() * 0.7;
    const width = Math.random() * 0.2 + 0.1; // Width between 10-30% of screen
    const height = Math.random() * 0.1 + 0.1; // Height between 10-20% of screen

    // Generate random confidence score between 0.7 and 1.0
    const confidence = Math.random() * 0.3 + 0.7;

    detections.push({
      number,
      confidence,
      bbox: [x, y, width, height],
    });
  }

  return detections;
};

// Function to track numbers across frames
// This would use some form of object tracking in a real implementation
export const trackNumbersAcrossFrames = (
  previousDetections,
  currentDetections
) => {
  // In a real implementation, this would:
  // 1. Match detections across frames using IOU (Intersection over Union)
  // 2. Assign consistent IDs to each tracked number
  // 3. Filter out spurious detections

  // For this simulation, we'll just return the current detections
  return currentDetections;
};

// Helper function to filter out duplicate or low-confidence detections
export const filterDetections = (detections, confidenceThreshold = 0.75) => {
  // Filter by confidence threshold
  const filteredByConfidence = detections.filter(
    (detection) => detection.confidence >= confidenceThreshold
  );

  // Sort by confidence (highest first)
  return filteredByConfidence.sort((a, b) => b.confidence - a.confidence);
};

// Find the detection with the highest number value
export const findHighestNumber = (detections) => {
  if (detections.length === 0) return null;

  return detections.reduce((highest, current) => {
    return current.number > highest.number ? current : highest;
  }, detections[0]);
};
