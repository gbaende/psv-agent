import React from "react";
import { View, Text, StyleSheet, Dimensions } from "react-native";

const { width, height } = Dimensions.get("window");

const NumberDetectionBox = ({ detectedNumber, bbox, isHighest }) => {
  // bbox format is [x, y, width, height] normalized to 0-1
  // We convert to screen coordinates
  const boxStyle = {
    left: bbox[0] * width,
    top: bbox[1] * height,
    width: bbox[2] * width,
    height: bbox[3] * height,
    borderColor: isHighest ? "#FFD700" : "#FF0000",
  };

  return (
    <View style={[styles.detectionBox, boxStyle]}>
      <View style={styles.numberContainer}>
        <Text style={[styles.numberText, isHighest && styles.highestText]}>
          {detectedNumber}
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  detectionBox: {
    position: "absolute",
    borderWidth: 2,
    backgroundColor: "transparent",
    justifyContent: "flex-start",
    alignItems: "flex-start",
  },
  numberContainer: {
    backgroundColor: "rgba(0, 0, 0, 0.7)",
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 4,
    position: "absolute",
    top: -30,
  },
  numberText: {
    color: "white",
    fontWeight: "bold",
    fontSize: 16,
  },
  highestText: {
    color: "#FFD700",
    fontSize: 18,
  },
});

export default NumberDetectionBox;
