# TikTok Effect House

## Overview

**Effect House** is TikTok's free, desktop-based augmented reality (AR) effect creation platform. It enables creators, developers, and brands to build custom AR effects (filters, lenses, face effects, world effects, interactive experiences) that can be published directly to TikTok for use in videos and LIVE streams. Effect House is comparable to Meta's Spark AR and Snapchat's Lens Studio.

**Website:** `https://effecthouse.tiktok.com/`

**Download:** Available for Windows and macOS at `https://effecthouse.tiktok.com/download`

---

## Purpose

- Enable anyone to create AR effects for TikTok
- Provide a visual, node-based development environment for AR creation
- Support branded effects for marketing campaigns
- Allow interactive effects for LIVE streams and video content
- Democratize AR creation without requiring deep coding knowledge

---

## Key Features

### Effect Types

| Effect Type | Description |
|-------------|-------------|
| Face Effects | Face filters, face tracking, face morphing, makeup, masks |
| Head Tracking | Effects that follow head movement (hats, hair, accessories) |
| Hand Tracking | Effects that respond to hand gestures and positions |
| Body Tracking | Full-body effects and segmentation |
| World Effects | AR objects placed in the 3D world (ground plane, surface tracking) |
| Background Effects | Background replacement, blur, segmentation |
| Interactive Effects | Touch-responsive and gesture-triggered effects |
| Mini Games | Simple interactive games as AR effects |
| Screen Effects | Post-processing effects (color grading, distortion, VHS) |
| Image Tracking | Effects anchored to flat image targets |

### Core Capabilities

| Capability | Description |
|------------|-------------|
| Visual Scripting | Node-based logic editor (no code required for many effects) |
| Script API | JavaScript/TypeScript scripting for advanced logic |
| 3D Asset Import | Import 3D models (FBX, OBJ, glTF), textures, animations |
| Face Mesh | Detailed face mesh for precise face-tracking effects |
| Segmentation | Person, hair, sky, and background segmentation |
| Physics Simulation | Cloth, particle, and rigid body physics |
| Audio Reactivity | Effects that respond to music/audio input |
| Multi-face Tracking | Track multiple faces simultaneously |
| Procedural Animation | Shader-based and node-based procedural animations |

---

## Effect House SDK / Script API

### Script API (JavaScript/TypeScript)

Effect House provides a **Script API** for advanced effect logic beyond visual scripting.

**Language:** JavaScript / TypeScript (compiled to run in Effect House runtime)

**Key Modules:**

| Module | Description |
|--------|-------------|
| `Scene` | Access and manipulate scene objects |
| `Transform` | Position, rotation, scale of objects |
| `Camera` | Camera properties and projection |
| `FaceMesh` | Face tracking mesh data and landmarks |
| `HandTracking` | Hand joint positions and gestures |
| `BodyTracking` | Body skeleton joint positions |
| `Segmentation` | Person/background/hair segmentation masks |
| `Animation` | Play, pause, blend animations |
| `Physics` | Rigid body, collision, ray casting |
| `Audio` | Audio playback and analysis |
| `Touch` | Touch/tap input events |
| `Gyroscope` | Device orientation data |
| `Persistence` | Save/load data between sessions |
| `Networking` | HTTP requests (limited, for approved effects) |
| `UI` | 2D UI elements (buttons, sliders, text) |

### Script Example

```typescript
// Simple face-tracking effect script
import { FaceTracking, Scene, Transform } from 'EffectHouse';

const faceTracker = FaceTracking.face(0);
const hatObject = Scene.root.find('hat_model');

faceTracker.onUpdate((face) => {
  const position = face.cameraTransform.position;
  const rotation = face.cameraTransform.rotation;

  Transform.setPosition(hatObject, position.x, position.y + 0.1, position.z);
  Transform.setRotation(hatObject, rotation.x, rotation.y, rotation.z);
});
```

---

## Effect House Architecture

### Node-Based Visual Editor

The core authoring experience uses a **visual node graph** system:

```
Input Nodes --> Processing Nodes --> Output Nodes
(camera, face)   (transform, math)   (render, material)
```

**Node Categories:**

| Category | Examples |
|----------|---------|
| Input | Camera Texture, Face Mesh, Hand Tracking, Microphone |
| Math | Add, Multiply, Lerp, Clamp, Random |
| Logic | If/Else, Compare, Switch, Delay, Timer |
| Transform | Position, Rotation, Scale, Look At |
| Material | Color, Texture, Shader, Blend Mode |
| Render | Mesh Renderer, Particle System, Trail Renderer |
| Animation | Animation Player, Tween, Keyframe |
| Physics | Rigid Body, Collider, Raycast |
| Audio | Audio Player, Audio Analyzer, Spectrum |
| Interaction | Tap, Swipe, Face Gesture, Head Nod |

### Project Structure

```
effect-project/
  assets/           # 3D models, textures, audio files
  scripts/          # JavaScript/TypeScript scripts
  materials/        # Shader materials
  prefabs/          # Reusable object templates
  scenes/           # Scene configuration
  effect.json       # Effect metadata and configuration
```

---

## Effect Publishing & Distribution

