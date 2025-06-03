import React, { useEffect, useState } from "react";
import {
  StyleSheet,
  View,
  Text,
  StatusBar,
  ActivityIndicator,
} from "react-native";
import * as tf from "@tensorflow/tfjs";
import { LogBox } from "react-native";

// Import our components
import NumberTracker from "./NumberTracker";
import SplashScreen from "./SplashScreen";

// Ignore specific warnings that might come from TensorFlow
LogBox.ignoreLogs([
  "Non-serializable values were found in the navigation state",
  "TensorFlow is still loading",
  "RCTBridge required dispatch_sync to load RNGestureHandlerModule",
]);

export default function App() {
  const [isTfReady, setIsTfReady] = useState(false);
  const [showSplash, setShowSplash] = useState(true);

  // Initialize TensorFlow.js
  useEffect(() => {
    const initializeTf = async () => {
      try {
        await tf.ready();
        setIsTfReady(true);
        console.log("TensorFlow.js is ready");
      } catch (error) {
        console.error("Failed to initialize TensorFlow", error);
      }
    };

    initializeTf();

    // Clean up TensorFlow resources on unmount
    return () => {
      tf.engine().startScope();
      tf.engine().endScope();
      console.log("TensorFlow resources cleaned up");
    };
  }, []);

  const handleSplashFinish = () => {
    setShowSplash(false);
  };

  if (showSplash) {
    return <SplashScreen onFinish={handleSplashFinish} />;
  }

  if (!isTfReady) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#4CAF50" />
        <Text style={styles.loadingText}>Initializing TensorFlow.js...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000000" />
      <NumberTracker />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#000",
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#000",
  },
  loadingText: {
    color: "white",
    marginTop: 20,
    fontSize: 18,
  },
});
