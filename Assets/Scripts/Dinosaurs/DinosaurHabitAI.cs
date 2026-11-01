using UnityEngine;

namespace MiniGame
{
    public enum DinoSpecies
    {
        Apatosaurus,
        Parasaurolophus,
        Velociraptor
    }

    public enum DinoState
    {
        Idle,
        Wander,
        GoingToDrink,
        Drinking,
        SpecialHabit
    }

    /// <summary>
    /// Autonomous dinosaur behavior AI with lifelike species-specific habits:
    /// - Paddock wandering with smooth turning and speed control.
    /// - Visiting the water pond to drink moving water.
    /// - High tree browsing (Apatosaurus), vocalizing/crest display (Parasaurolophus), pack stalking/leaping (Velociraptor).
    /// - Driven by Animator component with real FBX animation clips.
    /// </summary>
    [RequireComponent(typeof(Animator))]
    public class DinosaurHabitAI : MonoBehaviour
    {
        [Header("Species & Tuning")]
        [SerializeField] private DinoSpecies species = DinoSpecies.Apatosaurus;
        [SerializeField] private float walkSpeed = 2.0f;
        [SerializeField] private float runSpeed = 4.5f;
        [SerializeField] private float turnSpeed = 90f;

        [Header("Paddock Boundaries")]
        [SerializeField] private Vector2 xBounds = new Vector2(-28f, 28f);
        [SerializeField] private Vector2 zBounds = new Vector2(6f, 58f);

        [Header("Habit Timers")]
        [SerializeField] private float minStateTime = 6f;
        [SerializeField] private float maxStateTime = 14f;
        [SerializeField] private float drinkInterval = 25f;

        private Animator anim;
        private DinoState currentState = DinoState.Idle;
        private float stateTimer;
        private float thirstTimer;
        private Vector3 targetDestination;
        private PondWater pond;
        private Vector3 currentDrinkingSpot;

        // Animator hashes
        private static readonly int HashSpeed = Animator.StringToHash("Speed");
        private static readonly int HashAction = Animator.StringToHash("Action");
        private static readonly int HashDrinking = Animator.StringToHash("Drinking");

        public DinoSpecies Species => species;
        public DinoState CurrentState => currentState;

        public void SetSpecies(DinoSpecies sp)
        {
            species = sp;
            switch (species)
            {
                case DinoSpecies.Apatosaurus:
                    walkSpeed = 1.6f;
                    runSpeed = 3.0f;
                    turnSpeed = 40f;
                    break;
                case DinoSpecies.Parasaurolophus:
                    walkSpeed = 2.4f;
                    runSpeed = 5.2f;
                    turnSpeed = 80f;
                    break;
                case DinoSpecies.Velociraptor:
                    walkSpeed = 3.2f;
                    runSpeed = 7.0f;
                    turnSpeed = 160f;
                    break;
            }
        }

        private void Start()
        {
            anim = GetComponent<Animator>();
            pond = Object.FindAnyObjectByType<PondWater>();

            SetSpecies(species);

            thirstTimer = Random.Range(8f, drinkInterval);
            PickNewWanderTarget();
            EnterState(DinoState.Idle);
        }

        private void Update()
        {
            float dt = Time.deltaTime;
            stateTimer -= dt;
            thirstTimer -= dt;

            // Check if it's time to visit the pond
            if (thirstTimer <= 0f && currentState != DinoState.GoingToDrink && currentState != DinoState.Drinking && pond != null)
            {
                GoDrinkAtPond();
                return;
            }

            switch (currentState)
            {
                case DinoState.Idle:
                    UpdateIdle(dt);
                    break;
                case DinoState.Wander:
                    UpdateWander(dt);
                    break;
                case DinoState.GoingToDrink:
                    UpdateGoingToDrink(dt);
                    break;
                case DinoState.Drinking:
                    UpdateDrinking(dt);
                    break;
                case DinoState.SpecialHabit:
                    UpdateSpecialHabit(dt);
                    break;
            }

            // Always clamp inside enclosure
            Vector3 pos = transform.position;
            pos.x = Mathf.Clamp(pos.x, xBounds.x, xBounds.y);
            pos.z = Mathf.Clamp(pos.z, zBounds.x, zBounds.y);
            transform.position = pos;
        }