### Publishing Flow

```
1. Create effect in Effect House desktop app
2. Preview on device (TikTok Effect House Preview app)
3. Submit for review
4. TikTok reviews for quality, safety, and guidelines compliance
5. Approved effects appear in TikTok's Effect Gallery
6. Creators can use the effect in videos and LIVE streams
```

### Review Criteria

| Criteria | Description |
|----------|-------------|
| Technical quality | Stable framerate, no crashes, proper rendering |
| Content safety | No offensive, violent, or misleading content |
| Originality | Not a copy of existing effects |
| Performance | Acceptable on mid-range devices |
| Guidelines compliance | Follows TikTok Community Guidelines |

### Effect Analytics

Published effects provide analytics:

| Metric | Description |
|--------|-------------|
| Effect uses | Number of videos created with the effect |
| Unique users | Number of distinct users who used the effect |
| Impressions | Number of times videos with the effect were viewed |
| Save count | Number of users who saved the effect |
| Share count | Number of times the effect was shared |

---

## Effect House for LIVE

Effects can be used during TikTok LIVE streams:

| LIVE Feature | Description |
|--------------|-------------|
| LIVE effects | Creators apply AR effects during livestreams |
| Interactive effects | Viewers can trigger effects via gifts or comments |
| LIVE games | Mini-game effects for audience participation |
| Gift-triggered effects | Special effects activated by specific virtual gifts |

---

## Branded Effects

### Brand Partnership Effects

Effect House supports **branded effects** for marketing campaigns:

| Feature | Description |
|---------|-------------|
| Branded Hashtag Challenge | Custom effects for hashtag campaigns |
| Branded scan | Effects triggered by scanning a product/logo |
| Branded filter | Custom face/world filters with brand elements |
| TopView effects | Premium placement effects in the TikTok app |

### Access for Brands

- Brands can create effects through Effect House directly
- Premium branded effects campaigns are managed through **TikTok For Business** / **TikTok Ads Manager**
- Custom effect creation services available through TikTok's creative partners

---

## Developer Access Requirements

### Prerequisites

1. **TikTok account**: Required to sign in to Effect House
2. **Download**: Install Effect House desktop app (Windows 10+ or macOS 10.15+)
3. **No developer portal registration required**: Effect House is open to all users
4. **TikTok Effect House Preview app**: Install on mobile device for testing

### System Requirements

| Platform | Minimum Requirements |
|----------|---------------------|
| Windows | Windows 10 64-bit, 8 GB RAM, GPU with OpenGL 3.3+ |
| macOS | macOS 10.15 (Catalina)+, 8 GB RAM, Metal-compatible GPU |
| Preview (iOS) | iOS 13+ |
| Preview (Android) | Android 8.0+ |

### No API Registration Required

Unlike the TikTok Developer Platform APIs, Effect House does not require:
- Developer portal registration
- App creation or approval
- OAuth credentials
- API keys

It is a standalone creative tool that publishes directly to TikTok.

---

## Effect House vs. Other AR Platforms

| Feature | Effect House | Spark AR (Meta) | Lens Studio (Snap) |
|---------|-------------|-----------------|---------------------|
| Platform | TikTok | Instagram/Facebook | Snapchat |
| Cost | Free | Free | Free |
| Scripting | JavaScript/TypeScript | JavaScript | JavaScript |
| Visual Editor | Node-based | Patch Editor (node-based) | Node-based |
| 3D Import | FBX, OBJ, glTF | FBX, OBJ, glTF | FBX, OBJ, glTF |
| Body Tracking | Yes | Yes | Yes |
| Hand Tracking | Yes | Yes | Yes |
| World Tracking | Yes | Yes | Yes |
| LIVE Effects | Yes (TikTok LIVE) | Yes (IG Live) | Yes (Snap Live) |

---

## Effect House API Integrations

### No External REST API

Effect House does **not** provide an external REST API for:
- Programmatic effect creation
- Effect management
- Effect analytics retrieval
- Effect distribution

All effect creation, management, and publishing is done through the **Effect House desktop application**.

### Internal Script API Only

The Script API is for logic **within** effects, not for external integrations. It runs inside the TikTok app's AR runtime and cannot make arbitrary external API calls (networking is limited and requires approval).

---

## Key Limitations

1. **Desktop-only authoring**: Effects can only be created on Windows/macOS, not mobile or web
2. **No external API**: No REST/GraphQL API for programmatic effect management
3. **No bulk publishing**: Effects must be submitted individually through the desktop app
4. **Review delays**: Effect review can take days to weeks
5. **Performance constraints**: Effects must run at acceptable framerates on mid-range mobile devices
6. **Limited networking**: Scripts cannot make arbitrary HTTP requests without approval
7. **TikTok-only distribution**: Published effects only work on TikTok (not cross-platform)
8. **Effect size limits**: Asset size and complexity limits apply

## Related Documentation

- TikTok LIVE Platform: `./01-live-platform-overview.md`
- TikTok Developer Platform: `../tiktok-developer/01-platform-overview.md`
- Green Screen Kit: `../tiktok-developer/13-green-screen-kit.md`
