---
trigger: "When implementing, modifying, or scheduling mobile notifications, push alerts, app badges, or retention reminders."
---

# Mobile Notifications & Player Retention Rules

## 1. Permission & OS Compliance
- **Android 13+ (API 33+) Runtime Permission**: Always request notification permission at runtime via `NotificationCenter.RequestPermission()` or `Permission.RequestUserPermission("android.permission.POST_NOTIFICATIONS")`. Never attempt to post notifications without checking authorization status.
- **Mandatory Android Channels**: On Android 8.0+ (API 26+), every notification MUST be associated with a registered `AndroidNotificationChannel`. Create and register channels during app initialization.
- **iOS Authorization Flow**: Request `AuthorizationOption.Alert | AuthorizationOption.Badge | AuthorizationOption.Sound` using `NotificationCenter.RequestPermission()` or `iOSNotificationCenter.RequestAuthorization`.

## 2. Notification Hygiene & User Experience
- **Quiet Hours Enforcement**: Never allow local notifications to fire between 22:00 (10:00 PM) and 08:00 (8:00 AM) local player time. Push midnight timers to the following morning.
- **Clear on Startup**: Always call `NotificationCenter.CancelAllDeliveredNotifications()` and reset `iOSNotificationCenter.ApplicationBadge = 0` when the player launches or returns to the game.
- **Unique Identifier Discipline**: Assign fixed, meaningful integer IDs (e.g. `1001` for Energy, `1002` for Daily Login) to allow updating existing alerts without creating duplicate notifications in the tray.

## 3. Custom Icons & Assets
- **Android Small Icon Requirement**: The small icon (`SmallIcon`) must be an all-white silhouette on a transparent background (`.png`). Non-transparent or multi-colored icons will render as solid white boxes on modern Android versions.
- **Project Settings Registration**: Register all custom icons in `Project Settings > Mobile Notifications > Android`.
