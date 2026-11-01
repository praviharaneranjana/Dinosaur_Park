using System.Collections.Generic;
using UnityEngine;

namespace MiniGame
{
    public enum VisitorRole
    {
        DeckExplorer,   // Walks path -> climbs deck -> watches dinos -> descends -> walks fence
        FenceObserver,  // Strolls along the enclosure fence, stops and peers through cables
        PlazaStroller   // Walks along the visitor road and plaza
    }

    /// <summary>
    /// Autonomous Spectator/Visitor AI with dynamic crowd routines:
    /// - Walking forward along the paved road/path towards the elevated viewpoint.
    /// - Climbing stairs, admiring the dinosaurs from the observation deck railing.
    /// - Strolling around the perimeter cage/fence, stopping to watch dinosaurs.
    /// - Randomized stylish clothes (shirts, pants, shoes, skin) and hairstyles!
    /// </summary>
    public class VisitorAI : MonoBehaviour
    {
        [Header("Visitor Configuration")]
        [SerializeField] private VisitorRole role = VisitorRole.DeckExplorer;
        [SerializeField] private float walkSpeed = 1.4f;
        [SerializeField] private float turnSpeed = 120f;

        private Vector3 currentDestination;
        private int routineStep = 0;
        private float pauseTimer = 0f;
        private bool isPaused = false;
        private Animator anim;

        // Key park locations
        private Vector3 entrancePos = new Vector3(0f, 0f, -42f);
        private Vector3 stairsBottomPos = new Vector3(0f, 0f, -17f);
        private Vector3 stairsTopPos = new Vector3(0f, 4.5f, -9f);
        private Vector3 deckRailingPos;
        private Vector3 fenceViewPos;

        private void Start()
        {
            anim = GetComponent<Animator>();

            // Randomize deck viewing slot along railing (X from -7 to 7, Z = -5.7)
            deckRailingPos = new Vector3(Random.Range(-7f, 7f), 4.5f, -5.7f);

            // Randomize perimeter fence viewing slot (outside fence: Z = -1.5, X = -25 to 25)
            float fx = Random.Range(-26f, 26f);
            if (Mathf.Abs(fx) < 8f) fx = fx > 0 ? 12f : -12f; // don't block center gate
            fenceViewPos = new Vector3(fx, 0f, -1.8f);

            // Randomize starting routine offset
            routineStep = Random.Range(0, 3);
            SetNextDestination();
        }

        private void Update()
        {
            float dt = Time.deltaTime;

            if (isPaused)
            {
                pauseTimer -= dt;
                if (pauseTimer <= 0f)
                {
                    isPaused = false;
                    routineStep++;
                    SetNextDestination();
                }
                return;
            }

            // Move towards current waypoint
            Vector3 target = currentDestination;
            Vector3 diff = target - transform.position;
            diff.y = 0;

            if (diff.sqrMagnitude > 0.15f)
            {
                Quaternion look = Quaternion.LookRotation(diff.normalized);
                transform.rotation = Quaternion.RotateTowards(transform.rotation, look, turnSpeed * dt);
                transform.position += transform.forward * (walkSpeed * dt);

                if (anim != null) anim.SetFloat("Speed", 1.0f);
            }
            else
            {
                // Reached waypoint!
                OnReachedDestination();
            }
        }

        private void OnReachedDestination()
        {
            switch (role)
            {
                case VisitorRole.DeckExplorer:
                    if (routineStep == 2)
                    {
                        // On observation deck railing looking at dinosaurs!
                        transform.rotation = Quaternion.Euler(0, Random.Range(-15f, 15f), 0); // face paddock
                        isPaused = true;
                        pauseTimer = Random.Range(10f, 22f); // stay and admire
                        if (anim != null) anim.SetFloat("Speed", 0f);
                        return;
                    }
                    else if (routineStep == 5)
                    {
                        // Looking through fence
                        transform.rotation = Quaternion.Euler(0, 0f, 0); // face paddock
                        isPaused = true;
                        pauseTimer = Random.Range(8f, 16f);
                        if (anim != null) anim.SetFloat("Speed", 0f);
                        return;
                    }
                    break;

                case VisitorRole.FenceObserver:
                    if (routineStep == 1 || routineStep == 3)
                    {
                        // Stopped at fence peering in
                        transform.rotation = Quaternion.Euler(0, 0f, 0);
                        isPaused = true;
                        pauseTimer = Random.Range(7f, 15f);
                        if (anim != null) anim.SetFloat("Speed", 0f);
                        return;
                    }
                    break;
            }

            routineStep++;
            SetNextDestination();
        }

        private void SetNextDestination()
        {
            if (role == VisitorRole.DeckExplorer)
            {
                int maxSteps = 6;
                routineStep = routineStep % maxSteps;

                switch (routineStep)
                {
                    case 0: // Start at entrance path
                        currentDestination = entrancePos + new Vector3(Random.Range(-1.5f, 1.5f), 0, Random.Range(-5f, 5f));
                        break;
                    case 1: // Walk forward to bottom of observation deck stairs
                        currentDestination = stairsBottomPos + new Vector3(Random.Range(-1f, 1f), 0, 0);
                        break;
                    case 2: // Climb stairs and walk to front railing
                        currentDestination = deckRailingPos;
                        break;
                    case 3: // Walk to top of stairs to descend
                        currentDestination = stairsTopPos;
                        break;
                    case 4: // Bottom of stairs on ground
                        currentDestination = stairsBottomPos;
                        break;
                    case 5: // Walk along cage fence
                        currentDestination = fenceViewPos;
                        break;
                }
            }
            else // FenceObserver
            {
                int maxSteps = 4;
                routineStep = routineStep % maxSteps;

                switch (routineStep)
                {
                    case 0:
                        currentDestination = new Vector3(-24f + Random.Range(-3f, 3f), 0f, -2f);
                        break;
                    case 1:
                        currentDestination = new Vector3(-10f + Random.Range(-2f, 2f), 0f, -2f);
                        break;
                    case 2:
                        currentDestination = new Vector3(10f + Random.Range(-2f, 2f), 0f, -2f);
                        break;
                    case 3:
                        currentDestination = new Vector3(24f + Random.Range(-3f, 3f), 0f, -2f);
                        break;
                }
            }
        }
    }
}
