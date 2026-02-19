# TikTok Developer - Mobile SDK

## Overview

The TikTok OpenSDK for iOS and Android enables native integration of TikTok functionality into mobile apps. It provides two primary capabilities: user authentication (Login Kit) and content sharing (Share Kit, including Green Screen Kit).

## Supported Platforms

| Platform | Minimum Version |
|----------|----------------|
| iOS | 11.0 or later |
| Android | API level 21 (Android 5.0 Lollipop) or later |

## Core Capabilities

1. **Authentication (Login Kit)**: Users log in with their TikTok accounts via OAuth 2.0
2. **Content Sharing (Share Kit)**: Share images and videos from your app to TikTok
3. **Green Screen (Green Screen Kit)**: Share content as a green screen background

---

## iOS SDK

### Installation

**Swift Package Manager:**
```
https://github.com/tiktok/tiktok-opensdk-ios
```

**CocoaPods:**
```ruby
pod 'TikTokOpenSDKCore'
pod 'TikTokOpenAuthSDK'
pod 'TikTokOpenShareSDK'
```

### Configuration (Info.plist)

Add `LSApplicationQueriesSchemes`:
- `tiktokopensdk` (Login Kit)
- `tiktoksharesdk` (Share Kit)
- `snssdk1233` (device detection)
- `snssdk1180` (device detection)

Add `TikTokClientKey` with your client key value.

Add client key to `CFBundleURLSchemes` for callback handling.

### AppDelegate Integration

Implement URL handling through `TikTokURLHandler.handleOpenURL()` in both traditional AppDelegate and SceneDelegate approaches.

### Requirements

- Xcode 9.0 or later
- Developer account on TikTok for Developers
- Client key and client secret (obtained after app approval)

### Repository

```
https://github.com/tiktok/tiktok-opensdk-ios
```

---

## Android SDK

### Installation (Gradle)

```groovy
repositories {
    maven { url "https://artifact.bytedance.com/repository/AwemeOpenSDK" }
}

dependencies {
    implementation 'com.tiktok.open.sdk:tiktok-open-sdk-core:latest.release'
    implementation 'com.tiktok.open.sdk:tiktok-open-sdk-auth:latest.release'
    implementation 'com.tiktok.open.sdk:tiktok-open-sdk-share:latest.release'
}
```

### Android 11+ Configuration

For devices targeting Android 11 (API 30) and later, add package visibility declarations in `AndroidManifest.xml`:
- `com.zhiliaoapp.musically` (TikTok international)
- `com.ss.android.ugc.trill` (TikTok regional variant)

### Registration Requirements

- MD5 certificate fingerprint
- SHA-256 certificate fingerprint
- Both Google Play signing and self-signed certificates supported

### Repository

```
https://github.com/tiktok/tiktok-opensdk-android
```

---

## SDK Module Structure

| Module | Purpose |
|--------|---------|
| `tiktok-open-sdk-core` | Foundation/core module (required) |
| `tiktok-open-sdk-auth` | Login Kit authentication |
| `tiktok-open-sdk-share` | Share Kit content sharing |

All higher-level modules depend on the core module.
