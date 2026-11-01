# iOS Notifications Guide (iOSNotificationCenter)

This guide details iOS-specific features using `Unity.Notifications.iOS.iOSNotificationCenter`, including authorization options, calendar/interval triggers, badges, and notification actions under the Apple UserNotifications framework.

---

## 1. Requesting iOS Authorization

iOS requires explicit user consent before displaying alerts, updating badge counts, or playing sounds.

```csharp
using System.Collections;
using Unity.Notifications.iOS;
using UnityEngine;

public class iOSAuthorizationHandler : MonoBehaviour
{
    private IEnumerator Start()
    {
        // Request Alert, Badge, and Sound permissions
        var authOptions = AuthorizationOption.Alert | AuthorizationOption.Badge | AuthorizationOption.Sound;
        
        using (var req = new AuthorizationRequest(authOptions, registerForRemoteNotifications: false))
        {
            while (!req.IsFinished)
            {
                yield return null;
            }

            if (req.Granted)
            {
                Debug.Log("iOS Notification authorization granted!");
            }
            else
            {
                Debug.LogWarning($"iOS Notification authorization denied: {req.Error}");
            }
        }
    }
}
```

---

## 2. Scheduling with Triggers

iOS uses dedicated trigger classes to specify when notifications fire:

### 2.1 Time Interval Trigger (`iOSNotificationTimeIntervalTrigger`)
Fires after a specified duration:

```csharp
using System;
using Unity.Notifications.iOS;
using UnityEngine;

public class iOSTimeNotification : MonoBehaviour
{
    public void ScheduleTimeAlert(string title, string body, TimeSpan delay)
    {
        var timeTrigger = new iOSNotificationTimeIntervalTrigger()
        {
            TimeInterval = delay,
            Repeats = false
        };

        var notification = new iOSNotification()
        {
            Identifier = "_stamina_refill",
            Title = title,
            Subtitle = "Stamina Full",
            Body = body,
            ShowInForeground = true, // Display banner even if player has app open
            Badge = 1,
            Trigger = timeTrigger
        };

        iOSNotificationCenter.ScheduleNotification(notification);
    }
}
```

### 2.2 Calendar Trigger (`iOSNotificationCalendarTrigger`)
Fires at a specific recurring calendar time (e.g. Daily reset at 09:00 AM every day):

```csharp
var calendarTrigger = new iOSNotificationCalendarTrigger()
{
    Hour = 9,
    Minute = 0,
    Repeats = true // Repeats every day at 09:00 AM!
};

var dailyResetNotification = new iOSNotification()
{
    Identifier = "_daily_reset",
    Title = "Daily Rewards Ready! 🌟",
    Body = "Log in today to claim your daily bonus gems!",
    Trigger = calendarTrigger
};

iOSNotificationCenter.ScheduleNotification(dailyResetNotification);
```

---

## 3. Managing the App Icon Badge

The red numeric badge on the iOS app icon must be managed actively to keep the user interface clean:

```csharp
// Clear the app icon badge count when the player enters the game:
public void ClearBadgeOnAppOpen()
{
    iOSNotificationCenter.ApplicationBadge = 0;
}

// Set a specific badge number:
public void SetBadgeCount(int pendingAlerts)
{
    iOSNotificationCenter.ApplicationBadge = pendingAlerts;
}
```

---

## 4. Notification Categories & Interactive Actions

You can register interactive action buttons that allow players to respond directly from the iOS lock screen (e.g. "Accept" / "Decline" duel):

```csharp
public void RegisterInteractiveCategories()
{
    var acceptAction = new iOSNotificationAction("ACCEPT_ACTION", "Accept Duel ⚔️", iOSNotificationActionOptions.Foreground);
    var declineAction = new iOSNotificationAction("DECLINE_ACTION", "Decline", iOSNotificationActionOptions.Destructive);

    var duelCategory = new iOSNotificationCategory("DUEL_CATEGORY", new[] { acceptAction, declineAction });

    iOSNotificationCenter.SetNotificationCategories(new[] { duelCategory });
}
```
