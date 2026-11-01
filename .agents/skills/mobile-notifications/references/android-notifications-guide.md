# Android Notifications Guide (AndroidNotificationCenter)

This guide covers advanced Android-specific notification features using `Unity.Notifications.Android.AndroidNotificationCenter`, including notification channels, importance levels, custom icons, and Android 13 runtime permissions.

---

## 1. Notification Channels (Android 8.0+ / API 26+)

Since Android 8.0 (Oreo), all notifications **must** be posted to a registered `AndroidNotificationChannel`. If you attempt to send a notification without a valid channel ID, Android will silently discard it.

```csharp
using Unity.Notifications.Android;
using UnityEngine;

public class AndroidChannelSetup : MonoBehaviour
{
    public const string ChannelStamina = "channel_stamina";
    public const string ChannelCombat = "channel_combat";

    private void Start()
    {
        CreateNotificationChannels();
    }

    private void CreateNotificationChannels()
    {
        // 1. High-importance channel: makes a sound and pops up on screen (Heads-up alert)
        var combatChannel = new AndroidNotificationChannel()
        {
            Id = ChannelCombat,
            Name = "PvP & Raids",
            Importance = Importance.High,
            Description = "Alerts when your base is raided or combat begins.",
            EnableVibration = true,
            EnableLights = true
        };
        AndroidNotificationCenter.RegisterNotificationChannel(combatChannel);

        // 2. Default-importance channel: makes a sound, appears in tray
        var staminaChannel = new AndroidNotificationChannel()
        {
            Id = ChannelStamina,
            Name = "Stamina & Energy",
            Importance = Importance.Default,
            Description = "Alerts when your stamina has fully recharged.",
            EnableVibration = false
        };
        AndroidNotificationCenter.RegisterNotificationChannel(staminaChannel);
    }
}
```

---

## 2. Android 13+ (API 33+) Runtime Permission

Android 13 introduced the `android.permission.POST_NOTIFICATIONS` runtime permission.

```csharp
using System.Collections;
using Unity.Notifications.Android;
using UnityEngine;
using UnityEngine.Android;

public class AndroidPermissionRequester : MonoBehaviour
{
    private IEnumerator Start()
    {
        // Check if Android 13+ and permission not yet granted
        if (!Permission.HasUserAuthorizedPermission("android.permission.POST_NOTIFICATIONS"))
        {
            var request = new PermissionCallbacks();
            request.PermissionGranted += (perm) => Debug.Log("Notification permission granted!");
            request.PermissionDenied += (perm) => Debug.LogWarning("Notification permission denied!");

            Permission.RequestUserPermission("android.permission.POST_NOTIFICATIONS", request);
            yield return null;
        }
    }
}
```

---

## 3. Scheduling with `AndroidNotification`

```csharp
using System;
using Unity.Notifications.Android;
using UnityEngine;

public class AndroidNotificationSender : MonoBehaviour
{
    public void ScheduleEnergyNotification(int minutesUntilFull)
    {
        var notification = new AndroidNotification
        {
            Title = "Stamina Full! ⚔️",
            Text = "Your hero is ready for the dungeon.",
            FireTime = DateTime.Now.AddMinutes(minutesUntilFull),
            SmallIcon = "icon_small",      // Defined in Project Settings > Mobile Notification Settings
            LargeIcon = "icon_large",      // 192x192 PNG preview icon
            Color = new Color32(255, 140, 0, 255), // Accent color in Android notification header
            IntentData = "screen=dungeon_select"   // Passed back to app when tapped
        };

        // Send to specific channel and get generated notification ID
        int notificationId = AndroidNotificationCenter.SendNotification(notification, AndroidChannelSetup.ChannelStamina);
        Debug.Log($"Scheduled Android notification with ID: {notificationId}");
    }
}
```

---

## 4. Checking Notification Delivery Status

You can query whether an Android notification is scheduled, delivered, or unknown:

```csharp
NotificationStatus status = AndroidNotificationCenter.CheckScheduledNotificationStatus(notificationId);

switch (status)
{
    case NotificationStatus.Scheduled:
        Debug.Log("Notification is waiting in the Android system alarm queue.");
        break;
    case NotificationStatus.Delivered:
        Debug.Log("Notification has been shown to the user.");
        break;
    case NotificationStatus.Unknown:
        Debug.Log("Notification ID not found or already dismissed.");
        break;
}
```

---

## 5. Custom Notification Icons Setup

In **Edit > Project Settings > Mobile Notifications > Android**:
1. Add an entry to **Notification Icons**.
2. **Small Icon** (`icon_small`):
   - Must be an **all-white silhouette on a transparent background** (`.png`).
   - Android tints this icon automatically; non-transparent or colored pixels will render as an ugly white solid square on Android 8+.
3. **Large Icon** (`icon_large`):
   - Standard 192x192 RGB/RGBA image (game logo, item artwork, character face). Displays to the right of the notification body.
