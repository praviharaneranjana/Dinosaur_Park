# Unified Mobile Notifications API Reference

The Unified API (`Unity.Notifications.NotificationCenter`) provides a single cross-platform interface for Android and iOS, removing the need for platform `#if UNITY_ANDROID` or `#if UNITY_IOS` compiler preprocessors in standard game notification workflows.

---

## 1. System Initialization

`NotificationCenter` must be initialized once before scheduling any notifications.

```csharp
using Unity.Notifications;
using UnityEngine;

public class NotificationInitializer : MonoBehaviour
{
    private void Awake()
    {
        // 1. Populate default arguments
        var args = NotificationCenterArgs.Default;

        // 2. Configure default Android channel
        args.AndroidChannelId = "game_main_channel";
        args.AndroidChannelName = "General Game Notifications";
        args.AndroidChannelDescription = "Alerts for stamina refills, daily rewards, and game events.";

        // 3. Initialize
        NotificationCenter.Initialize(args);
    }
}
```

---

## 2. Requesting User Permissions

Android 13+ (API 33+) and all iOS versions require explicit runtime permission from the player before notifications can appear.

```csharp
using System.Collections;
using Unity.Notifications;
using UnityEngine;

public class NotificationPermissionHandler : MonoBehaviour
{
    public IEnumerator RequestPermissionCoroutine()
    {
        var request = NotificationCenter.RequestPermission();

        // Suspend until user grants, denies, or dismisses dialog
        if (request.Status == NotificationsPermissionStatus.RequestPending)
        {
            yield return request;
        }

        switch (request.Status)
        {
            case NotificationsPermissionStatus.Authorized:
                Debug.Log("Notifications authorized by user.");
                break;
            case NotificationsPermissionStatus.Denied:
                Debug.LogWarning("Notifications denied by user.");
                break;
            case NotificationsPermissionStatus.NotSupported:
                Debug.Log("Notifications not supported on this platform/device.");
                break;
        }
    }
}
```

---

## 3. Creating & Scheduling Notifications

### 3.1 The `Notification` Data Object
```csharp
var notification = new Notification
{
    Identifier = 2001,                    // Unique ID (used to update or cancel later)
    Title = "Chest Unlocked! 🎁",
    Text = "Your silver mystery chest is ready to be opened!",
    Data = "chest_id=silver_04;type=reward", // Custom payload data
    Badge = 1,                            // Badge number to show on app icon
    ShowInForeground = false              // Suppress banner if player is currently in-game
};
```

### 3.2 Scheduling by Target Date (`NotificationDateTimeSchedule`)
Displays at an absolute calendar point in time (e.g. tomorrow at 08:00 AM):

```csharp
System.DateTime targetTime = System.DateTime.Today.AddDays(1).AddHours(8); // Tomorrow at 8 AM
var schedule = new NotificationDateTimeSchedule(targetTime);

NotificationCenter.ScheduleNotification(notification, schedule);
```

### 3.3 Scheduling by Relative Interval (`NotificationIntervalSchedule`)
Displays after a duration elapses from now (e.g. 2 hours and 30 minutes from now):

```csharp
System.TimeSpan delay = System.TimeSpan.FromHours(2.5);
var schedule = new NotificationIntervalSchedule(delay);

NotificationCenter.ScheduleNotification(notification, schedule);
```

### 3.4 Repeating Schedules
To repeat an alert periodically (e.g. every 24 hours):

```csharp
System.TimeSpan initialDelay = System.TimeSpan.FromHours(24);
System.TimeSpan repeatInterval = System.TimeSpan.FromDays(1);

var repeatingSchedule = new NotificationIntervalSchedule(initialDelay, repeatInterval);
NotificationCenter.ScheduleNotification(notification, repeatingSchedule);
```

---

## 4. Updating & Canceling Notifications

```csharp
// Cancel an upcoming scheduled notification before it fires:
NotificationCenter.CancelScheduledNotification(2001);

// Remove an alert that has already been delivered and is sitting in the tray:
NotificationCenter.CancelDeliveredNotification(2001);

// Cancel ALL scheduled notifications (e.g. when resetting game state):
NotificationCenter.CancelAllScheduledNotifications();

// Clear ALL delivered notifications (standard practice on app launch):
NotificationCenter.CancelAllDeliveredNotifications();
```

> [!TIP]
> **Updating an Alert**:
> To update an existing scheduled notification (e.g. stamina full time changed because player spent more stamina), simply call `ScheduleNotification` with the **same `Identifier`**. The new schedule automatically replaces the previous one.

---

## 5. Detecting App Launch from Notification Tap

To check if the player launched or resumed the game by tapping a notification:

```csharp
using System.Collections;
using Unity.Notifications;
using UnityEngine;

public class NotificationResponseTracker : MonoBehaviour
{
    private IEnumerator Start()
    {
        var query = NotificationCenter.QueryLastRespondedNotification();
        yield return query;

        if (query.State == QueryLastRespondedNotificationState.HaveRespondedNotification)
        {
            Notification notification = query.Notification;
            Debug.Log($"App opened via notification! Title: {notification.Title}, Payload: {notification.Data}");

            // Handle custom deep-link payload (e.g. open chest screen)
            if (!string.IsNullOrEmpty(notification.Data))
            {
                HandleNotificationDeepLink(notification.Data);
            }
        }
    }

    private void HandleNotificationDeepLink(string data)
    {
        if (data.Contains("chest_id"))
        {
            // Navigate directly to the Chest inventory UI
        }
    }
}
```
