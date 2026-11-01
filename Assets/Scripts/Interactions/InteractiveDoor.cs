using System;
using System.Collections;
using UnityEngine;
using NaughtyAttributes;

namespace MiniGame.Interactions
{
    public enum DoorMotionType
    {
        DoubleSlide,
        SingleSlide,
        HingeSwing
    }

    public enum DoorState
    {
        Closed,
        Opening,
        Open,
        Closing,
        Locked
    }

    /// <summary>
    /// Handles interactive doors and gates (sliding automatic gates, double glass doors, single swing doors)
    /// with lock/unlock mechanics, smooth animation curves, and proximity sensor triggers.
    /// </summary>
    [SelectionBase]
    public class InteractiveDoor : MonoBehaviour
    {
        [Header("Door Configuration")]
        [SerializeField] private DoorMotionType motionType = DoorMotionType.DoubleSlide;
        [SerializeField] private bool startLocked = false;
        [SerializeField] private bool autoClose = true;
        [SerializeField] private float autoCloseDelay = 3.5f;
        [SerializeField] private float transitionDuration = 1.2f;
        [SerializeField] private AnimationCurve motionCurve = AnimationCurve.EaseInOut(0, 0, 1, 1);

        [Header("Door Transforms")]
        [Tooltip("Primary moving door or left sliding leaf")]
        [SerializeField] private Transform primaryDoorLeaf;
        [Tooltip("Secondary moving door (for double sliding doors, e.g. Right leaf)")]
        [SerializeField, ShowIf("IsDoubleDoor")] private Transform secondaryDoorLeaf;

        [Header("Motion Parameters")]
        [Tooltip("Slide travel distance (meters) along local X")]
        [SerializeField, HideIf("IsSwingDoor")] private float slideDistance = 1.4f;
        [Tooltip("Swing angle around local Y axis in degrees")]
        [SerializeField, ShowIf("IsSwingDoor")] private float swingAngle = 90.0f;

        [Header("Proximity Sensor")]
        [SerializeField] private bool useProximitySensor = true;
        [SerializeField] private float sensorRadius = 4.0f;
        [SerializeField] private LayerMask detectionMask = ~0;

        [Header("Status Indicators (Optional)")]
        [SerializeField] private Renderer statusBeaconRenderer;
        [SerializeField] private Color unlockedColor = new Color(0.95f, 0.72f, 0.29f); // Brass Gold
        [SerializeField] private Color lockedColor = new Color(0.85f, 0.2f, 0.15f);

        [Header("Runtime State")]
        [SerializeField, ReadOnly] private DoorState currentState = DoorState.Closed;

        private Vector3 _primaryClosedPos;
        private Quaternion _primaryClosedRot;
        private Vector3 _secondaryClosedPos;
        private Quaternion _secondaryClosedRot;

        private Coroutine _motionCoroutine;
        private Coroutine _autoCloseCoroutine;
        private float _currentOpenRatio = 0f;

        private bool IsDoubleDoor => motionType == DoorMotionType.DoubleSlide;
        private bool IsSwingDoor => motionType == DoorMotionType.HingeSwing;

        public DoorState State => currentState;
        public bool IsLocked => currentState == DoorState.Locked;
        public bool IsOpen => currentState == DoorState.Open;

        private void Awake()
        {
            InitializeTransforms();
        }

        private void Start()
        {
            if (startLocked)
            {
                Lock();
            }
            else
            {
                ApplyStateImmediate(0f);
                currentState = DoorState.Closed;
            }
            UpdateStatusIndicator();
        }

        private void InitializeTransforms()
        {
            // Auto-locate door leaves if unassigned based on naming conventions from Blender models
            if (primaryDoorLeaf == null)
            {
                var lLeaf = transform.Find("Hatchery_Door_L") ?? transform.Find("AutoGate_Door_L") ?? transform.Find("Door_TicketPavilion") ?? transform.Find("Canteen_StaffDoor");
                if (lLeaf != null) primaryDoorLeaf = lLeaf;
            }

            if (secondaryDoorLeaf == null && motionType == DoorMotionType.DoubleSlide)
            {
                var rLeaf = transform.Find("Hatchery_Door_R") ?? transform.Find("AutoGate_Door_R");
                if (rLeaf != null) secondaryDoorLeaf = rLeaf;
            }

            if (primaryDoorLeaf != null)
            {
                _primaryClosedPos = primaryDoorLeaf.localPosition;
                _primaryClosedRot = primaryDoorLeaf.localRotation;
            }

            if (secondaryDoorLeaf != null)
            {
                _secondaryClosedPos = secondaryDoorLeaf.localPosition;
                _secondaryClosedRot = secondaryDoorLeaf.localRotation;
            }
        }

        private void Update()
        {
            if (!useProximitySensor || currentState == DoorState.Locked) return;

            Collider[] hits = Physics.OverlapSphere(transform.position, sensorRadius, detectionMask);
            bool detectedTarget = false;
            foreach (var hit in hits)
            {
                if (hit.CompareTag("Player") || hit.name.Contains("Visitor") || hit.name.Contains("Dinosaur"))
                {
                    detectedTarget = true;
                    break;
                }
            }

            if (detectedTarget)
            {
                if (currentState == DoorState.Closed || currentState == DoorState.Closing)
                {
                    Open();
                }
            }
        }

