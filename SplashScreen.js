import React, { useEffect } from "react";
import { View, Text, StyleSheet, Image, Animated } from "react-native";

const SplashScreen = ({ onFinish }) => {
  const fadeAnim = new Animated.Value(0);

  useEffect(() => {
    // Fade in animation
    Animated.sequence([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 1000,
        useNativeDriver: true,
      }),
      // Wait for 1.5 seconds
      Animated.delay(1500),
      // Fade out
      Animated.timing(fadeAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true,
      }),
    ]).start(() => {
      // Call onFinish when animation is complete
      if (onFinish) {
        onFinish();
      }
    });
  }, []);

  return (
    <View style={styles.container}>
      <Animated.View style={[styles.content, { opacity: fadeAnim }]}>
        <View style={styles.iconContainer}>
          <Text style={styles.numberIcon}>1-500</Text>
        </View>
        <Text style={styles.title}>Number Tracker</Text>
        <Text style={styles.subtitle}>Find the highest number</Text>
      </Animated.View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#000",
  },
  content: {
    alignItems: "center",
  },
  iconContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: "#2196F3",
    justifyContent: "center",
    alignItems: "center",
    marginBottom: 30,
  },
  numberIcon: {
    fontSize: 28,
    fontWeight: "bold",
    color: "white",
  },
  title: {
    fontSize: 32,
    fontWeight: "bold",
    color: "white",
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 18,
    color: "#bbb",
  },
});

export default SplashScreen;