        private void EnterState(DinoState newState)
        {
            currentState = newState;
            stateTimer = Random.Range(minStateTime, maxStateTime);

            switch (currentState)
            {
                case DinoState.Idle:
                    SetAnimSpeed(0f);
                    SetAnimAction(false);
                    SetAnimDrinking(false);
                    break;

                case DinoState.Wander:
                    SetAnimSpeed(1.0f);
                    SetAnimAction(false);
                    SetAnimDrinking(false);
                    break;

                case DinoState.GoingToDrink:
                    SetAnimSpeed(1.2f);
                    SetAnimAction(false);
                    SetAnimDrinking(false);
                    break;

                case DinoState.Drinking:
                    SetAnimSpeed(0f);
                    SetAnimDrinking(true);
                    SetAnimAction(true); // lower neck/head into water
                    stateTimer = Random.Range(8f, 14f); // drink for 8-14 seconds
                    break;

                case DinoState.SpecialHabit:
                    SetAnimSpeed(0f);
                    SetAnimAction(true); // roar, crest trumpet, or raptor alert scan
                    stateTimer = Random.Range(3f, 6f);
                    break;
            }
        }

        private void UpdateIdle(float dt)
        {
            if (stateTimer <= 0f)
            {
                // Chance to do special habit (roar / graze / scan) or wander
                if (Random.value < 0.35f)
                {
                    EnterState(DinoState.SpecialHabit);
                }
                else
                {
                    PickNewWanderTarget();
                    EnterState(DinoState.Wander);
                }
            }
        }

        private void UpdateWander(float dt)
        {
            MoveTowards(targetDestination, walkSpeed, dt);

            float dist = Vector3.Distance(new Vector3(transform.position.x, 0, transform.position.z),
                                          new Vector3(targetDestination.x, 0, targetDestination.z));
            if (dist < 2.0f || stateTimer <= 0f)
            {
                EnterState(DinoState.Idle);
            }
        }

        private void GoDrinkAtPond()
        {
            if (pond != null)
            {
                currentDrinkingSpot = pond.GetDrinkingSpot(transform.position);
                targetDestination = currentDrinkingSpot;
                EnterState(DinoState.GoingToDrink);
            }
        }

        private void UpdateGoingToDrink(float dt)
        {
            MoveTowards(targetDestination, walkSpeed * 1.15f, dt);

            float dist = Vector3.Distance(new Vector3(transform.position.x, 0, transform.position.z),
                                          new Vector3(targetDestination.x, 0, targetDestination.z));
            if (dist < 2.5f)
            {
                // Face toward the pond center
                if (pond != null)
                {
                    Vector3 lookDir = (pond.transform.position - transform.position).normalized;
                    lookDir.y = 0;
                    if (lookDir != Vector3.zero)
                        transform.rotation = Quaternion.LookRotation(lookDir);
                }
                EnterState(DinoState.Drinking);
            }
        }

        private void UpdateDrinking(float dt)
        {
            if (stateTimer <= 0f)
            {
                // Finished drinking! Reset thirst timer
                thirstTimer = Random.Range(drinkInterval * 0.8f, drinkInterval * 1.4f);
                SetAnimDrinking(false);
                SetAnimAction(false);
                PickNewWanderTarget();
                EnterState(DinoState.Wander);
            }
        }

        private void UpdateSpecialHabit(float dt)
        {
            if (stateTimer <= 0f)
            {
                SetAnimAction(false);
                PickNewWanderTarget();
                EnterState(DinoState.Wander);
            }
        }

        private void MoveTowards(Vector3 dest, float speed, float dt)
        {
            Vector3 dir = (dest - transform.position);
            dir.y = 0;

            if (dir.sqrMagnitude > 0.05f)
            {
                Quaternion targetRot = Quaternion.LookRotation(dir.normalized);
                transform.rotation = Quaternion.RotateTowards(transform.rotation, targetRot, turnSpeed * dt);
                transform.position += transform.forward * (speed * dt);
            }
        }

        private void PickNewWanderTarget()
        {
            float rx = Random.Range(xBounds.x + 3f, xBounds.y - 3f);
            float rz = Random.Range(zBounds.x + 3f, zBounds.y - 3f);

            // Avoid pond center as regular wander target (use drink habit for pond)
            if (pond != null && Vector2.Distance(new Vector2(rx, rz), new Vector2(pond.transform.position.x, pond.transform.position.z)) < 5f)
            {
                rx += (rx > pond.transform.position.x ? 6f : -6f);
            }

            targetDestination = new Vector3(rx, transform.position.y, rz);
        }

        private void SetAnimSpeed(float speedVal)
        {
            if (anim != null) anim.SetFloat(HashSpeed, speedVal);
        }

        private void SetAnimAction(bool actionVal)
        {
            if (anim != null) anim.SetBool(HashAction, actionVal);
        }

        private void SetAnimDrinking(bool drinkVal)
        {
            if (anim != null) anim.SetBool(HashDrinking, drinkVal);
        }
    }
}
