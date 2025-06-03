import React, { useState, useEffect, useRef } from "react";
import {
  StyleSheet,
  Text,
  View,
  TouchableOpacity,
  Dimensions,
  Alert,
  ActivityIndicator,
} from "react-native";
import { Camera } from "expo-camera";
import * as tf from "@tensorflow/tfjs";
import { cameraWithTensors } from "@tensorflow/tfjs-react-native";
import * as FileSystem from "expo-file-system";

// Import our custom utilities and components
import NumberDetectionBox from "./NumberDetectionBox";
import {
  preprocessImage,
  detectNumbers,
  trackNumbersAcrossFrames,
  filterDetections,
  findHighestNumber,
} from "./numberDetectionUtil";

// Create TensorCamera from regular Camera
const TensorCamera = cameraWithTensors(Camera);

// Get screen dimensions
const { width, height } = Dimensions.get("window");

// Define tensor dimensions - use smaller resolution for better performance
const TENSOR_WIDTH = 200;
const TENSOR_HEIGHT = 200;

export default function NumberTracker() {
  const [hasPermission, setHasPermission] = useState(null);
  const [isTfReady, setIsTfReady] = useState(false);
  const [isModelReady, setIsModelReady] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [detections, setDetections] = useState([]);
  const [highestNumberDetection, setHighestNumberDetection] = useState(null);
  const [scannedBoxCount, setScannedBoxCount] = useState(0);
  const frameCount = useRef(0);
  const cameraRef = useRef(null);
  const rafRef = useRef(null);
  const previousDetectionsRef = useRef([]);

  // Initialize TensorFlow and request camera permissions
  useEffect(() => {
    (async () => {
      try {
        // Request camera permission
        const { status } = await Camera.requestCameraPermissionsAsync();
        setHasPermission(status === "granted");

        // Initialize TensorFlow - make sure await is used
        await tf.ready();
        setIsTfReady(true);
        console.log("TensorFlow ready");

        // In a real app, you would load a custom model here
        // For demo purposes, we'll just set it to ready after a delay
        await new Promise((resolve) => setTimeout(resolve, 1000));
        setIsModelReady(true);
      } catch (error) {
        console.error("Setup error:", error);
        Alert.alert("Error", "Failed to initialize camera or TensorFlow");
      }
    })();

    // Cleanup function
    return () => {
      if (rafRef.current) {
        cancelAnimationFrame(rafRef.current);
      }
      // Clean up TensorFlow memory properly
      try {
        if (tf && tf.dispose) {
          tf.dispose();
        }
      } catch (error) {
        console.error("TensorFlow cleanup error:", error);
      }
    };
  }, []);

  const handleCameraStream = (images) => {
    const loop = async () => {
      if (!isScanning) {
        rafRef.current = requestAnimationFrame(loop);
        return;
      }

      try {
        frameCount.current += 1;
        // Only process every 15th frame for better performance
        if (frameCount.current % 15 !== 0) {
          rafRef.current = requestAnimationFrame(loop);
          return;
        }

        const nextImageTensor = images.next().value;
        if (!nextImageTensor) {
          rafRef.current = requestAnimationFrame(loop);
          return;
        }

        // Use tf.tidy to automatically clean up intermediate tensors
        tf.tidy(() => {
          // Preprocess the image
          const processedTensor = preprocessImage(nextImageTensor);

          // Detect numbers (simulated in our case)
          detectNumbers(processedTensor).then((newDetections) => {
            // Track numbers across frames
            const trackedDetections = trackNumbersAcrossFrames(
              previousDetectionsRef.current,
              newDetections
            );

            // Filter and sort detections by confidence
            const filteredDetections = filterDetections(trackedDetections);

            // Update state
            if (filteredDetections.length > 0) {
              setDetections(filteredDetections);

              // Find the highest number
              const highest = findHighestNumber(filteredDetections);
              setHighestNumberDetection(highest);

              // Update the number of boxes scanned
              setScannedBoxCount((prev) => prev + 1);

              // Save current detections for next frame
              previousDetectionsRef.current = filteredDetections;
            }
          });
        });

        // Dispose of the camera tensor explicitly
        tf.dispose(nextImageTensor);
      } catch (error) {
        console.error("Detection error:", error);
      }

      rafRef.current = requestAnimationFrame(loop);
    };

    loop();
  };

  const toggleScanning = () => {
    if (!isScanning) {
      // Reset state when starting a new scan
      setDetections([]);
      setHighestNumberDetection(null);
      setScannedBoxCount(0);
      previousDetectionsRef.current = [];
    }
    setIsScanning(!isScanning);
  };

  const captureHighestNumber = async () => {
    if (!highestNumberDetection) {
      Alert.alert("No numbers detected", "Keep scanning to find numbers");
      return;
    }

    Alert.alert(
      "Highest Number Found!",
      `The highest number detected is ${
        highestNumberDetection.number
      } with ${Math.round(
        highestNumberDetection.confidence * 100
      )}% confidence.`,
      [{ text: "OK" }]
    );
  };

  if (hasPermission === null) {
    return (
      <View style={styles.container}>
        <Text style={styles.statusText}>Requesting camera permission...</Text>
      </View>
    );
  }

  if (hasPermission === false) {
    return (
      <View style={styles.container}>
        <Text style={styles.statusText}>No access to camera</Text>
      </View>
    );
  }

  if (!isTfReady || !isModelReady) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.statusText}>Loading resources...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {Camera && TensorCamera ? (
        <TensorCamera
          ref={cameraRef}
          style={styles.camera}
          type={Camera.Constants.Type.back}
          onReady={handleCameraStream}
          resizeHeight={TENSOR_HEIGHT}
          resizeWidth={TENSOR_WIDTH}
          resizeDepth={3}
          autorender={true}
          useCustomShadersToResize={false}
        />
      ) : (
        <View
          style={[
            styles.camera,
            {
              backgroundColor: "#333",
              justifyContent: "center",
              alignItems: "center",
            },
          ]}
        >
          <Text style={styles.statusText}>Camera not available</Text>
        </View>
      )}

      {/* Render detection boxes for all detected numbers */}
      {detections.map((detection, index) => (
        <NumberDetectionBox
          key={`detection-${index}`}
          detectedNumber={detection.number}
          bbox={detection.bbox}
          isHighest={
            highestNumberDetection &&
            detection.number === highestNumberDetection.number
          }
        />
      ))}

      <View style={styles.overlay}>
        <View style={styles.infoContainer}>
          <Text style={styles.infoText}>Scanning for numbers 1-500...</Text>
          <Text style={styles.infoText}>Boxes Scanned: {scannedBoxCount}</Text>
          {highestNumberDetection && (
            <Text style={styles.highestText}>
              Highest: {highestNumberDetection.number}
            </Text>
          )}
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={[
              styles.button,
              isScanning ? styles.buttonStop : styles.buttonStart,
            ]}
            onPress={toggleScanning}
          >
            <Text style={styles.buttonText}>
              {isScanning ? "Stop Scanning" : "Start Scanning"}
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.button,
              styles.captureButton,
              !highestNumberDetection ? styles.buttonDisabled : null,
            ]}
            onPress={captureHighestNumber}
            disabled={!highestNumberDetection}
          >
            <Text style={styles.buttonText}>Capture Highest</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "black",
  },
  statusText: {
    color: "white",
    fontSize: 18,
    textAlign: "center",
    marginTop: 20,
  },
  camera: {
    flex: 1,
    width: "100%",
  },
  overlay: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    padding: 20,
    backgroundColor: "rgba(0,0,0,0.7)",
  },
  infoContainer: {
    backgroundColor: "rgba(0,0,0,0.5)",
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
  },
  infoText: {
    color: "white",
    fontSize: 16,
    fontWeight: "500",
    textAlign: "center",
    marginBottom: 5,
  },
  highestText: {
    color: "#FFD700", // Gold color for highlighting
    fontSize: 24,
    fontWeight: "bold",
    textAlign: "center",
    marginTop: 10,
  },
  buttonContainer: {
    flexDirection: "row",
    justifyContent: "space-between",
  },
  button: {
    flex: 1,
    padding: 15,
    borderRadius: 10,
    alignItems: "center",
    marginHorizontal: 5,
  },
  buttonStart: {
    backgroundColor: "#4CAF50", // Green
  },
  buttonStop: {
    backgroundColor: "#f44336", // Red
  },
  captureButton: {
    backgroundColor: "#2196F3", // Blue
  },
  buttonDisabled: {
    backgroundColor: "#cccccc", // Gray
    opacity: 0.7,
  },
  buttonText: {
    color: "white",
    fontSize: 16,
    fontWeight: "bold",
  },
});
