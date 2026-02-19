# TikTok Developer - Green Screen Kit

## Overview

The Green Screen Kit enables users to share content from third-party apps as a green screen background in TikTok. It uses TikTok's green-screen effect to let creators record videos with an image or video in the background and the creator's face in the foreground.

## Supported Platforms

- **iOS**: Version 11.0 or later
- **Android**: API level 21 (Android 5.0 Lollipop) or later

## How It Works

Green Screen Kit is a feature of Share Kit. Both platforms use a `shareFormat` field set to green screen mode within the share request object.

## iOS Implementation

**Prerequisites:** Complete the iOS Mobile SDK quickstart.

**Dependencies (CocoaPods):**
- `TikTokOpenSDKCore`
- `TikTokOpenShareSDK`

**Swift Package Manager:**
```
https://github.com/tiktok/tiktok-opensdk-ios
```

**Code Example:**

```swift
import TikTokOpenShareSDK

let shareRequest = TikTokShareRequest()
shareRequest.localIdentifiers = [assetIdentifier]
shareRequest.mediaType = .video  // or .image
shareRequest.shareFormat = .greenScreen
shareRequest.redirectURI = "your-redirect-uri"

shareRequest.send { response in
    let shareResponse = response as? TikTokShareResponse
    if shareResponse?.errorCode == .noError {
        print("Share succeeded!")
    }
}
```

## Android Implementation

**Prerequisites:** Complete the Android Mobile SDK quickstart.

**Dependencies (Gradle):**

```groovy
implementation 'com.tiktok.open.sdk:tiktok-open-sdk-core:latest.release'
implementation 'com.tiktok.open.sdk:tiktok-open-sdk-share:latest.release'
```

**Repository:**
```groovy
maven { url "https://artifact.bytedance.com/repository/AwemeOpenSDK" }
```

**Code Example:**

```kotlin
val mediaContent = MediaContent(/* media paths */)
val request = ShareRequest(
    clientKey = clientKey,
    mediaContent = mediaContent,
    shareFormat = Format.GREEN_SCREEN,
    packageName = packageName,
    resultActivityFullPath = activityPath
)
val shareApi = ShareApi(activity)
shareApi.share(request)
```

## Limitations

1. **Single item only**: Only supports sharing a single video or single image. Multiple items cause the green screen format to be ignored.
2. **Video trimming**: Videos include an extra trimming step before recording begins.
3. **Fallback behavior**: Falls back to regular sharing if the green screen effect fails to load.

## Related Documentation

- Share Kit for iOS
- Share Kit for Android
- Mobile SDK iOS Quickstart
- Mobile SDK Android Quickstart
