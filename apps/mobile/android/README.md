# Android Mobile App

## Overview
Native Android application for RAW/DNG image capture with real-time color card detection for the Color Correction System.

## Technology Stack
- **Language**: Kotlin
- **Camera API**: Camera2 API + CameraX
- **Computer Vision**: OpenCV for Android
- **Architecture**: MVVM with Jetpack Compose
- **Networking**: Retrofit + OkHttp
- **Image Processing**: RenderScript / Vulkan

## Features

### Core Capture
- RAW/DNG capture with Camera2 API
- Fallback to high-quality JPEG if RAW unavailable
- Manual exposure, ISO, and shutter controls
- Focus peaking and exposure meter
- Live histogram display

### Real-time Detection
- ArUco marker detection overlay
- Color card alignment guides
- Quality indicators (distance, angle, lighting)
- Visual feedback for optimal positioning
- Capture readiness indicators

### Processing & Upload
- Background upload to cloud API
- Low-resolution preview processing
- Progress notifications
- Batch upload queue management
- Offline mode with sync

### Device Capability Detection
- RAW capability badge
- Camera tier classification
- Lens info and calibration metadata
- Device profile caching

## Project Structure
```
app/
├── src/main/
│   ├── java/com/colorcorrection/
│   │   ├── ui/
│   │   │   ├── capture/
│   │   │   ├── gallery/
│   │   │   └── settings/
│   │   ├── camera/
│   │   │   ├── Camera2Manager.kt
│   │   │   └── CameraXManager.kt
│   │   ├── detection/
│   │   │   ├── ArucoDetector.kt
│   │   │   └── CardAlignmentHelper.kt
│   │   ├── network/
│   │   │   ├── ApiService.kt
│   │   │   └── UploadManager.kt
│   │   └── utils/
│   ├── res/
│   └── AndroidManifest.xml
├── build.gradle.kts
└── proguard-rules.pro
```

## Setup Instructions

### Prerequisites
- Android Studio Hedgehog or later
- Android SDK 24+ (minimum)
- Android SDK 33+ (target)
- NDK for OpenCV native libs
- Gradle 8.0+

### Build
```bash
./gradlew assembleDebug
```

### Run
```bash
./gradlew installDebug
adb shell am start -n com.colorcorrection/.MainActivity
```

## Dependencies
- androidx.camera:camera-camera2
- androidx.camera:camera-lifecycle
- org.opencv.android:opencv
- com.squareup.retrofit2:retrofit
- androidx.compose.ui:ui
- com.google.accompanist:accompanist-permissions

## Testing
- Unit tests: `./gradlew test`
- Instrumented tests: `./gradlew connectedAndroidTest`
- Camera tests require physical device with RAW support

## Permissions Required
- CAMERA
- WRITE_EXTERNAL_STORAGE
- READ_EXTERNAL_STORAGE
- INTERNET
- ACCESS_NETWORK_STATE
