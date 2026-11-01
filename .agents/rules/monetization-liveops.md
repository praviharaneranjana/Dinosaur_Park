# Monetization and Live Operations Guidelines

This rule establishes technical standards for In-App Purchases (`implement-in-app-purchases`), LevelPlay Ad Mediation (`levelplay-unity-integration`), and Unity Gaming Services (`build-live-game`).

## 1. In-App Purchases (Unity IAP)
- **Catalog Management**: Always configure products through `ProductCatalog` with deterministic product IDs (e.g., `gem_pack_100`, `vip_monthly_sub`).
- **Store Receipt Validation**:
  - Never unlock purchased currencies or items client-side without validating the cryptographic app store receipt.
  - Prefer server-side receipt validation via UGS Cloud Code or backend auth rather than trusting client-side `IStoreListener.ProcessPurchase`.
- **Purchase Restoration**: Always expose a dedicated "Restore Purchases" button in game settings on iOS/macOS builds as required by App Store Review Guideline 3.1.1.

## 2. Ad Mediation (IronSource LevelPlay)
- **SDK Lifecycle**:
  - Initialize the LevelPlay SDK once during game splash/bootstrap before loading gameplay scenes: `IronSource.Agent.init(appKey)`.
  - Pause game audio, time scale, or network tick rates during fullscreen interstitial and rewarded video playback via `OnApplicationPause` callbacks.
- **Rewarded Ad Flow**:
  - Only grant in-game rewards on `OnRewardedVideoAdRewardedEvent`.
  - Never grant rewards solely on `OnRewardedVideoAdClosedEvent` or ad click.
- **Privacy & Compliance**: Ensure COPPA, GDPR, and ATT (App Tracking Transparency on iOS) consent flags are set before initializing the ad network.

## 3. Unity Gaming Services (UGS) LiveOps
- **Authentication**: Initialize `UnityServices.InitializeAsync()` followed by anonymous or social sign-in (`AuthenticationService.Instance.SignInAnonymouslyAsync()`).
- **Remote Config**: Cache Remote Config parameters locally to prevent network timeouts from halting game boot.
- **Cloud Save**: Always include timestamp metadata and merge conflicts cleanly when saving player progress across multiple devices.