        [Button("Open Door")]
        public void Open()
        {
            if (currentState == DoorState.Locked)
            {
                Debug.Log($"[{name}] Door is locked! Unlock it first.", this);
                return;
            }

            if (currentState == DoorState.Open || currentState == DoorState.Opening) return;

            if (_autoCloseCoroutine != null)
            {
                StopCoroutine(_autoCloseCoroutine);
                _autoCloseCoroutine = null;
            }

            if (_motionCoroutine != null) StopCoroutine(_motionCoroutine);
            _motionCoroutine = StartCoroutine(AnimateDoor(1f, DoorState.Opening, DoorState.Open));
        }

        [Button("Close Door")]
        public void Close()
        {
            if (currentState == DoorState.Locked || currentState == DoorState.Closed || currentState == DoorState.Closing) return;

            if (_autoCloseCoroutine != null)
            {
                StopCoroutine(_autoCloseCoroutine);
                _autoCloseCoroutine = null;
            }

            if (_motionCoroutine != null) StopCoroutine(_motionCoroutine);
            _motionCoroutine = StartCoroutine(AnimateDoor(0f, DoorState.Closing, DoorState.Closed));
        }

        [Button("Toggle Open/Close")]
        public void Toggle()
        {
            if (currentState == DoorState.Open) Close();
            else if (currentState == DoorState.Closed) Open();
        }

        [Button("Unlock Door")]
        public void Unlock()
        {
            if (currentState != DoorState.Locked) return;
            currentState = DoorState.Closed;
            UpdateStatusIndicator();
            Debug.Log($"[{name}] Door unlocked.", this);
        }

        [Button("Lock Door")]
        public void Lock()
        {
            if (currentState == DoorState.Open || currentState == DoorState.Opening)
            {
                Close();
            }
            currentState = DoorState.Locked;
            UpdateStatusIndicator();
            Debug.Log($"[{name}] Door locked.", this);
        }

        private IEnumerator AnimateDoor(float targetRatio, DoorState activeState, DoorState finalState)
        {
            currentState = activeState;
            float startRatio = _currentOpenRatio;
            float elapsed = 0f;

            while (elapsed < transitionDuration)
            {
                elapsed += Time.deltaTime;
                float t = Mathf.Clamp01(elapsed / transitionDuration);
                float curvedT = motionCurve.Evaluate(t);
                _currentOpenRatio = Mathf.Lerp(startRatio, targetRatio, curvedT);
                ApplyStateImmediate(_currentOpenRatio);
                yield return null;
            }

            _currentOpenRatio = targetRatio;
            ApplyStateImmediate(_currentOpenRatio);
            currentState = finalState;

            if (currentState == DoorState.Open && autoClose)
            {
                _autoCloseCoroutine = StartCoroutine(AutoCloseRoutine());
            }
        }

        private IEnumerator AutoCloseRoutine()
        {
            yield return new WaitForSeconds(autoCloseDelay);
            Close();
        }

        private void ApplyStateImmediate(float ratio)
        {
            switch (motionType)
            {
                case DoorMotionType.DoubleSlide:
                    if (primaryDoorLeaf != null)
                    {
                        // Left leaf slides in -X
                        primaryDoorLeaf.localPosition = _primaryClosedPos + Vector3.left * (slideDistance * ratio);
                    }
                    if (secondaryDoorLeaf != null)
                    {
                        // Right leaf slides in +X
                        secondaryDoorLeaf.localPosition = _secondaryClosedPos + Vector3.right * (slideDistance * ratio);
                    }
                    break;

                case DoorMotionType.SingleSlide:
                    if (primaryDoorLeaf != null)
                    {
                        primaryDoorLeaf.localPosition = _primaryClosedPos + Vector3.left * (slideDistance * ratio);
                    }
                    break;

                case DoorMotionType.HingeSwing:
                    if (primaryDoorLeaf != null)
                    {
                        primaryDoorLeaf.localRotation = _primaryClosedRot * Quaternion.Euler(0, swingAngle * ratio, 0);
                    }
                    break;
            }
        }

        private void UpdateStatusIndicator()
        {
            if (statusBeaconRenderer != null && statusBeaconRenderer.material != null)
            {
                Color targetCol = IsLocked ? lockedColor : unlockedColor;
                statusBeaconRenderer.material.color = targetCol;
                if (statusBeaconRenderer.material.HasProperty("_EmissionColor"))
                {
                    statusBeaconRenderer.material.SetColor("_EmissionColor", targetCol * 1.5f);
                }
            }
        }

        private void OnDrawGizmosSelected()
        {
            if (useProximitySensor)
            {
                Gizmos.color = IsLocked ? new Color(1, 0, 0, 0.3f) : new Color(0.2f, 0.8f, 1f, 0.3f);
                Gizmos.DrawWireSphere(transform.position, sensorRadius);
            }
        }
    }
}
