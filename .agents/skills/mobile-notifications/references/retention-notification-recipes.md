# Game Retention Notification Recipes

Local push notifications are one of the most effective tools for increasing Day-1, Day-7, and Day-30 mobile player retention. When implemented ethically around player-driven milestones, they serve as helpful reminders rather than intrusive spam.

---

## 1. The 5 Core Game Notification Patterns

| Recipe | Trigger Event | Optimal Timing | Goal |
|---|---|---|---|
| **1. Energy / Stamina Refilled** | Player depletes energy in combat | Calculated exact refill time | Re-engage player for their next play session. |
| **2. Timed Chest / Upgrade Ready** | Player starts opening a mystery chest / building | When unlock timer expires (e.g. 3 hours) | Provide an immediate feeling of progression & reward. |
| **3. Daily Bonus / Spin Reset** | App paused / backgrounded | Next day at 09:00 AM local time | Establish a daily login ritual. |
| **4. Event Ending Soon** | Active time-limited raid or battle pass | 4 hours before event expiration | Create urgency to finish quests and claim rewards. |
| **5. Gentle Inactivity Comeback** | Player has not opened game for 48 hours | 48 hours after last exit (at 12:00 PM) | Re-ignite curiosity with a free welcome-back gift. |

---

## 2. Production C# Notification Manager Implementation

This complete, production-ready manager handles energy scheduling, daily resets, quiet hours protection, and badge resetting:

```csharp
using System;
using System.Collections;
using Unity.Notifications;
#if UNITY_ANDROID
using Unity.Notifications.Android;
#endif
#if UNITY_IOS
using Unity.Notifications.iOS;
#endif
using UnityEngine;

public class GameNotificationManager : MonoBehaviour
{
    public static GameNotificationManager Instance { get; private set; }

    private const int IdEnergyRefill = 1001;
    private const int IdDailyReward = 1002;
    private const int IdChestReady = 1003;
    private const int IdInactivityReminder = 1004;

    private void Awake()
    {
        if (Instance != null) { Destroy(gameObject); return; }
        Instance = this;
        DontDestroyOnLoad(gameObject);

        InitializeNotificationSystem();
    }

    private void Start()
    {
        StartCoroutine(RequestPermissions());
        ClearDeliveredNotificationsOnStartup();
    }

    private void InitializeNotificationSystem()
    {
        var args = NotificationCenterArgs.Default;
        args.AndroidChannelId = "game_alerts_channel";
        args.AndroidChannelName = "Game Alerts";
        args.AndroidChannelDescription = "Alerts for stamina, rewards, and timers.";
        NotificationCenter.Initialize(args);
    }

    private IEnumerator RequestPermissions()
    {
        var req = NotificationCenter.RequestPermission();
        if (req.Status == NotificationsPermissionStatus.RequestPending)
            yield return req;
    }

    private void ClearDeliveredNotificationsOnStartup()
    {
        // Clear all alerts from tray when player launches the game
        NotificationCenter.CancelAllDeliveredNotifications();

#if UNITY_IOS
        iOSNotificationCenter.ApplicationBadge = 0;
#endif
    }

    /// <summary>
    /// Recipe 1: Schedule Stamina Refilled alert
    /// </summary>
    public void ScheduleEnergyRefilled(int minutesUntilFull)
    {
        if (minutesUntilFull <= 0) return;

        DateTime targetTime = DateTime.Now.AddMinutes(minutesUntilFull);
        targetTime = EnforceQuietHours(targetTime); // Shift if fires in middle of night!

        var notification = new Notification
        {
            Identifier = IdEnergyRefill,
            Title = "Stamina Fully Restored! ⚡",
            Text = "Your energy is full! Jump back in and continue your adventure.",
            Data = "nav=stamina"
        };

        NotificationCenter.ScheduleNotification(notification, new NotificationDateTimeSchedule(targetTime));
    }

    /// <summary>
    /// Recipe 2: Schedule Daily Reward Reminder for tomorrow morning
    /// </summary>
    public void ScheduleDailyRewardReminder()
    {
        DateTime tomorrowMorning = DateTime.Today.AddDays(1).AddHours(9); // Tomorrow 9:00 AM

        var notification = new Notification
        {
            Identifier = IdDailyReward,
            Title = "Daily Gift Awaits! 🎁",
            Text = "Your daily bonus gems are ready to collect. Don't miss out!",
            Data = "nav=daily_gift"
        };

        NotificationCenter.ScheduleNotification(notification, new NotificationDateTimeSchedule(tomorrowMorning));
    }

    /// <summary>
    /// Recipe 3: Protect players from notifications during sleeping hours (10:00 PM - 08:00 AM)
    /// </summary>
    private DateTime EnforceQuietHours(DateTime scheduledTime)
    {
        int hour = scheduledTime.Hour;

        // If scheduled between 10 PM and 8 AM, push to 8:30 AM next morning
        if (hour >= 22 || hour < 8)
        {
            DateTime nextMorning = scheduledTime.Date;
            if (hour >= 22) nextMorning = nextMorning.AddDays(1);
            return nextMorning.AddHours(8).AddMinutes(30);
        }

        return scheduledTime;
    }
}
```

---

## 3. Best Practices for High Retention

1. **Quiet Hours Protection**: Never schedule local notifications between 22:00 (10 PM) and 08:00 (8 AM) local time. Nighttime dings lead to immediate notification revocation or uninstalls.
2. **Clear on Open**: Always clear delivered notifications when the player enters the game. Nothing looks worse than opening a game and seeing a notification sitting in the tray telling you to open the game!
3. **Deep Linking**: Attach serialized navigation payloads (e.g. `data = "nav=chest"`) so when the player taps the notification, the game takes them straight to the chest screen rather than dumping them at the main menu.
